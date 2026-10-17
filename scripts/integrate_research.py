#!/usr/bin/env python3
"""Integrate public-research discoveries (.cache/public-research) into the authoritative base.

Nothing is copied blindly: every discovered source is fetched again and re-verified with
resolve_syllabi.verify_programme against OUR catalogue name and code (explicit-code, identity, content
and non-listing rules). Quarantined items, rejected candidates and courses absent from data.json are
skipped with a reason. Accepted programmes are appended to syllabi/fontes-verificadas.json keeping any
previous record in `history`; every decision is logged in syllabi/integracao-pesquisa-publica.json.

Run: python scripts/integrate_research.py [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resolve_syllabi import FetchCache, academic_year, sync_records, verify_programme  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / ".cache" / "public-research"
LEDGERS = {"europe": "europe.json", "americas": "americas.json", "asia": "asia-brazil.json", "solbridge": "solbridge-audited.json"}
NOW = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect_candidates(ledgers: dict, catalogue: set, already_verified: set) -> tuple[list[dict], list[dict]]:
    out, skipped, seen = [], [], set()
    for name, led in ledgers.items():
        quarantined = {q.get("code") for q in led.get("quarantined", [])}
        rejected = {(r.get("universityId"), r.get("code")) for r in led.get("rejectedCandidates", [])}
        for f in led.get("foreign", []):
            key = (f.get("universityId"), f.get("code"))
            base = {"ledger": name, "universityId": key[0], "code": key[1], "source": f.get("source")}
            if not f.get("individualSyllabus", f.get("status") == "verified"):
                continue
            if f.get("code") in quarantined:
                skipped.append({**base, "reason": "em quarentena no levantamento"})
            elif key in rejected:
                skipped.append({**base, "reason": "rejeitado na auditoria manual do levantamento"})
            elif key not in catalogue:
                skipped.append({**base, "reason": "disciplina ausente do catálogo data.json"})
            elif key in already_verified:
                skipped.append({**base, "reason": "já verificado na base"})
            elif key not in seen and f.get("source"):
                seen.add(key)
                out.append(base)
    return out, skipped


def reverify(cand: dict, catalogue_name: str, other_titles: list[str], fetch) -> dict:
    info, text = fetch(cand["source"])
    if not text:
        return {"ok": False, "reason": f"HTTP {info.get('http')} {info.get('error', '')}".strip()}
    final = info.get("finalUrl") or cand["source"]
    v = verify_programme(text, catalogue_name, cand["code"], other_titles, source_url=final)
    if not v["ok"]:
        return {"ok": False, "reason": v["reason"]}
    return {"ok": True, "entry": {
        "universityId": cand["universityId"], "code": cand["code"], "name": catalogue_name, "source": final,
        "individualSyllabus": True, "academicYear": academic_year(text[:3000]), "sha256": info.get("sha256"),
        "format": info.get("format"), "identifiedBy": v["identifiedBy"], "contentMarker": v["contentMarker"], "checkedAt": NOW,
        "method": f"Varredura pública ({cand['ledger']}) reverificada por integrate_research.py: identidade + código + conteúdo + não listagem"}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
    names = {(f["universityId"], f["code"]): f["name"] for f in data["foreignCourses"]}
    titles = {}
    for f in data["foreignCourses"]:
        titles.setdefault(f["universityId"], []).append(f["name"])
    vpath = ROOT / "syllabi" / "fontes-verificadas.json"
    verified = json.loads(vpath.read_text(encoding="utf-8"))
    already = {(v["universityId"], v["code"]) for v in verified["foreign"] if v.get("individualSyllabus")}
    rec = json.loads((ROOT / "syllabi" / "records.json").read_text(encoding="utf-8"))
    already |= {(r["universityId"], r["foreignCode"]) for r in rec["foreign"] if r["status"] == "ementa_individual"}
    ledgers = {k: json.loads((RESEARCH / v).read_text(encoding="utf-8")) for k, v in LEDGERS.items() if (RESEARCH / v).exists()}
    cands, skipped = collect_candidates(ledgers, set(names), already)
    cache = FetchCache()

    def one(c):
        key = (c["universityId"], c["code"])
        others = [t for t in titles.get(c["universityId"], []) if t != names[key]]
        return c, reverify(c, names[key], others, cache.fetch)

    with ThreadPoolExecutor(max_workers=max(1, min(a.workers, 8))) as pool:
        results = list(pool.map(one, cands))
    accepted = [r["entry"] for _, r in results if r["ok"]]
    rejected = [{**c, "reason": r["reason"]} for c, r in results if not r["ok"]]
    print(f"candidates {len(cands)}; accepted {len(accepted)}; rejected {len(rejected)}; skipped {len(skipped)}")
    if a.dry_run:
        for x in rejected[:25]:
            print("  REJ", x["universityId"], x["code"], x["reason"])
        return 0
    index = {(v["universityId"], v["code"]): v for v in verified["foreign"]}
    for e in accepted:
        prior = index.get((e["universityId"], e["code"]))
        if prior:
            e["history"] = [*prior.get("history", []), {k: v for k, v in prior.items() if k != "history"}]
        index[(e["universityId"], e["code"])] = e
    verified["foreign"] = sorted(index.values(), key=lambda x: (x["universityId"], x["code"]))
    verified["meta"] = {**verified.get("meta", {}), "updated": NOW, "foreign": len(verified["foreign"])}
    vpath.write_text(json.dumps(verified, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    log = {"meta": {"integratedAt": NOW, "ledgers": list(ledgers), "candidates": len(cands), "accepted": len(accepted),
                    "rejected": len(rejected), "skipped": len(skipped),
                    "policy": "Descobertas reverificadas uma a uma; rejeição não prova inexistência do programa."},
           "accepted": [{k: e[k] for k in ("universityId", "code", "source", "sha256", "identifiedBy")} for e in accepted],
           "rejected": rejected, "skipped": skipped}
    (ROOT / "syllabi" / "integracao-pesquisa-publica.json").write_text(json.dumps(log, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("records synced:", sync_records())
    return 0


if __name__ == "__main__":
    sys.exit(main())
