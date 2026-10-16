#!/usr/bin/env python3
"""Prepare independently verifiable research gap report for mobile dashboards."""
import collections
import datetime as dt
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def write(path, data):
    (ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
    database=read("data.json")
    foreign=read("syllabi/records.json")["foreign"]
    br=read("syllabi/mackenzie-docs.json")["rows"]
    comparison=read("syllabi/comparacoes.json")
    manual=read("syllabi/revisoes-ementas.json")["reviews"]
    udata={u["id"]:u for u in database["universities"]}
    courses={c["id"]:c for c in database["courses"]}
    by_uni=collections.defaultdict(list)
    for f in foreign: by_uni[f["universityId"]].append(f)
    institutions=[]
    for uid,u in udata.items():
        f=by_uni[uid]
        states=collections.Counter(x["status"] for x in f)
        good=[x for x in f if x["status"]=="ementa_individual"]
        withhours=sum(x.get("contactHours") is not None for x in good)
        missing=[x for x in f if x["status"]!="ementa_individual"]
        institutions.append({
            "id":uid,"name":u["name"],"country":u.get("country"),"eligibleFor":[c for c in courses if u.get("courses",{}).get(c) is True],
            "catalogued":len(f),"individualSyllabus":len(good),"individualWithContactHours":withhours,
            "withoutIndividualSyllabus":len(missing),"withIndividualButMissingHours":len(good)-withhours,
            "statuses":dict(states),"samplePending":[{"code":x["foreignCode"],"name":x["name"],"status":x["status"],"source":x.get("source") or x.get("catalogueUrl")} for x in missing[:12]],
            "pendingForeign":[{"code":x["foreignCode"],"name":x["name"],"status":x["status"],"source":x.get("source") or x.get("catalogueUrl")} for x in missing],
            "syllabiMissingContactHours":[{"code":x["foreignCode"],"name":x["name"],"status":"ementa_sem_horas","source":x.get("document") or x.get("source")} for x in good if x.get("contactHours") is None],
            "sourceEvidenceHint":"Only course-level syllabus status has been checked, not offer or academic equivalence."
        })
    institutions.sort(key=lambda z:(-z["withoutIndividualSyllabus"],z["name"]))
    br_index={(r["courseId"],str(r.get("code") or r["name"]).casefold()):r for r in br}
    by_course=collections.Counter()
    for r in br:
        if r["status"]=="ementa_oficial_correspondente":by_course[r["courseId"]]+=1
    candidate_by_course=collections.defaultdict(list)
    for x in comparison["registered"]:candidate_by_course[x["courseId"]].append(x)
    courses_out=[]
    for cid,c in courses.items():
        items=candidate_by_course[cid]
        official=by_course[cid]
        pending=[{"code":r.get("id"),"name":r["name"],"semester":r.get("semester"),"status":br_index.get((cid,str(r.get("id") or r["name"]).casefold()),{}).get("status","ementario_oficial_atual_pendente")} for r in c["rows"] if br_index.get((cid,str(r.get("id") or r["name"]).casefold()),{}).get("status")!="ementa_oficial_correspondente"]
        phases=collections.Counter(x["phase"] for x in items)
        courses_out.append({"id":cid,"name":c["name"],"components":len(c["rows"]),"officialSyllabiMatched":official,
              "officialSyllabiPending":len(c["rows"])-official,"pendingSubjects":pending,
              "candidates":len(items),"candidatePhases":dict(phases),
              "individualReviews":sum(x["courseId"]==cid for x in manual)})
    report={"generated":dt.datetime.now(dt.timezone.utc).isoformat(),"definitions":{
       "individualSyllabus":"Automated document identity + syllabus criteria; independent human audit pending.",
       "withoutIndividualSyllabus":"A course is indexed but individual syllabus not established.",
       "withIndividualButMissingHours":"Individual syllabus found but contact hours not extracted.",
       "officialSyllabiMatched":"Mackenzie source title matched to current matrix; 2025 applicability needs confirmation.",
       "candidatePhases":"Source availability only, not equivalence verdict."
       },"metrics":{"foreignTotal":len(foreign),"foreignIndividual":sum(x["status"]=="ementa_individual" for x in foreign),
          "foreignMissingIndividual":sum(x["status"]!="ementa_individual" for x in foreign),
          "foreignIndividualMissingHours":sum(x["status"]=="ementa_individual" and x.get("contactHours") is None for x in foreign),
          "mackTotal":sum(len(c["rows"]) for c in database["courses"]),"mackVerified":sum(by_course.values()),
          "registeredCandidates":len(comparison["registered"]),"bothSyllabiCandidates":sum(x["phase"]=="topicos_preliminares_disponiveis" for x in comparison["registered"]),
          "manualReviews":len(manual),"institutionalApprovals":0},"universities":institutions,"mackenzieCourses":courses_out}
    write("syllabi/coverage-report.json",report)
    assert report["metrics"]["foreignTotal"]==2608
    assert report["metrics"]["registeredCandidates"]==725
    assert len(institutions)==66
    print("Gap report:",report["metrics"])
if __name__=="__main__":main()
