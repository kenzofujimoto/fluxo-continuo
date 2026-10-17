#!/usr/bin/env python3
"""Find and verify individual official programmes for candidate foreign courses still lacking one.

For every foreign course that is a registered or concept-based candidate without an individual syllabus,
build candidate URLs (provider rules, the catalogue source itself, or a link found on the catalogue/listing
page by its anchor text), fetch them and accept a URL only when the page:
  * identifies the course (normalised title near the top, or the exact code);
  * contains a content section ("Contenidos", "Conteúdos", "Programma", "Contents", "İçerik", ...);
  * is not a listing (at most 3 other course titles of the same university appear).
Accepted sources go to syllabi/fontes-verificadas.json; every attempt (HTTP status, reason) goes to
syllabi/tentativas-coleta.json. A failed attempt is never evidence that a programme does not exist.

Run: python scripts/resolve_syllabi.py [--limit N] [--university ID]
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
from urllib.parse import urljoin, urlparse

import fitz
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
VERIFIED = ROOT / "syllabi" / "fontes-verificadas.json"
ATTEMPTS = ROOT / "syllabi" / "tentativas-coleta.json"
UA = "FluxoContinuoResearch/1.1 (academic source audit; https://github.com/kenzofujimoto/fluxo-continuo)"
NOW = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

CONTENT_MARKERS = re.compile(
    r"\b(?:temario|contenidos?|conte[uú]dos?\s*(?:program[aá]tico)?|programa (?:de la asignatura|da unidade|do curso|detallado)|"
    r"programma(?: del corso| dell'insegnamento)?|contenuti|course contents?|contents of the course|syllabus|course outline|"
    r"learning outcomes|ders i[cç]eri[gğ]i|i[cç]erik|haftal[ıi]k|weekly (?:topics|schedule)|continguts|unidades tem[aá]ticas|"
    r"resultados de aprendi[sz]a(?:je|gem))\b", re.I)


def fold(s: str) -> str:
    t = unicodedata.normalize("NFD", str(s or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def academic_year(text: str) -> str | None:
    m = re.search(r"\b(20\d\d)\s*[/-]\s*(20\d\d|\d\d)\b", text or "")
    if not m:
        return None
    a, b = m.group(1), m.group(2)
    b = b if len(b) == 4 else a[:2] + b
    return f"{a}/{b}" if int(b) - int(a) == 1 else None


def verify_programme(text: str, title: str, code: str, other_titles: list[str]) -> dict:
    # Explicit academic metadata overrides a coincidentally matching course title.
    declared_code = re.search(r"\bC[oó]digo(?:\s+(?:de la asignatura|da disciplina))?\s*:?\s*(\d{4,})\b", text[:6000], re.I)
    if str(code).isdigit() and declared_code and declared_code.group(1) != str(code):
        return {"ok": False, "reason": "código acadêmico declarado difere da disciplina solicitada"}
    head = fold(text[:6000])
    t = fold(title)
    ident = []
    if len(t) >= 5 and t in head:
        ident.append("title")
    if code and not str(code).startswith("CAT-") and len(str(code)) >= 4 and fold(code) in fold(text[:8000]):
        ident.append("code")
    if not ident:
        return {"ok": False, "reason": "disciplina não identificada no topo da página"}
    if ident == ["code"]:
        # A code alone is not enough: the name printed next to it must be this course (catalogues reuse codes).
        near = fold(text[:8000])
        pos = near.find(fold(code))
        window = set(near[pos:pos + 160].split()) - {fold(code)}
        want = {w for w in t.split() if len(w) > 2}
        if not want or len(want & window) / len(want) < 0.5:
            return {"ok": False, "reason": "código aponta para outra disciplina (título junto ao código não confere)"}
    others = {fold(o) for o in other_titles if fold(o) and fold(o) != t and len(fold(o)) >= 6}
    full = fold(text)
    found = sum(1 for o in others if o in full)
    if found > 3:
        return {"ok": False, "reason": f"página de listagem ({found} outras disciplinas citadas)"}
    m = CONTENT_MARKERS.search(text)
    if not m or len(text) < 800:
        return {"ok": False, "reason": "seção de conteúdos não encontrada"}
    return {"ok": True, "identifiedBy": ident, "contentMarker": m.group(0)[:40], "otherTitlesFound": found}


def find_course_link(html: str, base: str, title: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    t = fold(title)
    best = None
    for a in soup.find_all("a", href=True):
        txt = fold(a.get_text(" ", strip=True))
        if not txt:
            continue
        if txt == t or (len(t) >= 8 and txt.startswith(t) and len(txt) - len(t) <= 12 and not re.match(r"^\s*i+\b", txt[len(t):].strip())):
            url = urljoin(base, a["href"])
            if urlparse(url).scheme in ("http", "https"):
                if txt == t:
                    return url
                best = best or url
    return best


# Provider rules for URLs that can be built from the official code.
def candidate_urls(university_id: str, code: str, source: str | None) -> list[str]:
    host = (urlparse(source or "").hostname or "").lower()
    if university_id == "es-cadiz" and re.fullmatch(r"\d{8}", str(code)):
        return [f"https://asignaturas.uca.es/2026-27/{code}", f"https://asignaturas.uca.es/2025-26/{code}"]
    if host == "guias.usal.es" and "/node/" in (source or ""):
        return [source]
    if host.endswith("ucp.pt") and "/unidade-curricular/" in (source or ""):
        return [source]
    if host == "drive.google.com" and "id=" in (source or ""):
        return [source]
    return [source] if source else []


def fetch_text(url: str) -> tuple[dict, str]:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=(10, 30), allow_redirects=True, stream=True)
        info = {"http": r.status_code, "finalUrl": r.url}
        if r.status_code >= 400:
            r.close()
            return info, ""
        # Hard deadline and size cap: slow-trickle servers must not stall the whole batch.
        start, chunks, size = time.monotonic(), [], 0
        for part in r.iter_content(65536):
            chunks.append(part)
            size += len(part)
            if size > 15_000_000 or time.monotonic() - start > 60:
                r.close()
                return {**info, "error": "download excedeu 60 s ou 15 MB"}, ""
        raw = b"".join(chunks)
        if "drive.google.com" in r.url and raw[:5] != b"%PDF" and b"confirm=" in raw:
            m = re.search(rb'confirm=([0-9A-Za-z_-]+)', raw)
            if m:
                r = requests.get(url + "&confirm=" + m.group(1).decode(), headers={"User-Agent": UA}, timeout=(10, 40))
                raw = r.content
        info["sha256"] = hashlib.sha256(raw).hexdigest()
        if raw[:5] == b"%PDF":
            pdf = fitz.open(stream=raw, filetype="pdf")
            info["format"], info["pages"] = "pdf", len(pdf)
            return info, "\n".join(p.get_text() for p in pdf)[:200000]
        soup = BeautifulSoup(raw, "html.parser")
        for t in soup(["script", "style", "noscript"]):
            t.decompose()
        info["format"] = "html"
        info["_html"] = str(soup)[:600000]
        # Page title and main headings first: site menus often push the course title far down the text.
        heading = " ".join(x.get_text(" ", strip=True) for x in soup.find_all(["title", "h1", "h2"])[:4])
        for t in soup(["nav", "header", "footer", "aside"]):
            t.decompose()
        return info, re.sub(r"\s+", " ", heading + " " + soup.get_text(" ", strip=True))
    except Exception as e:  # recorded as an attempt, never as absence
        return {"http": None, "error": f"{type(e).__name__}: {str(e)[:120]}"}, ""


def _load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def targets(only_uni: str | None) -> list[dict]:
    data = _load("data.json")
    rec = {(r["universityId"], r["foreignCode"]): r for r in _load("syllabi/records.json")["foreign"]}
    verified = {(x["universityId"], x["code"]) for x in (_load("syllabi/fontes-verificadas.json")["foreign"] if VERIFIED.exists() else [])}
    req = _load("syllabi/pendencias-documentais.json")
    fc = {(f["universityId"], f["code"]): f for f in data["foreignCourses"]}
    out = []
    for u in req["foreign"]:
        if only_uni and u["universityId"] != only_uni:
            continue
        titles = [f["name"] for (uid, _), f in fc.items() if uid == u["universityId"]]
        for x in u["missingSyllabi"]:
            key = (u["universityId"], x["code"])
            if key in verified or rec.get(key, {}).get("status") == "ementa_individual":
                continue
            f = fc.get(key, {})
            out.append({"universityId": key[0], "code": key[1], "name": f.get("name") or x.get("name"),
                        "source": f.get("source"), "titles": titles, "reason": x.get("reason")})
    return out


def resolve(t: dict, listing_cache: dict) -> dict:
    tried = []
    urls = candidate_urls(t["universityId"], t["code"], t["source"])
    for url in urls:
        info, text = fetch_text(url)
        v = verify_programme(text, t["name"], t["code"], t["titles"]) if text else {"ok": False, "reason": f"HTTP {info.get('http')} {info.get('error', '')}".strip()}
        tried.append({"url": url, "http": info.get("http"), "result": v.get("reason") or "verificado"})
        if v["ok"]:
            return {"ok": True, "url": info.get("finalUrl") or url, "info": info, "verify": v, "text": text, "tried": tried}
        # The catalogue page may be a listing: look for the course's own link on it.
        html = info.get("_html")
        if html and url == t["source"]:
            link = find_course_link(html, info.get("finalUrl") or url, t["name"])
            if link and link not in urls:
                info2, text2 = fetch_text(link)
                v2 = verify_programme(text2, t["name"], t["code"], t["titles"]) if text2 else {"ok": False, "reason": f"HTTP {info2.get('http')}"}
                tried.append({"url": link, "http": info2.get("http"), "result": v2.get("reason") or "verificado", "foundOn": url})
                if v2["ok"]:
                    return {"ok": True, "url": info2.get("finalUrl") or link, "info": info2, "verify": v2, "text": text2, "tried": tried}
    return {"ok": False, "tried": tried}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--university", default=None)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    todo = targets(a.university)
    if a.limit:
        todo = todo[:a.limit]
    verified = _load("syllabi/fontes-verificadas.json") if VERIFIED.exists() else {"meta": {}, "foreign": [], "brazil": []}
    attempts = _load("syllabi/tentativas-coleta.json") if ATTEMPTS.exists() else {"meta": {}, "attempts": []}
    att_idx = {(x["universityId"], x["code"]): x for x in attempts["attempts"]}
    ok = done = 0
    with ThreadPoolExecutor(max_workers=max(1, min(a.workers, 8))) as pool:
        futs = {pool.submit(resolve, t, {}): t for t in todo}
        for f in as_completed(futs):
            t = futs[f]
            r = f.result()
            att_idx[(t["universityId"], t["code"])] = {"universityId": t["universityId"], "code": t["code"], "name": t["name"],
                                                         "checkedAt": NOW, "verified": r["ok"], "tried": r["tried"]}
            if r["ok"]:
                ok += 1
                verified["foreign"] = [x for x in verified["foreign"] if (x["universityId"], x["code"]) != (t["universityId"], t["code"])]
                verified["foreign"].append({"universityId": t["universityId"], "code": t["code"], "name": t["name"], "source": r["url"],
                                            "individualSyllabus": True, "academicYear": academic_year(r["text"][:3000]),
                                            "sha256": r["info"].get("sha256"), "format": r["info"].get("format"),
                                            "identifiedBy": r["verify"]["identifiedBy"], "contentMarker": r["verify"]["contentMarker"],
                                            "checkedAt": NOW, "method": "resolve_syllabi.py: identidade + seção de conteúdos + não listagem"})
            done += 1
            if done % 50 == 0:  # checkpoint: partial progress survives interruptions
                save(verified, attempts, att_idx)
                print(f"{done}/{len(todo)} checked, {ok} verified", flush=True)
    save(verified, attempts, att_idx)
    print(f"resolved {ok}/{len(todo)}; verified total {len(verified['foreign'])}; records synced {sync_records()}", flush=True)
    return 0


def sync_records() -> int:
    """Mirror verified programmes into records.json so every report uses one definition of 'individual'."""
    rec_path = ROOT / "syllabi" / "records.json"
    rec = json.loads(rec_path.read_text(encoding="utf-8"))
    ver = {(v["universityId"], v["code"]): v for v in (_load("syllabi/fontes-verificadas.json")["foreign"] if VERIFIED.exists() else []) if v.get("individualSyllabus")}
    changed = 0
    for r in rec["foreign"]:
        v = ver.get((r["universityId"], r["foreignCode"]))
        if v and r.get("status") != "ementa_individual":
            r.update({"status": "ementa_individual", "document": v["source"], "source": v["source"], "academicYear": v.get("academicYear"),
                      "reason": "Programa individual verificado (" + v.get("method", "verificação") + ")", "verifiedAt": v.get("checkedAt")})
            changed += 1
    counts = {}
    for r in rec["foreign"]:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    rec["meta"]["statusCounts"] = counts
    rec["meta"]["foreignCourses"] = len(rec["foreign"])
    rec_path.write_text(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return changed


def save(verified: dict, attempts: dict, att_idx: dict) -> None:
    verified["foreign"].sort(key=lambda x: (x["universityId"], x["code"]))
    verified["meta"] = {"updated": NOW, "foreign": len(verified["foreign"]),
                        "policy": "Somente programas individuais oficiais verificados por identidade da disciplina e seção de conteúdos."}
    attempts["attempts"] = sorted(att_idx.values(), key=lambda x: (x["universityId"], x["code"]))
    attempts["meta"] = {"updated": NOW, "attempted": len(attempts["attempts"]), "verified": sum(x["verified"] for x in attempts["attempts"]),
                        "note": "Tentativa sem verificação não prova inexistência do programa; muitas fontes exigem login, anexos ou navegação dinâmica."}
    VERIFIED.write_text(json.dumps(verified, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    ATTEMPTS.write_text(json.dumps(attempts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
