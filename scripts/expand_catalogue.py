#!/usr/bin/env python3
"""Expand the indexed foreign catalogue with official per-course pages, one provider at a time.

Each provider enumerates official course pages (never guessing URLs), parses only explicit fields and
returns entries that are appended to data.json `foreignCourses` (existing entries are never changed or
removed). Pages that pass resolve_syllabi.verify_programme are also registered in
syllabi/fontes-verificadas.json as individual programmes. Provenance is kept in
syllabi/catalogo-ampliado.json.

Run: python scripts/expand_catalogue.py leeds [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resolve_syllabi import verify_programme  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 FluxoContinuoResearch/1.1 (academic source audit; https://github.com/kenzofujimoto/fluxo-continuo)"}
NOW = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _num(s):
    try:
        v = float(str(s).replace(",", "."))
        return int(v) if v.is_integer() else v
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ Leeds

def parse_leeds_module(text: str, code: str) -> dict:
    t = re.sub(r"\s+", " ", text)
    m = re.search(re.escape(code) + r"\s+(.*?)\s+(\d+)\s+Credits", t)
    year = re.search(r"Year running (\d{4})/(\d{2})", t)
    delivery = [[d, _num(h)] for d, n, l, h in re.findall(r"((?:On-line Learning|Lecture|Seminar|Practical|Tutorial|Workshop|Lab(?:oratory)?|Class|Supervision|Fieldwork|Independent online learning hours|Discussion forum)[\w -]*?)\s+(\d+)\s+([\d.]+)\s+([\d.]+)", t)]
    syl = re.search(r"Syllabus\s+(.*?)\s+Teaching Methods", t)
    syl_txt = syl.group(1) if syl else ""
    return {
        "code": code,
        "name": m.group(1).strip() if m else None,
        "credits": _num(m.group(2)) if m else None,
        "creditUnit": "UK credits",
        "period": (re.search(r"Taught:\s*(.*?)\s*View Timetable", t) or re.search(r"Taught:\s*(.{5,40}?\))", t) or [None, None])[1],
        "academicYear": f"{year.group(1)}/{int(year.group(1)) + 1}" if year else None,
        "contactHours": _num((re.search(r"Total Contact hours\s+([\d.]+)", t) or [None, None])[1]),
        "selfStudy": _num((re.search(r"Private study hours\s+([\d.]+)", t) or [None, None])[1]),
        "totalHours": _num((re.search(r"Total hours \(100hr per 10 credits\)\s+([\d.]+)", t) or [None, None])[1]),
        "delivery": delivery,
        "syllabusPublished": bool(syl_txt) and not re.search(r"provided on the Minerva|will be provided", syl_txt, re.I),
    }


def leeds(session: requests.Session) -> list[dict]:
    base = "https://catalogue.leeds.ac.uk"
    subjects = [("COMP", "COMP", "cc"), ("LAW", "LAW", "dir"), ("LUBS", "LUBS", "adm")]
    out = []
    for school, subj, area in subjects:
        lists = {}
        for sa in ("False", "True"):
            r = session.get(f"{base}/ModuleSearch/results/UG/202627/{school}/{subj}/False/ALL/{sa}?keyMatch=any", timeout=60)
            lists[sa] = sorted(set(re.findall(r"/Module/UG/([A-Z]{3,4})/(\d{4})/202627", r.text)))
        abroad = {a + b for a, b in lists["True"]}

        def one(pair):
            code = pair[0] + pair[1]
            url = f"{base}/Module/UG/{pair[0]}/{pair[1]}/202627"
            r = session.get(url, timeout=60)
            if r.status_code != 200:
                return None
            soup = BeautifulSoup(r.text, "html.parser")
            for x in soup(["script", "style", "nav", "header", "footer"]):
                x.decompose()
            text = soup.get_text(" ", strip=True)
            m = parse_leeds_module(text, code)
            if not m["name"]:
                return None
            m.update({"universityId": "gb-leeds", "source": url, "area": area, "degree": "Graduação (UG)",
                      "studyAbroadListed": code in abroad, "sha256": hashlib.sha256(r.content).hexdigest(), "_text": text})
            return m
        with ThreadPoolExecutor(max_workers=6) as pool:
            out += [x for x in pool.map(one, lists["False"]) if x]
    return out


# ------------------------------------------------------------------ Salamanca (guias.usal.es)

def parse_usal_guide(text: str) -> dict:
    t = re.sub(r"\s+", " ", text)
    g = lambda p: (re.search(p, t) or [None, None])[1]  # noqa: E731
    year = re.search(r"Curso (\d{4})/(\d{4})", t)
    return {"code": g(r"C[oó]digo (\d{4,7})"), "ects": float(g(r"ECTS (\d+(?:[.,]\d+)?)").replace(",", ".")) if g(r"ECTS (\d+(?:[.,]\d+)?)") else None,
            "character": g(r"Car[aá]cter ([A-ZÁÉÍÓÚÑ ]+?) Curso"), "year": int(g(r"Car[aá]cter [A-ZÁÉÍÓÚÑ ]+? Curso (\d)")) if g(r"Car[aá]cter [A-ZÁÉÍÓÚÑ ]+? Curso (\d)") else None,
            "period": g(r"Periodicidad (.+?) Idioma"), "language": g(r"Idioma ([A-ZÁÉÍÓÚÑ/ ,]+?) (?:Área|Departamento)"),
            "academicYear": f"{year.group(1)}/{year.group(2)}" if year else None}


USAL_DEGREES = [("235383", "dir", "Grado en Derecho (Plan 223)"), ("237741", "adm", "Grado en Administración y Dirección de Empresas (238)"),
                ("254942", "cc", "Grado en Ingeniería Informática (211)"), ("250678", "si", "Grado en Ingeniería Informática en Sistemas de Información (259)")]


def usal(session: requests.Session) -> list[dict]:
    base = "https://guias.usal.es"
    out = []
    for node, area, degree in USAL_DEGREES:
        r = session.get(f"{base}/node/{node}", timeout=60)
        soup = BeautifulSoup(r.text, "html.parser")
        seen = {}
        for a in soup.find_all("a", href=True):
            m = re.fullmatch(r"(?:https://guias\.usal\.es)?/node/(\d+)", a["href"])
            name = re.sub(r"\s*\[Grupo:.*?\]\s*$", "", a.get_text(" ", strip=True)).strip()
            if m and name and name.upper() == name and m.group(1) != node and name not in seen:
                seen[name] = m.group(1)  # first group's guide; groups share the programme

        def one(item):
            name, nid = item
            url = f"{base}/node/{nid}"
            x = session.get(url, timeout=60)
            if x.status_code != 200:
                return None
            sp = BeautifulSoup(x.text, "html.parser")
            for y in sp(["script", "style", "nav", "header", "footer"]):
                y.decompose()
            text = sp.get_text(" ", strip=True)
            g = parse_usal_guide(text)
            return {"universityId": "es-salamanca", "code": g["code"] or f"USAL-node-{nid}", "name": name.title() if name.isupper() else name,
                    "source": url, "area": area, "degree": degree, "credits": g["ects"], "creditUnit": "ECTS", "period": g["period"],
                    "academicYear": g["academicYear"], "contactHours": None, "language": g["language"], "character": g["character"],
                    "sha256": hashlib.sha256(x.content).hexdigest(), "_text": text}
        with ThreadPoolExecutor(max_workers=6) as pool:
            out += [e for e in pool.map(one, seen.items()) if e]
    return out


PROVIDERS = {"leeds": leeds, "usal": usal}


# ------------------------------------------------------------------ merge

def _fold(s: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFD", str(s or "").lower())
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in t if unicodedata.category(c) != "Mn")).strip()


def merge_courses(existing: list[dict], new: list[dict]) -> tuple[list[dict], int]:
    """Append only courses not yet indexed (same code, or same name at the same university)."""
    keys = {(c["universityId"], c["code"]) for c in existing}
    names = {(c["universityId"], _fold(c["name"])) for c in existing}
    merged = list(existing)
    added = 0
    for c in new:
        k, n = (c["universityId"], c["code"]), (c["universityId"], _fold(c["name"]))
        if k not in keys and n not in names:
            merged.append(c)
            keys.add(k)
            names.add(n)
            added += 1
    return merged, added


def _load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def _dump(p, obj, indent=None):
    """Write JSON keeping the file's existing layout (compact vs indented, trailing newline or not)."""
    path = ROOT / p
    newline = path.read_text(encoding="utf-8").endswith("\n") if path.exists() else True
    body = json.dumps(obj, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))
    path.write_text(body + ("\n" if newline else ""), encoding="utf-8")


