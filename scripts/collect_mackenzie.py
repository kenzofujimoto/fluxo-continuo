#!/usr/bin/env python3
"""Audit Mackenzie Alphaville official 2025 syllabi; keep links and evidence metadata, not PDFs.

Do not confuse PDFs from different campuses, catalog years, CH basis or source matrices.
Extract exact-title records only; ambiguous results remain pending.
"""
from __future__ import annotations
import datetime as dt
import difflib
import hashlib
import json
import re
import unicodedata
from pathlib import Path
import requests
import fitz

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"syllabi"
CC_ROOT="https://www.mackenzie.br/fileadmin/ARQUIVOS/Public/1-mackenzie/universidade/unidades-academicas/FCI/2025/EMENTAS_-_CC__ALPHAVILLE_/"
SI_URL="https://www.mackenzie.br/fileadmin/ARQUIVOS/Public/1-mackenzie/universidade/unidades-academicas/FCI/2025/EMENTAS_-_SI__ALPHAVILLE_/Ement%C3%A1rio_SI_Alphaville__2025_.pdf"
def pdf_urls():
    return [("cc", f"{CC_ROOT}{stage}__ETAPA_-_CC_-_ALPHAVILLE.pdf",stage) for stage in range(1,9)] + [("si",SI_URL,None)]
def canonical(s):
    t=unicodedata.normalize("NFD",str(s or ""))
    t="".join(c for c in t if unicodedata.category(c)!="Mn")
    return re.sub(r"\s+"," ",re.sub(r"[^A-Z0-9]+"," ",t.upper())).strip()
def get_pdf(url):
    try:
        r=requests.get(url,timeout=(10,45),headers={"User-Agent":"FluxoContinuoResearch/1.0"},stream=True)
        r.raise_for_status()
        if "mackenzie.br" not in requests.utils.urlparse(r.url).hostname:
            return None,{"error":"redirect outside official domain"}
        raw=r.content
        if len(raw)>20_000_000 or not raw.startswith(b"%PDF"):
            return None,{"error":"not a small PDF"}
        return fitz.open(stream=raw,filetype="pdf"),{"sha256":hashlib.sha256(raw).hexdigest(),"source":r.url,"bytes":len(raw)}
    except Exception as e: return None,{"error":type(e).__name__+": "+str(e)[:130]}
def get_segments(pdf):
    # Blocks may continue across pages and a page may contain two courses.
    txt="\n".join(page.get_text(sort=True) for page in pdf)
    expr=re.compile(r"\bComp\.\s*Curricular\s*\n?\s*([A-ZÀ-ÖØ-Ý][^\n]{3,100})",re.I)
    found=list(expr.finditer(txt))
    rows=[]
    for i,m in enumerate(found):
        end=found[i+1].start() if i+1<len(found) else len(txt)
        segment=txt[m.end():end]
        title=m.group(1)
        title=re.split(r"\bC[oó]digo\b",title,flags=re.I)[0].strip()
        title=re.sub(r"\s+"," ",title)
        hm=re.search(r"Carga\s*hor[aá]ria\s*\(horas\)\s*[:\s]*([0-9]{1,3}(?:[,\.][0-9]{1,2})?)",segment,re.I)
        hours=float(hm.group(1).replace(",",".")) if hm else None
        em=re.search(r"\bEmenta\b\s*\n",segment,re.I)
        # Some PDFs have 'Ementa' same line as start of description.
        if not em: em=re.search(r"\bEmenta\b\s*",segment,re.I)
        content=""
        if em:
            remainder=segment[em.end():]
            stop=re.search(r"\bBibliografia\s+(?:b[aá]sica|complementar)\b|\bCoordenador\s+do\s+Curso\b",remainder,re.I)
            content=(remainder[:stop.start()] if stop else remainder[:1800]).strip()
            content=re.sub(r"\s+"," ",content)
        rows.append({"name":title,"contactHoursDeclared":hours,"syllabusText":content,"hasSyllabus":bool(len(content)>45),
                     "hash":hashlib.sha256(content.encode("utf-8")).hexdigest() if content else None})
    return rows
