#!/usr/bin/env python3
"""Check cross-file evidence invariants independently from lexical recommendations."""
import collections
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_text(encoding="utf-8"))
def main():
    db=read("data.json")
    syllabi=read("syllabi/records.json")
    metrics=read("syllabi/metrics.json")
    docs=read("syllabi/mackenzie-docs.json")
    comparisons=read("syllabi/comparacoes.json")
    gaps=read("syllabi/coverage-report.json")
    reviews=read("syllabi/revisoes-ementas.json")["reviews"]
    foreign={(x["universityId"],x["foreignCode"]):x for x in syllabi["foreign"]}
    assert len(foreign)==len(db["foreignCourses"])
    br={(x["courseId"],str(x.get("code") or x["name"]).casefold()):x for x in docs["rows"]}
    assert len(br)==93
    assert len(db["courses"])==4
    for u in db["universities"]:
        assert any(x["universityId"]==u["id"] for x in syllabi["foreign"]),("No courses",u["id"])
    status=collections.Counter(x["status"] for x in syllabi["foreign"])
    assert dict(status)==metrics["sourceStatuses"],"Source audit count mismatch"
    assert metrics["foreignIndividualDocuments"]==status["ementa_individual"]
    assert metrics["officialMackenzieSyllabi"]==sum(x["status"]=="ementa_oficial_correspondente" for x in docs["rows"])
    assert gaps["metrics"]["foreignMissingIndividual"]==len(foreign)-status["ementa_individual"]
    assert gaps["metrics"]["foreignIndividualMissingHours"]==sum(x["status"]=="ementa_individual" and x.get("contactHours") is None for x in foreign.values())
    assert sum(u["catalogued"] for u in gaps["universities"])==len(db["foreignCourses"])
    assert len(gaps["universities"])==len(db["universities"])==66
    for u in gaps["universities"]:
        assert u["catalogued"]==u["individualSyllabus"]+u["withoutIndividualSyllabus"]
        assert u["individualSyllabus"]>=u["individualWithContactHours"]
        assert len(u["pendingForeign"])==u["withoutIndividualSyllabus"]
    assert len(comparisons["registered"])==len(db["matches"])==metrics["registeredCandidates"]==725
    assert len(comparisons["matrixCoverage"])==6856
    if (ROOT/"syllabi/direito-historico-2022.json").exists():
        history=read("syllabi/direito-historico-2022.json")
        assert len(history["rows"])==81
        assert all(r["validFor2027"] is False for r in history["rows"])
    for r in reviews:
        assert (r["foreignUniversityId"],r["foreignCode"]) in foreign
        f=foreign[r["foreignUniversityId"],r["foreignCode"]]
        assert f["status"]=="ementa_individual",(r["foreignCode"],"unverified foreign syllabus")
        b=br["cc",r["mackCode"].casefold()]
        assert b["status"]=="ementa_oficial_correspondente"
        assert r["courseId"]=="cc"
        assert r["hoursMackenzieDeclared"]==b["contactHoursDeclared"]
        assert r["hoursForeignContact"]==f["contactHours"]
        assert r["conclusion"] and r["justification"] and r["sharedAreas"]
    # Individual pareceres (schema v2): index matches files, no homologation without a formal decision,
    # every crossing has exactly one research state, and the request report covers every Brazilian row.
    files=sorted((ROOT/"syllabi"/"pareceres").rglob("*.json"))
    index=read("syllabi/pareceres-index.json")
    assert index["meta"]["count"]==len(files)==len(index["pareceres"]),"pareceres index out of date"
    assert index["meta"]["institutionalDecisions"]==0 or all(p.get("decisionDocument") for p in index["pareceres"] if p["institutionalStatus"]!="aguardando_validacao_institucional")
    for p in index["pareceres"]:
        assert p["conclusionClass"] in ("alta_afinidade","afinidade_parcial","baixa_afinidade","evidencia_insuficiente")
        assert p["coverage"]["essential"]>0,(p["id"],"no essential Brazilian topic assessed")
        assert p["brazil"]["source"].startswith("https://") and all(f["source"].startswith("https://") for f in p["foreign"])
    triage=read("syllabi/triagem-semantica.json")
    assert len(triage["crossings"])==6856 and len({tuple(c[:3]) for c in triage["crossings"]})==6856
    assert all("incompat" not in c[3] for c in triage["crossings"])
    requests=read("syllabi/pendencias-documentais.json")
    assert sum(len(c["rows"]) for c in requests["brazil"].values())==sum(len(c["rows"]) for c in db["courses"])==221
    print("OK: documentary provenance, hours and gaps are internally consistent")
    print("OK:",len(files),"pareceres,",len(triage["crossings"]),"crossings with a research state")
if __name__=="__main__":main()
