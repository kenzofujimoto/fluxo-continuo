#!/usr/bin/env python3
"""Assemble a local reading dossier (both official texts + extracted fields) for one candidate pair.

Usage: python scripts/make_dossier.py COURSE BRCODE UNIVERSITY FOREIGNCODE [FOREIGNCODE2 ...]
Writes .cache/dossiers/<id>.md (git-ignored). The dossier is a reading aid for the reviewer who writes the
parecer; it is never published because it contains full institutional texts.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".cache" / "dossiers"


def text_of(url: str, max_chars: int = 30000) -> str:
    p = ROOT / ".cache" / "text" / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".txt")
    if not p.exists():
        return "[TEXTO NÃO DISPONÍVEL NO CACHE — rode scripts/fetch_documents.py]"
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t[:max_chars] + ("\n[...truncado...]" if len(t) > max_chars else "")


def build(course: str, brcode: str, uni: str, fcodes: list[str]) -> Path:
    data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
    progs = json.loads((ROOT / "syllabi/programas.json").read_text(encoding="utf-8"))
    rec = json.loads((ROOT / "syllabi/records.json").read_text(encoding="utf-8"))
    c = next(x for x in data["courses"] if x["id"] == course)
    row = next(r for r in c["rows"] if (r.get("id") or r["name"]) == brcode)
    u = next(x for x in data["universities"] if x["id"] == uni)
    br = progs["brazil"].get(course + "|" + brcode, {})
    parts = [f"# Dossiê {course}|{brcode}|{uni}|{'+'.join(fcodes)}", "",
             "## Mackenzie", json.dumps({"row": row, "programa": br}, ensure_ascii=False, indent=1), "",
             "## Universidade", json.dumps({k: u.get(k) for k in ("id", "name", "country", "courses", "language", "catalogUrl", "notes", "period", "semesterInfo") if k in u}, ensure_ascii=False, indent=1)]
    for fc in fcodes:
        fdata = next((f for f in data["foreignCourses"] if f["universityId"] == uni and f["code"] == fc), {})
        frec = next((r for r in rec["foreign"] if r["universityId"] == uni and r["foreignCode"] == fc), {})
        fp = progs["foreign"].get(uni + "|" + fc, {})
        parts += ["", f"## Estrangeira {fc}", "### data.json", json.dumps(fdata, ensure_ascii=False, indent=1),
                  "### records.json", json.dumps({k: frec.get(k) for k in ("status", "document", "contactHours", "totalHours", "academicYear", "sha256")}, ensure_ascii=False),
                  "### campos extraídos", json.dumps({k: v for k, v in fp.items() if k not in ("courseTopics", "labTopics")}, ensure_ascii=False, indent=1),
                  "### texto oficial (cache local)", text_of(fp.get("source") or frec.get("document") or "")]
    OUT.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{course}_{brcode}_{uni}_{'+'.join(fcodes)}")[:150] + ".md"
    path = OUT / name
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(2)
    print(build(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]))
