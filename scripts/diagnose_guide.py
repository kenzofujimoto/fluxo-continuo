#!/usr/bin/env python3
"""Print classification conditions for a handful of known official teaching guides."""
from collect_syllabi import get_document, extract_official_program, course_quality, clean
import json
SAMPLES=[
 ("Universidad de Salamanca","101131","Seguridad en Sistemas Informáticos","https://guias.usal.es/node/255761"),
 ("Universidad de Jaén","11911001","Administración de empresas","https://uvirtual.ujaen.es/pub/es/informacionacademica/catalogofichasdocentesasignaturas/p/2025-26/3/119A/11911001/es/2025-26-11911001_es.html"),
 ("Universidad de Cádiz","21714033","Programación Paralela y Distribuida","https://asignaturas.uca.es/2026-27/21714033"),
 ("Universitat Autònoma de Barcelona","102300","Dret Civil I","https://apps.uab.cat/guies/public/html/2026/assignatura/102300/ca")
]
def main():
 for uni,code,name,url in SAMPLES:
    doc=get_document(url)
    text=doc.get("_text","")
    program, guide=extract_official_program(text,doc.get("finalUrl"))
    evidence=course_quality({"name":name,"code":code,"source":url},doc)
    print(json.dumps({"uni":uni,"sourceCode":code,"status":evidence["status"],"fetchStatus":doc.get("status"),"final":doc.get("finalUrl"),
       "nameFound":clean(name) in clean(text[:15000]),"codeFound":code.casefold() in text[:10000].casefold(),
       "textLength":len(text),"programLength":len(program),"programWords":len(program.split()),
       "programSample":program[:180],"individualGuide":guide,"detectedHours":evidence.get("contactHours")},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
