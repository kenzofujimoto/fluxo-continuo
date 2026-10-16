#!/usr/bin/env python3
"""Research-only crosswalk of candidate evidence; never emits academic equivalence claims."""
from __future__ import annotations
import collections
import datetime as dt
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"syllabi"
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def key(c,code): return str(c)+"|"+str(code)
def run():
    data=load("data.json")
    evid=load("syllabi/records.json")
    triage=load("triagem.json")
    extra=load("candidatos-catalogo.json")
    foreign={key(x["universityId"],x["foreignCode"]):x for x in evid["foreign"]}
    mack={(x["courseId"],str(x["code"] or x["name"]).casefold()):x for x in evid["mackenzie"]}
    names={u["id"]:u["name"] for u in data["universities"]}
    courses={c["id"]:c for c in data["courses"]}
    # Registered manual/preliminary candidates. Explicitly track whether both sources exist.
    rows=[]
    counter=collections.Counter()
    for m in data["matches"]:
        cid, uid=m["courseId"],m["universityId"]
        mk=str(m.get("mackCode") or m.get("mackName") or "")
        br=mack.get((cid,mk.casefold()))
        # Data sometimes stores a code and display name that differ from the matrix row.
        if br is None:
            cr=courses[cid]
            r=next((x for x in cr["rows"] if x.get("id")==mk or x.get("name","").casefold()==str(m.get("mackName","")).casefold()),None)
            if r:
                br=mack.get((cid,str(r.get("id") or r["name"]).casefold()))
        fr=foreign.get(key(uid,m["foreignCode"]))
        docs=bool(fr and fr.get("status")=="ementa_individual")
        brdata=bool(br and br.get("hasAbstractInData"))
        brhours=br.get("hoursInData") if br else None
        frhours=fr.get("contactHours") if fr else None
        tags_br=set(br.get("topicTags") or []) if br else set()
        tags_fr=set(fr.get("topicTags") or []) if fr else set()
        shared=sorted(tags_br & tags_fr) if docs and brdata else []
        missing=sorted(tags_br-tags_fr) if docs and brdata else []
        if docs and brdata:
            phase="topicos_preliminares_disponiveis"
        elif docs:
            phase="falta_ementa_brasileira_validada"
        else:
            phase="falta_ementa_estrangeira_individual"
        if frhours is None or brhours is None:
            hours="horas_incompletas"
        else:
            hours="bases_horarias_a_confirmar" # Brazilian CH basis vs foreign contact CH NOT established
        counter[phase]+=1
        rows.append({"courseId":cid,"universityId":uid,"university":names.get(uid),"mackCode":mk,
                     "foreignCode":m["foreignCode"],"candidateStatus":m.get("status"),"phase":phase,
                     "mackAbstractInDatabase":brdata,"foreignIndividualSyllabus":docs,"foreignSyllabusUrl":fr.get("document") if fr else None,
                     "foreignYear":fr.get("academicYear") if fr else None,
                     "foreignContactHours":frhours,"mackHoursListed":brhours,"hourComparison":hours,
                     "sharedTopicSignals":shared,"mackTopicSignalsNotFound":missing,
                     "topicComparisonCaveat":"Controlled keyword evidence only; not coverage percentage and not final academic equivalence."})
    # All 6856 eligible subject/university cells keep a visible independent documentary state.
    by_university=collections.defaultdict(list)
    for f in evid["foreign"]:
        by_university[f["universityId"]].append(f)
    matrix=[]
    matrix_counts=collections.Counter()
    for c,ri,ui,*_ in triage["pairs"]:
        u=data["universities"][ui]
        candidates=by_university.get(u["id"],[])
        documented=sum(x["status"]=="ementa_individual" for x in candidates)
        withhours=sum(x["status"]=="ementa_individual" and x["contactHours"] is not None for x in candidates)
        state="instituicao_com_ementas" if documented else "sem_ementa_individual_recuperada"
        matrix_counts[state]+=1
        matrix.append([c,ri,ui,documented,withhours])
    meta={"generated":dt.datetime.now(dt.timezone.utc).isoformat(),"registeredCandidates":len(rows),
          "crossings":len(matrix),"candidatePhases":dict(counter),"matrixStates":dict(matrix_counts),
          "hoursPolicy":"BR CH basis and foreign contact hours are not assumed comparable.",
          "decisionsApproved":0,"note":"No final compatibility or incompatibility conclusions; institutional review required."}
    (DIR/"comparacoes.json").write_text(json.dumps({"meta":meta,"registered":rows,"matrixCoverage":matrix},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    source_counts=collections.Counter(f["status"] for f in evid["foreign"])
    hours_count=sum(1 for f in evid["foreign"] if f["status"]=="ementa_individual" and f.get("contactHours") is not None)
    topic_count=sum(1 for f in evid["foreign"] if f["status"]=="ementa_individual" and len(f.get("topicTags") or [])>=2)
    metrics={"generated":meta["generated"],"cataloguedForeign":len(evid["foreign"]),
             "mackCourses":len(evid["mackenzie"]),"foreignIndividualDocuments":source_counts.get("ementa_individual",0),
             "individualWithExtractedContactHours":hours_count,"individualWithAtLeastTwoTopicSignals":topic_count,
             "sourceStatuses":dict(source_counts),"registeredCandidates":len(rows),
             "candidatesWithPreliminaryTopicSignals":counter.get("topicos_preliminares_disponiveis",0),
             "institutionalApprovals":0,"crossings":len(matrix),"scope":"Evidence, NOT academic equivalence"}
    (DIR/"metrics.json").write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Comparisons inventory:",meta,flush=True)
if __name__=="__main__":run()