def main():
    data=json.loads((ROOT/"data.json").read_text(encoding="utf-8"))
    courses={c["id"]:c for c in data["courses"]}
    src={}
    found=[]
    for cid,url,st in pdf_urls():
        pdf,info=get_pdf(url)
        if not pdf:
            print(f"ERROR {cid} stage {st}: {info}",flush=True)
            src[url]=info
            continue
        blocks=get_segments(pdf)
        info.update({"pages":len(pdf),"recordsParsed":len(blocks),"course":cid,"stage":st})
        src[url]=info
        for row in blocks:
            row.update({"courseId":cid,"stage":st,"url":info["source"]})
        found.extend(blocks)
        print(cid,st,"pages:",len(pdf),"records:",len(blocks),"with syllabus:",sum(x["hasSyllabus"] for x in blocks),flush=True)
    audit=[]
    for cid in ("cc","si"):
        for row in courses[cid]["rows"]:
            name=canonical(row["name"])
            stage=int(row.get("semester") or 0)
            candidates=[f for f in found if f["courseId"]==cid and f["hasSyllabus"] and (f["stage"] is None or f["stage"]==stage)]
            exact=[f for f in candidates if canonical(f["name"])==name]
            if len(exact)==1:
                match=exact[0]
                strength="titulo_exato"
            elif len(exact)>1:
                match=None
                strength="duplicidade"
            else:
                scored=sorted(((difflib.SequenceMatcher(None,name,canonical(f["name"])).ratio(),f) for f in candidates),key=lambda x:-x[0])
                if scored and scored[0][0]>=0.92 and (len(scored)<2 or scored[0][0]-scored[1][0]>0.06):
                    match=scored[0][1]
                    strength="nome_proximo_requer_revisao"
                else:
                    match=None
                    strength="nao_localizada"
            verified=bool(match and strength=="titulo_exato" and match.get("contactHoursDeclared") is not None)
            audit.append({"courseId":cid,"code":row.get("id"),"name":row["name"],"stage":stage,
                 "status":"ementa_oficial_correspondente" if verified else ("pareamento_incerto" if match else "pendente"),
                 "matchMethod":strength,
                 "documentName":match["name"] if match else None,
                 "source":match["url"] if match else None,
                 "contactHoursDeclared":match["contactHoursDeclared"] if match else None,
                 "topicTags":[],
                 "shortEvidenceDigest":match["hash"] if match else None,
                 "syllabusCharacters":len(match["syllabusText"]) if match else None,
                 "note":"Ementário público 2025, câmpus Alphaville; confirmar aplicabilidade à matriz e período do aluno."})
    # Topic signals from independently read and course-identity-checked Brazilian syllabi.
    try:
        from collect_syllabi import topic_tags
        lookup={(r["courseId"],r["stage"],canonical(r["name"])):r for r in found}
        for row in audit:
            m=lookup.get((row["courseId"],row["stage"] if row["courseId"]=="cc" else None,canonical(row.get("documentName"))))
            if m and row["status"]=="ementa_oficial_correspondente":
                row["topicTags"]=topic_tags(m["syllabusText"])
    except Exception as e: print("Topic-tagging unavailable",e,flush=True)
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    meta={"generated":stamp,"campus":"Alphaville","sourceYear":2025,"officialRecordsScanned":len(found),
          "ccConfirmed":sum(r["status"]=="ementa_oficial_correspondente" for r in audit if r["courseId"]=="cc"),
          "siConfirmed":sum(r["status"]=="ementa_oficial_correspondente" for r in audit if r["courseId"]=="si"),
          "ccInMatrix":len(courses["cc"]["rows"]),"siInMatrix":len(courses["si"]["rows"]),
          "statusCounts":{k:sum(r["status"]==k for r in audit) for k in sorted({r["status"] for r in audit})},
          "scope":"Identity and source-CH extraction, not content equivalence",
          "notes":"Store provenance, signatures, CH and derived topics only; see institutional PDFs for complete ementa."}
    (OUT/"mackenzie-docs.json").write_text(json.dumps({"meta":meta,"sources":src,"rows":audit},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Mackenzie syllabus audit:",meta,flush=True)
if __name__=="__main__":main()
