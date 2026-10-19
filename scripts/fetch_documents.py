#!/usr/bin/env python3
"""Incremental cache of official syllabus documents plus structured field extraction.

Run:  python scripts/fetch_documents.py [--refresh] [--only-host HOST]

* Raw documents and extracted text stay in .cache/ (git-ignored): official PDFs are referenced, not republished.
* syllabi/documentos.json  -> provenance manifest (URL, final URL, HTTP status, SHA-256, ETag/Last-Modified,
                              fetch date, pages, extraction errors). Unchanged sources are not re-downloaded.
* syllabi/programas.json   -> fields read from explicit document sections (hours split, ECTS, year, level,
                              prerequisites, topic headings). Missing values stay null; ECTS never become hours.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import fitz
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from program_fields import parse_ficha_blocks, parse_mackenzie_blocks, parse_ubb, split_ementa, split_ementa_fine  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache"
RAW, TXT = CACHE / "docs", CACHE / "text"
MANIFEST = ROOT / "syllabi" / "documentos.json"
PROGRAMS = ROOT / "syllabi" / "programas.json"
UA = "FluxoContinuoResearch/1.1 (academic source audit; https://github.com/kenzofujimoto/fluxo-continuo)"
MAX_BYTES = 20 * 1024 * 1024
NOW = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_url(u: str) -> bool:
    p = urlparse(str(u or ""))
    host = (p.hostname or "").lower()
    return p.scheme in ("https", "http") and bool(host) and host not in ("localhost", "127.0.0.1") and not host.endswith(".local")


def text_path(url: str) -> Path:
    return TXT / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".txt")


def sorted_path(url: str) -> Path:
    return TXT / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".sorted.txt")


def extract_pdf_page_text(page: fitz.Page, *, sort: bool = False) -> str:
    """Recover full AcroForm values when their appearance rectangle clips the text."""
    text = page.get_text(sort=sort)
    normalized = lambda value: re.sub(r"\s+", " ", value).strip()
    for widget in page.widgets() or []:
        value = widget.field_value
        if widget.field_type != fitz.PDF_WIDGET_TYPE_TEXT or not isinstance(value, str) or not value.strip():
            continue
        if normalized(value) in normalized(text):
            continue
        visible = page.get_text(clip=widget.rect, sort=sort).strip()
        if visible and visible in text:
            text = text.replace(visible, value.strip(), 1)
        else:
            text += f"\n[PDF form field: {widget.field_name}]\n{value.strip()}\n"
    return text


def fetch(url: str, prev: dict | None, refresh: bool) -> dict:
    entry = dict(prev or {})
    entry["url"] = url
    if not safe_url(url):
        entry.update({"status": "url_invalida", "checkedAt": NOW})
        return entry
    if prev and not refresh and prev.get("status") == "lido" and text_path(url).exists():
        return entry  # incremental: unchanged cache, no network
    headers = {"User-Agent": UA, "Accept": "text/html,application/pdf,*/*"}
    if prev and prev.get("etag") and text_path(url).exists():
        headers["If-None-Match"] = prev["etag"]
    if prev and prev.get("lastModified") and text_path(url).exists():
        headers["If-Modified-Since"] = prev["lastModified"]
    try:
        r = requests.get(url, headers=headers, timeout=(10, 40), stream=True, allow_redirects=True)
        entry.update({"httpStatus": r.status_code, "checkedAt": NOW, "finalUrl": r.url})
        if r.status_code == 304:
            entry["status"] = "lido"
            return entry
        if r.status_code >= 400:
            entry.update({"status": "erro_http", "error": f"HTTP {r.status_code}"})
            return entry
        if not safe_url(r.url):
            entry.update({"status": "redirecionamento_invalido"})
            return entry
        chunks, size = [], 0
        for part in r.iter_content(65536):
            size += len(part)
            if size > MAX_BYTES:
                entry.update({"status": "arquivo_grande"})
                return entry
            chunks.append(part)
        raw = b"".join(chunks)
        mime = r.headers.get("content-type", "").lower()
        sha = hashlib.sha256(raw).hexdigest()
        if raw.startswith(b"%PDF") or "application/pdf" in mime:
            pdf = fitz.open(stream=raw, filetype="pdf")
            pages = [extract_pdf_page_text(p) for p in pdf]
            text = "\n\f\n".join(pages)
            stext = "\n".join(extract_pdf_page_text(p, sort=True) for p in pdf)
            fmt, npages = "pdf", len(pdf)
        elif "html" in mime or raw.lstrip()[:200].lower().startswith((b"<!doctype", b"<html")):
            soup = BeautifulSoup(raw, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = soup.get_text("\n", strip=True)
            stext, fmt, npages = "", "html", None
        else:
            entry.update({"status": "formato_indisponivel", "mime": mime[:80]})
            return entry
        TXT.mkdir(parents=True, exist_ok=True)
        text_path(url).write_text(text, encoding="utf-8")
        if stext:
            sorted_path(url).write_text(stext, encoding="utf-8")
        entry.update({"status": "lido", "sha256": sha, "bytes": len(raw), "format": fmt, "pages": npages,
                      "textChars": len(text), "fetchedAt": NOW, "etag": r.headers.get("ETag"),
                      "lastModified": r.headers.get("Last-Modified"), "changedSincePrevious": bool(prev and prev.get("sha256") and prev["sha256"] != sha)})
        entry.pop("error", None)
        return entry
    except Exception as e:  # network errors are recorded, never treated as proof of absence
        entry.update({"status": "erro_acesso", "error": f"{type(e).__name__}: {str(e)[:140]}", "checkedAt": NOW})
        return entry


def content_hash(url: str, entry: dict) -> str | None:
    """Version identity of a document: raw bytes for PDFs; normalised visible text for HTML pages,
    whose raw bytes change on every request (tokens, timestamps) even when the programme does not."""
    if entry.get("format") == "pdf":
        return entry.get("sha256")
    p = text_path(url)
    if not p.exists():
        return None
    text = re.sub(r"\s+", " ", p.read_text(encoding="utf-8")).strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical(s: str) -> str:
    t = unicodedata.normalize("NFD", str(s or ""))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9]+", " ", t.upper())).strip()


def page_of(url: str, needle: str) -> int | None:
    p = text_path(url)
    if not p.exists():
        return None
    pages = p.read_text(encoding="utf-8").split("\n\f\n")
    n = canonical(needle)
    for i, page in enumerate(pages, 1):
        if n and n in canonical(page):
            return i
    return None


def aliases() -> list[dict]:
    """Documented links between matrix rows and FCI 2025 blocks printed under another title or file."""
    p = ROOT / "syllabi/aliases-mackenzie.json"
    return json.loads(p.read_text(encoding="utf-8"))["aliases"] if p.exists() else []


def brazil_registry() -> list[dict]:
    p = ROOT / "syllabi/fontes-brasileiras.json"
    return json.loads(p.read_text(encoding="utf-8"))["sources"] if p.exists() else []


def match_ficha_rows(course: dict, blocks: list[dict]) -> dict:
    """Match matrix rows to ficha blocks by exact canonical title (stage must agree when both are known)."""
    found = {}
    for row in course["rows"]:
        name = canonical(row["name"])
        stage = row.get("semester")
        cand = [b for b in blocks if canonical(b["name"]) == name and (b["stage"] is None or not stage or b["stage"] == stage)]
        method = "titulo_exato"
        if not cand:
            # Documented abbreviations/articles only ('Adm.' -> 'Administração', 'para a' / 'da' / 'de').
            alias = lambda s: re.sub(r"\b(?:A|DA|DE|DO|NA|NO)\b", " ", canonical(s).replace("ADM ", "ADMINISTRACAO "))
            cand = [b for b in blocks if re.sub(r"\s+", " ", alias(b["name"])).strip() == re.sub(r"\s+", " ", alias(row["name"])).strip()
                    and (b["stage"] is None or not stage or b["stage"] == stage)]
            method = "titulo_normalizado_artigos"
        if len(cand) == 1 and len(cand[0]["ementa"]) >= 45:
            found[row.get("id") or row["name"]] = (cand[0], method)
    return found


def targets(only_host: str | None) -> tuple[list[tuple[str, dict]], list[str]]:
    rec = json.loads((ROOT / "syllabi/records.json").read_text(encoding="utf-8"))
    mack = json.loads((ROOT / "syllabi/mackenzie-docs.json").read_text(encoding="utf-8"))
    extra_p = ROOT / "syllabi/fontes-verificadas.json"
    extra = json.loads(extra_p.read_text(encoding="utf-8")) if extra_p.exists() else {"foreign": [], "brazil": []}
    foreign = [(r["document"], {"universityId": r["universityId"], "code": r["foreignCode"]})
               for r in rec["foreign"] if r["status"] == "ementa_individual" and r.get("document")]
    foreign += [(r["source"], {"universityId": r["universityId"], "code": r["code"]}) for r in extra.get("foreign", []) if r.get("source")]
    br = sorted({u for u in mack["sources"]} | {r["source"] for r in extra.get("brazil", []) if r.get("source")}
                | {r["url"] for r in brazil_registry()} | {a["source"] for a in aliases()})
    if only_host:
        foreign = [x for x in foreign if only_host in (urlparse(x[0]).hostname or "")]
        br = [u for u in br if only_host in (urlparse(u).hostname or "")]
    return foreign, br


def extract_programs(manifest: dict, foreign: list[tuple[str, dict]], br_urls: list[str]) -> dict:
    data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
    mack = json.loads((ROOT / "syllabi/mackenzie-docs.json").read_text(encoding="utf-8"))
    progs_f, progs_b = {}, {}
    for url, ident in foreign:
        m = manifest.get(url, {})
        key = ident["universityId"] + "|" + ident["code"]
        base = {"source": url, "sha256": m.get("sha256"), "contentSha256": content_hash(url, m), "fetchedAt": m.get("fetchedAt"), "status": m.get("status")}
        if m.get("status") != "lido" or not text_path(url).exists():
            progs_f[key] = base
            continue
        text = text_path(url).read_text(encoding="utf-8")
        host = urlparse(url).hostname or ""
        if host.endswith("ubbcluj.ro") and re.search(r"COURSE DESCRIPTION|SYLLABUS", text[:600], re.I):
            st = sorted_path(url).read_text(encoding="utf-8") if sorted_path(url).exists() else None
            base.update(parse_ubb(text, st))
            base["location"] = "Course description: secções 1-4 (identificação/horas), 7 (resultados), 8.1-8.2 (conteúdos)"
        else:
            base.update({"layout": "nao_estruturado", "textChars": len(text),
                         "ectsMentioned": bool(re.search(r"\bECTS\b", text)),
                         "location": "Documento integral; campos extraídos manualmente no parecer"})
        progs_f[key] = base
    # Mackenzie blocks: identify each matrix row by the title already audited in mackenzie-docs.json
    blocks_by_url = {}
    for url in br_urls:
        if manifest.get(url, {}).get("status") == "lido" and text_path(url).exists():
            txt = text_path(url).read_text(encoding="utf-8").replace("\n\f\n", "\n")
            blocks_by_url[url] = parse_mackenzie_blocks(txt)
    rows = [r for r in mack["rows"] if r["status"] == "ementa_oficial_correspondente"]
    linked = {(r["courseId"], str(r["code"] or r["name"])) for r in rows}
    stage_of = {(c["id"], r.get("id") or r["name"]): r.get("semester") for c in data["courses"] for r in c["rows"]}
    for a in aliases():
        if (a["courseId"], a["code"]) in linked:
            continue
        rows.append({"courseId": a["courseId"], "code": a["code"], "name": a["code"], "source": a["source"],
                     "documentName": a["documentName"], "stage": stage_of.get((a["courseId"], a["code"])),
                     "aliasMethod": a["method"], "aliasNote": a.get("note")})
    for row in rows:
        url = row["source"]
        cand = [b for b in blocks_by_url.get(url, []) if canonical(b["name"]) == canonical(row["documentName"])]
        if row["courseId"] == "cc":
            cand = [b for b in cand if b["stage"] == row["stage"]] or cand
        key = row["courseId"] + "|" + str(row["code"] or row["name"])
        if len(cand) != 1:
            progs_b[key] = {"source": url, "status": "bloco_nao_isolado", "candidates": len(cand)}
            continue
        b = cand[0]
        progs_b[key] = {"source": url, "sha256": manifest.get(url, {}).get("sha256"), "documentYear": 2025,
                        "campus": "Alphaville", "page": page_of(url, row["documentName"]), "stage": b["stage"],
                        "name": b["name"], "hours": b["hours"], "hourUnit": b["hourUnit"], "weekly": b["weekly"],
                        "optional": b["optional"], "ementa": b["ementa"], "topics": split_ementa(b["ementa"]),
                        "anomalies": b.get("anomalies", []) + ([f"Bloco do PDF da {row['stage']}ª etapa declara Etapa {b['stage']}"] if row["courseId"] == "cc" and b["stage"] != row["stage"] else [])
                        + ([row["aliasNote"]] if row.get("aliasMethod") == "titulo_diferente_confirmar" else []),
                        "matchMethod": row.get("aliasMethod") or "titulo_exato", "status": "lido"}
    for k, v in progs_b.items():
        if v.get("status") == "lido":
            v.update({"officialSyllabus": True, "current": True, "currencyNote": "Ementário público FCI 2025, câmpus Alphaville"})
            if v.get("matchMethod") == "titulo_diferente_confirmar":
                # Same 2025 document, but the printed title differs from the matrix: identity awaits confirmation.
                v.update({"current": False, "currencyNote": "Ementário FCI 2025 com título diferente da matriz; vínculo a confirmar com a coordenação"})
            if not (v.get("ementa") or "").strip():
                # A matched course block proves its identity, not the presence of syllabus content.
                v.update({"officialSyllabus": False, "current": False,
                          "currencyNote": "Ementário público FCI 2025 com campo Ementa vazio; conteúdo curricular ausente, plano de ensino necessário."})
    # Additional official Brazilian ementários (Administração, Direito 2022) with explicit currency flags.
    courses = {c["id"]: c for c in data["courses"]}
    by_course = {}
    for src in sorted(brazil_registry(), key=lambda item: bool(item.get("onlyMissing"))):
        url = src["url"]
        if manifest.get(url, {}).get("status") != "lido" or not text_path(url).exists():
            continue
        txt = text_path(url).read_text(encoding="utf-8")
        pages = txt.split("\n\f\n")
        course = courses[src["courseId"]]
        existing = match_ficha_rows(course, by_course.get(src["courseId"], []))
        for b in parse_ficha_blocks(txt.replace("\n\f\n", "\n")):
            identities = match_ficha_rows(course, [b])
            allowed = src.get("matchOnlyCodes")
            if allowed is not None and not any(code in allowed for code in identities):
                continue
            if src.get("onlyMissing") and (not identities or any(code in existing for code in identities)):
                continue  # Supplemental sources cannot make an existing exact match ambiguous.
            b["src"] = src
            b["page"] = next((i for i, pg in enumerate(pages, 1) if canonical(b["name"]) in canonical(pg)), None)
            by_course.setdefault(src["courseId"], []).append(b)
    for cid, blocks in by_course.items():
        for code, (b, method) in match_ficha_rows(courses[cid], blocks).items():
            key = f"{cid}|{code}"
            if key in progs_b and progs_b[key].get("current"):
                continue  # never replace a current FCI 2025 ementa by an older document
            src = b["src"]
            progs_b[key] = {"source": src["url"], "sha256": manifest.get(src["url"], {}).get("sha256"),
                            "documentYear": src.get("documentYear"), "campus": src.get("campus"), "page": b["page"],
                            "stage": b["stage"], "name": b["name"], "matchMethod": method,
                            "hours": b["hours"], "hourUnit": b["hourUnit"],
                            "weeklyClassPeriods": b["weeklyClassPeriods"], "ementa": b["ementa"],
                            # The official 'Conteúdo Programático' is the finer topic list when present.
                            "topics": b["programContent"] if len(b["programContent"]) >= 3 else split_ementa_fine(b["ementa"]),
                            "topicSource": "conteudo_programatico" if len(b["programContent"]) >= 3 else "ementa",
                            "programContent": b["programContent"],
                            "officialSyllabus": True, "current": bool(src.get("current")),
                            "currencyNote": src.get("currencyNote"), "provenance": src.get("provenance"), "status": "lido"}
    return {"meta": {"generated": NOW, "foreign": len(progs_f), "brazil": len(progs_b),
                     "brazilByCourse": {c: sum(1 for k, v in progs_b.items() if k.startswith(c + "|") and v.get("status") == "lido") for c in ("cc", "si", "adm", "dir")},
                     "brazilCurrent": sum(1 for v in progs_b.values() if v.get("current")),
                     "structuredForeign": sum(1 for v in progs_f.values() if v.get("layout") == "ubb_course_description"),
                     "policy": "Campos lidos de seções explícitas; nulos quando ausentes. ECTS nunca convertidos em horas."},
            "foreign": progs_f, "brazil": progs_b}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="revalidate cached sources with conditional requests")
    ap.add_argument("--only-host", default=None)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    manifest = {}
    if MANIFEST.exists():
        manifest = {d["url"]: d for d in json.loads(MANIFEST.read_text(encoding="utf-8"))["documents"]}
    foreign, br = targets(args.only_host)
    urls = list(dict.fromkeys([u for u, _ in foreign] + br))
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 6))) as pool:
        futs = {pool.submit(fetch, u, manifest.get(u), args.refresh): u for u in urls}
        for f in as_completed(futs):
            manifest[futs[f]] = f.result()
            done += 1
            if done % 50 == 0:
                print(f"{done}/{len(urls)}", flush=True)
    docs = sorted(manifest.values(), key=lambda d: d["url"])
    counts = {}
    for d in docs:
        counts[d.get("status")] = counts.get(d.get("status"), 0) + 1
    MANIFEST.write_text(json.dumps({"meta": {"generated": NOW, "documents": len(docs), "statusCounts": counts,
                                             "storage": "Somente metadados; documentos permanecem nas URLs institucionais."},
                                    "documents": docs}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    all_foreign, all_br = targets(None)
    programs = extract_programs(manifest, all_foreign, all_br)
    PROGRAMS.write_text(json.dumps(programs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("manifest:", counts, "programs:", programs["meta"], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