def apply(entries: list[dict], provider: str) -> dict:
    data = _load("data.json")
    titles = {}
    for f in data["foreignCourses"]:
        titles.setdefault(f["universityId"], []).append(f["name"])
    # A course already indexed under another code (e.g. internal CAT-*) keeps that code everywhere;
    # the official code is recorded as officialCode.
    existing_by_name = {(f["universityId"], _fold(f["name"])): f["code"] for f in data["foreignCourses"]}
    for e in entries:
        known = existing_by_name.get((e["universityId"], _fold(e["name"])))
        if known and known != e["code"]:
            e["officialCode"], e["code"] = e["code"], known
    new_courses, verified = [], []
    for e in entries:
        notes = []
        if e.get("studyAbroadListed"):
            notes.append("listado pelo catálogo como disponível a estudantes de intercâmbio (study abroad)")
        if e.get("syllabusPublished") is False:
            notes.append("seção 'Syllabus' remete ao ambiente virtual; conteúdo detalhado não publicado na ficha")
        new_courses.append({"universityId": e["universityId"], "code": e["code"], "name": e["name"], "source": e["source"],
                            "period": e.get("period"), "degree": e.get("degree"), "contactHours": e.get("contactHours"),
                            "credits": str(e["credits"]) if e.get("credits") is not None else None, "creditUnit": e.get("creditUnit"),
                            "documentation": "FICHA INDIVIDUAL OFICIAL (catálogo ampliado)", "academicYear": e.get("academicYear"),
                            "limitations": "; ".join(notes) or None, "origin": f"catalogo-ampliado:{provider}:{NOW[:10]}"})
        others = titles.get(e["universityId"], []) + [x["name"] for x in entries if x["universityId"] == e["universityId"] and x is not e]
        v = verify_programme(e["_text"], e["name"], e["code"], others)
        if v["ok"]:
            verified.append({"universityId": e["universityId"], "code": e["code"], "name": e["name"], "source": e["source"],
                             "individualSyllabus": True, "academicYear": e.get("academicYear"), "sha256": e.get("sha256"),
                             "format": "html", "identifiedBy": v["identifiedBy"], "contentMarker": v["contentMarker"],
                             "checkedAt": NOW, "method": f"expand_catalogue.py:{provider} + verify_programme"})
    merged, added = merge_courses(data["foreignCourses"], new_courses)
    data["foreignCourses"] = merged
    # data.json is stored compact (single line); keep that format to keep diffs reviewable.
    (ROOT / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    # records.json mirrors data.json foreignCourses; new entries start as individual or catalogue pages.
    rec = _load("syllabi/records.json")
    have = {(r["universityId"], r["foreignCode"]) for r in rec["foreign"]}
    vset = {(v["universityId"], v["code"]) for v in verified}
    in_catalogue = {(c["universityId"], c["code"]) for c in merged}
    for c in new_courses:
        k = (c["universityId"], c["code"])
        if k in have or k not in in_catalogue:  # records.json mirrors data.json exactly
            continue
        ok = k in vset
        rec["foreign"].append({"universityId": k[0], "foreignCode": k[1], "name": c["name"], "catalogueUrl": c["source"],
                               "status": "ementa_individual" if ok else "pagina_com_conteudo", "source": c["source"], "document": c["source"] if ok else None,
                               "contactHours": c.get("contactHours"), "totalHours": None, "reason": "Catálogo ampliado " + provider,
                               "topicTags": [], "academicYear": c.get("academicYear")})
    rec["meta"]["foreignCourses"] = len(rec["foreign"])
    counts = {}
    for r in rec["foreign"]:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    rec["meta"]["statusCounts"] = counts
    _dump("syllabi/records.json", rec)
    vf = _load("syllabi/fontes-verificadas.json") if (ROOT / "syllabi/fontes-verificadas.json").exists() else {"meta": {}, "foreign": []}
    known = {(x["universityId"], x["code"]) for x in vf["foreign"]}
    vf["foreign"] += [v for v in verified if (v["universityId"], v["code"]) not in known]
    vf["meta"]["foreign"] = len(vf["foreign"])
    _dump("syllabi/fontes-verificadas.json", vf, indent=1)
    tri = _load("triagem.json")
    tri["meta"]["foreignCatalogCount"] = len(merged)
    _dump("triagem.json", tri)
    prov = _load("syllabi/catalogo-ampliado.json") if (ROOT / "syllabi/catalogo-ampliado.json").exists() else {"meta": {}, "batches": []}
    prov["batches"].append({"provider": provider, "collectedAt": NOW, "entries": len(entries), "added": added,
                            "verifiedIndividual": len(verified), "courses": [{k: v for k, v in e.items() if k != "_text"} for e in entries]})
    prov["meta"] = {"updated": NOW, "policy": "Apenas páginas oficiais por disciplina; nada é removido de data.json."}
    _dump("syllabi/catalogo-ampliado.json", prov, indent=1)
    return {"entries": len(entries), "added": added, "verified": len(verified), "foreignCourses": len(merged)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("provider", choices=sorted(PROVIDERS))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    s = requests.Session()
    s.headers.update(UA)
    entries = PROVIDERS[a.provider](s)
    if a.dry_run:
        for e in entries[:10]:
            print({k: v for k, v in e.items() if k != "_text"})
        print("entries:", len(entries))
        return 0
    print(apply(entries, a.provider))
    return 0


if __name__ == "__main__":
    sys.exit(main())
