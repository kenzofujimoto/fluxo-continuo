#!/usr/bin/env python3
"""What must be requested, and from whom, before more pareceres can be written.

Writes syllabi/pendencias-documentais.json:
* brazil  — per Mackenzie course, each matrix row in exactly one category (current ementa linked,
            confirm currency of an official but undated/historical text, confirm an internal inconsistency,
            request the ementa, or component governed by specific rules), with the coordination e-mail.
* foreign — per eligible university, crossings blocked by an insufficient indexed catalogue, registered or
            concept candidates whose individual syllabus is missing, and anomalies recorded in pareceres.
* coi     — pending institutional confirmations from docs/coi/regras.json.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from semantic_triage import row_kind  # noqa: E402

LABELS = {
    "vigente_vinculada": "Ementa oficial vigente vinculada",
    "confirmar_inconsistencia": "Confirmar inconsistência no documento oficial",
    "confirmar_vigencia": "Ementa oficial localizada, vigência não confirmada (sem ano impresso ou edição histórica)",
    "solicitar_ementa": "Solicitar ementa/plano de ensino vigente à coordenação",
    "regra_especifica": "Componente com regra própria (TCC, estágio, optativa livre)",
}


def brazil_requests(courses: list[dict], programs: dict, contacts: dict) -> dict:
    out = {}
    for c in courses:
        rows = []
        for r in c["rows"]:
            code = r.get("id") or r["name"]
            p = programs.get(f"{c['id']}|{code}", {})
            if row_kind(r["name"]) != "disciplina":
                cat = "regra_especifica"
            elif p.get("status") != "lido":
                cat = "solicitar_ementa"
            elif p.get("anomalies"):
                cat = "confirmar_inconsistencia"
            elif not p.get("current"):
                cat = "confirmar_vigencia"
            else:
                cat = "vigente_vinculada"
            rows.append({"code": r.get("id"), "name": r["name"], "stage": r.get("semester"), "category": cat,
                         "label": LABELS[cat], "source": p.get("source"), "documentYear": p.get("documentYear"),
                         "detail": "; ".join(p.get("anomalies") or []) or p.get("currencyNote")})
        out[c["id"]] = {"contact": contacts.get(c["id"]), "rows": rows,
                        "counts": dict(collections.Counter(x["category"] for x in rows))}
    return out


def _load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def main() -> int:
    data = _load("data.json")
    programs = _load("syllabi/programas.json")["brazil"]
    records = {(r["universityId"], r["foreignCode"]): r for r in _load("syllabi/records.json")["foreign"]}
    vpath = ROOT / "syllabi" / "fontes-verificadas.json"
    if vpath.exists():
        for v in json.loads(vpath.read_text(encoding="utf-8")).get("foreign", []):
            if v.get("individualSyllabus"):
                records[(v["universityId"], v["code"])] = {"status": "ementa_individual", "document": v["source"]}
    tri = _load("syllabi/triagem-semantica.json")
    pidx = _load("syllabi/pareceres-index.json")["pareceres"]
    coi = _load("docs/coi/regras.json")
    unis = data["universities"]
    fname = {(f["universityId"], f["code"]): f["name"] for f in data["foreignCourses"]}

    br = brazil_requests(data["courses"], programs, data.get("contacts", {}))

    per = collections.defaultdict(lambda: {"insufficientCatalogue": 0, "missingSyllabi": {}, "anomalies": []})
    for cid, ri, ui, state, sem, _note in tri["crossings"]:
        u = unis[ui]["id"]
        if state == "catalogo_insuficiente":
            per[u]["insufficientCatalogue"] += 1
        for code, *_rest in sem:
            if records.get((u, code), {}).get("status") != "ementa_individual":
                per[u]["missingSyllabi"].setdefault(code, {"code": code, "name": fname.get((u, code)), "reason": "candidata por conceitos",
                                                           "source": records.get((u, code), {}).get("catalogueUrl")})
    for m in data["matches"]:
        if records.get((m["universityId"], m["foreignCode"]), {}).get("status") != "ementa_individual":
            per[m["universityId"]]["missingSyllabi"].setdefault(m["foreignCode"], {"code": m["foreignCode"], "name": fname.get((m["universityId"], m["foreignCode"])),
                                                                                   "reason": "candidata registrada", "source": m.get("source")})
    for p in pidx:
        if (p.get("secondReview") or {}).get("required"):
            f = p["foreign"][0]
            per[f["universityId"]]["anomalies"].append({"parecer": p["id"], "reason": p["secondReview"].get("reason")})
    foreign = []
    for i, u in enumerate(unis):
        if not any(u.get("courses", {}).values()):
            continue
        x = per.get(u["id"], {"insufficientCatalogue": 0, "missingSyllabi": {}, "anomalies": []})
        foreign.append({"universityId": u["id"], "name": u["name"], "country": u["country"], "catalogUrl": u.get("catalogUrl"),
                        "insufficientCatalogueCrossings": x["insufficientCatalogue"],
                        "missingSyllabi": sorted(x["missingSyllabi"].values(), key=lambda y: (y["reason"], str(y["name"]))),
                        "parecerAnomalies": x["anomalies"]})
    foreign.sort(key=lambda y: -(y["insufficientCatalogueCrossings"] + len(y["missingSyllabi"])))
    meta = {"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "brazilCounts": {k: v["counts"] for k, v in br.items()},
            "foreignUniversities": len(foreign),
            "foreignMissingSyllabi": sum(len(f["missingSyllabi"]) for f in foreign),
            "insufficientCatalogueCrossings": sum(f["insufficientCatalogueCrossings"] for f in foreign),
            "note": "Pendência documental não é incompatibilidade. Tentativas malsucedidas não provam inexistência do documento."}
    out = {"meta": meta, "labels": LABELS, "brazil": br, "foreign": foreign, "coi": coi["meta"]["pending"]}
    (ROOT / "syllabi" / "pendencias-documentais.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("requests:", meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
