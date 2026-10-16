#!/usr/bin/env python3
"""Extract official *historical* 2022 Alphaville Law syllabi; never relabel as current."""
from __future__ import annotations
import collections
import datetime as dt
import hashlib
import json
import re
import unicodedata
from pathlib import Path
import requests
import fitz

ROOT=Path(__file__).resolve().parents[1]
URL="https://www.mackenzie.br/fileadmin/ARQUIVOS/Public/5-graduacao/upm-alphaville/direito/EMENT%C3%81RIO_2022.pdf"

def norm(value):
    t=unicodedata.normalize("NFD",str(value or "").upper())
    t="".join(x for x in t if unicodedata.category(x)!="Mn")
    return " ".join(re.findall(r"[A-Z0-9]+",t))
def read():
    r=requests.get(URL,headers={"User-Agent":"FluxoContinuoResearch/1.0"},timeout=(10,60))
    r.raise_for_status()
    assert r.content.startswith(b"%PDF"),"Expected institutional PDF"
    assert len(r.content)<20_000_000,"PDF too large"
    pdf=fitz.open(stream=r.content,filetype="pdf")
    return pdf,hashlib.sha256(r.content).hexdigest()
def segments(pdf):
    found=[]
    for page_idx,page in enumerate(pdf):
        txt=page.get_text(sort=True)
        if page_idx==0:
            print("DEBUG PAGE0 PDF TEXT:",repr(txt[:1300]),flush=True)
        hits=list(re.finditer(r"Nome\s+do\s+Componente\s+Curricular\s*:?\s*\n\s*([^\n]{3,150})",txt,re.I))
        for n,m in enumerate(hits):
            title=m.group(1).strip()
            if re.match(r"C[oó]digo do Componente",title,re.I):continue
            section=txt[m.end():(hits[n+1].start() if n+1<len(hits) else len(txt))]
            em=re.search(r"\bEmenta\s*:\s*",section,re.I)
            end=re.search(r"\bBibliografia\s+b[aá]sica\b",section[em.end():],re.I) if em else None
            text=(section[em.end():][:end.start()] if end else section[em.end():][:1800]) if em else ""
            text=re.sub(r"\s+"," ",text).strip()
            stage_m=re.search(r"Etapa\s*:\s*(\d{1,2})\s*[ªaoº]",section,re.I)
            weekly=re.search(r"(?:Carga\s+hor[aá]ria\s*:\s*)(\d{1,2})\s*horas?\s+aula",section,re.I)
            if not weekly:
                weekly=re.search(r"(?:Carga\s+hor[aá]ria\s*:\s*)\n\s*(\d{1,2})\s*horas?\s+aula",section,re.I)
            if len(text)<45:continue
            found.append({"name":title,"norm":norm(title),"stage":int(stage_m.group(1)) if stage_m else None,
                "page":page_idx+1,"weeklyClassHours":int(weekly.group(1)) if weekly else None,
                "contentHash":hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "textChars":len(text),"summaryTopics":[]})
    return found

def main():
    pdf,sha=read()
    found=segments(pdf)
    data=json.loads((ROOT/"data.json").read_text(encoding="utf-8"))
    courses=next(c for c in data["courses"] if c["id"]=="dir")
    # Avoid guessing from other academic years, courses or similarly named discipline options.
    rows=[]
    matches=0
    for r in courses["rows"]:
        key=norm(r["name"])
        stage=int(r.get("semester") or 0)
        arr=[x for x in found if x["norm"]==key and x["stage"]==stage]
        alt=[x for x in found if x["norm"]==key]
        item=arr[0] if len(arr)==1 else alt[0] if len(alt)==1 and alt[0]["stage"] is None else None
        status="historical_2022_identified" if item else ("ambiguous_historical" if arr or alt else "historical_not_located")
        if item:matches+=1
        rows.append({"code":r.get("id"),"name":r["name"],"stage":stage,"status":status,
          "sourceYear":2022,"source":URL if item else None,
          "pdfPage":item["page"] if item else None,
          "weeklyClassHours":item["weeklyClassHours"] if item else None,
          "syllabusDigest":item["contentHash"] if item else None,
          "textChars":item["textChars"] if item else None,
          "validFor2027":False,
          "caveat":"2022 historical edition. Weekly class hours NOT semester contact hours. This is not a confirmed syllabus for current curriculum."})
    metrics={"generated":dt.datetime.now(dt.timezone.utc).isoformat(),"document":"Alphaville Direito official 2022 historical",
       "pdfPages":len(pdf),"sha256":sha,"extracted":len(found),
       "matchedHistorical":matches,"curriculumDisciplineCount":len(rows),
       "unmatchedCurrent":len(rows)-matches,"hourUnits":"weekly class hours, NOT total semester contact hours",
       "canProve2027Equivalence":False}
    dest=ROOT/"syllabi"/"direito-historico-2022.json"
    dest.write_text(json.dumps({"meta":metrics,"rows":rows,"rawTitles":[{"name":x["name"],"stage":x["stage"],"page":x["page"]} for x in found]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(metrics,flush=True)
if __name__=="__main__":main()
