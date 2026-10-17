#!/usr/bin/env python3
"""List candidate pairs that are ready for an individual parecer and build their reading dossiers.

Ready = official Brazilian programme linked (programas.json) + individual official foreign programme
(records.json or fontes-verificadas.json) + no parecer yet. Sources of candidates: registered matches
(data.json) and concept candidates (triagem-semantica.json). Writes .cache/worklist-ready.json and
batches .cache/worklist-<prefix>N.json (default 12 pairs each, grouped by course and university).

Run: python scripts/worklist.py [--batch 12] [--prefix w]
"""
from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def ready_pairs() -> list[dict]:
    data = _load("data.json")
    prog = _load("syllabi/programas.json")
    individual = {(r["universityId"], r["foreignCode"]) for r in _load("syllabi/records.json")["foreign"] if r["status"] == "ementa_individual"}
    vp = ROOT / "syllabi" / "fontes-verificadas.json"
    if vp.exists():
        individual |= {(v["universityId"], v["code"]) for v in _load("syllabi/fontes-verificadas.json")["foreign"] if v.get("individualSyllabus")}
    done = {p["id"] for p in _load("syllabi/pareceres-index.json")["pareceres"]}
    unis = data["universities"]
    courses = {c["id"]: c for c in data["courses"]}
    out, seen = [], set()

    def add(cid, ri, uid, fcode, origin, score=None, shared=None):
        row = courses[cid]["rows"][ri]
        code = row.get("id") or row["name"]
        pid = f"{cid}|{code}|{uid}|{fcode}"
        if pid in done or pid in seen:
            return
        if prog["brazil"].get(f"{cid}|{code}", {}).get("status") != "lido" or (uid, fcode) not in individual:
            return
        if prog["foreign"].get(f"{uid}|{fcode}", {}).get("status") != "lido":
            return  # verified but not yet cached by fetch_documents.py
        seen.add(pid)
        out.append({"course": cid, "br": code, "uni": uid, "foreign": fcode, "origin": origin, "conceptScore": score, "sharedConcepts": shared})

    for m in data["matches"]:
        rows = courses[m["courseId"]]["rows"]
        ri = next((i for i, r in enumerate(rows) if m.get("mackCode") and (r.get("id") or r["name"]) == m["mackCode"]), None)
        if ri is None:
            ri = next((i for i, r in enumerate(rows) if r["name"].casefold() == str(m.get("mackName", "")).casefold()), None)
        if ri is not None:
            add(m["courseId"], ri, m["universityId"], m["foreignCode"], "candidata_registrada")
    for cid, ri, ui, state, sem, _ in _load("syllabi/triagem-semantica.json")["crossings"]:
        for code, score, shared, _doc in sem:
            add(cid, ri, unis[ui]["id"], code, "candidata_semantica", score, shared)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=12)
    ap.add_argument("--prefix", default="w")
    ap.add_argument("--dossiers", action="store_true", help="also build .cache/dossiers for every ready pair")
    a = ap.parse_args()
    pairs = ready_pairs()
    for p in pairs if a.dossiers else []:
        r = subprocess.run([sys.executable, str(ROOT / "scripts/make_dossier.py"), p["course"], p["br"], p["uni"], p["foreign"]],
                           capture_output=True, text=True, encoding="utf-8")
        p["dossier"] = r.stdout.strip()
    (ROOT / ".cache").mkdir(exist_ok=True)
    (ROOT / ".cache/worklist-ready.json").write_text(json.dumps(pairs, ensure_ascii=False, indent=1), encoding="utf-8")
    groups = collections.defaultdict(list)
    for p in sorted(pairs, key=lambda x: (x["course"], x["uni"], x["br"])):
        groups[(p["course"], p["uni"])].append(p)
    batches, cur = [], []
    for g in groups.values():
        for p in g:
            cur.append(p)
            if len(cur) >= a.batch:
                batches.append(cur)
                cur = []
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches, 1):
        (ROOT / f".cache/worklist-{a.prefix}{i}.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ready:", len(pairs), dict(collections.Counter(p["origin"] for p in pairs)), dict(collections.Counter(p["course"] for p in pairs)), "batches:", len(batches))
    return 0


if __name__ == "__main__":
    sys.exit(main())
