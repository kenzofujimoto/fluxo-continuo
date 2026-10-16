#!/usr/bin/env python3
"""Collect verifiable syllabus metadata without mislabeling catalogues as course syllabi.

Run: pip install -r scripts/requirements-audit.txt
     python scripts/collect_syllabi.py
Official PDFs remain on university servers; only short evidence metadata is versioned.
"""
from __future__ import annotations
import collections
import datetime as dt
import hashlib
import io
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "syllabi"
OUT.mkdir(exist_ok=True)
TODAY = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
UA = "FluxoContinuoResearch/1.0 (academic source audit; contact via GitHub)"
UBB = "https://www.cs.ubbcluj.ro/apps/fise/viewSyllabi.php?an=2026&lang=en&specializare=IE"
MAX_BYTES = 8 * 1024 * 1024
MAX_URLS = int(os.getenv("MAX_SOURCE_URLS", "1800"))
WORKERS = max(1, min(int(os.getenv("AUDIT_WORKERS", "4")), 6))
MARKERS = re.compile(r"syllabus|course description|course content|course outline|conteúdo programático|conteudos programaticos|ementa|programa da unidade|\bprograma\b|objetivos|resultados de aprendizagem|objectives|learning outcomes|tematica|temario|programa analítico", re.I)

def valid_url(u):
    p = urlparse(str(u or ""))
    return p.scheme == "https" and bool(p.hostname) and not (p.hostname in {"localhost", "127.0.0.1"} or p.hostname.endswith(".local"))

def normalize(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()

def clean(s):
    return re.sub(r"[^a-z0-9]+", "", str(s or "").casefold())

def get_document(url):
    if not valid_url(url):
        return {"status": "url_invalida"}
    try:
        response = requests.get(url, headers={"User-Agent": UA, "Accept": "text/html,application/pdf,*/*"}, timeout=(8, 19), stream=True, allow_redirects=True)
        response.raise_for_status()
        if not valid_url(response.url):
            return {"status": "redirecionamento_invalido"}
        parts, size = [], 0
        for part in response.iter_content(65536):
            size += len(part)
            if size > MAX_BYTES:
                return {"status": "arquivo_grande"}
            parts.append(part)
        raw = b"".join(parts)
        mime = response.headers.get("content-type", "").lower()
        if raw.startswith(b"%PDF") or "application/pdf" in mime:
            pdf = fitz.open(stream=raw, filetype="pdf")
            pages = len(pdf)
            text = normalize(" ".join(page.get_text(sort=True) for page in pdf if page.number < 75))
            kind = "pdf"
        elif "html" in mime or raw.lstrip().lower().startswith((b"<!doctype html", b"<html")):
            soup = BeautifulSoup(raw, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = normalize(soup.get_text(" ", strip=True))
            pages, kind = None, "html"
        else:
            return {"status": "formato_indisponivel", "mime": mime[:100]}
        return {"status": "lido", "type": kind, "pages": pages, "sha256": hashlib.sha256(raw).hexdigest(), "finalUrl": response.url, "_text": text[:400000]}
    except Exception as e:
        return {"status": "erro_acesso", "error": type(e).__name__ + ": " + str(e)[:100]}

# Multilingual subject-topic lexicon. Matches are retrieval hints, NOT equivalence percentages.
TOPICS = {
 "algoritmos": r"\balgoritm|\balgorithm", "estrutura_de_dados": r"data structures?|estrutur[ae]s? de dados",
 "redes": r"\bnetwork|redes? de computadores?|redes? informatic", "seguranca": r"\bsecurity|\bseguranca|\bseguranca da informac|\bcryptograph|\bcriptograf",
 "bancos_de_dados": r"\bdatabase|banco[s]? de dados|\bbasi di dati", "sql": r"\bsql\b",
 "sistemas_operacionais": r"operating systems?|sistemas? operaciona", "linux": r"\blinux\b",
 "nuvem": r"\bcloud\b|\bnuvem\b", "virtualizacao": r"\bvirtualiz|\bvirtualis",
 "concorrencia": r"\bconcurr|\bconcorr[eê]n|\bsynchroniz|\bsincroniza",
 "paralelismo": r"\bparallel|\bparalel|\bopenmp\b|\bmpi\b|\bcuda\b",
 "java": r"\bjava\b", "python": r"\bpython\b", "cpp": r"\bc\+\+\b|\bc\+\+",
 "web": r"\bweb\b|\bhttp\b|\bjavascript\b|\bhtml\b", "orientacao_objetos": r"object.oriented|orienta[cç][aã]o a objetos",
 "engenharia_software": r"software engineering|engenharia de software",
 "teste_software": r"software testing|testes? de software|test driven",
 "inteligencia_artificial": r"artificial intelligence|intelig[eê]ncia artificial|\bmachine learning\b|aprendizagem de m[aá]quina",
 "logica": r"\blogic\b|\bl[oó]gica\b", "matematica_discreta": r"discrete math|matem[aá]tica discreta",
 "estatistica": r"\bstatistic|\bestat[ií]stica|\bprobabilid|\bprobabilit",
 "calculo": r"\bcalculus\b|\bc[aá]lculo\b", "algebra": r"\balgebra\b|\b[aá]lgebra\b",
 "financas": r"\bfinance|\bfinan[cç]|\binterest rates?\b|\bjuros\b",
 "economia": r"\beconom|\bmacroeconom|\bmicroeconom",
 "administracao": r"\bmanagement\b|\bgest[aã]o\b|\badministr",
 "marketing": r"\bmarketing\b", "contabilidade": r"\baccounting\b|\bcontabil",
 "direito_constitucional": r"constitutional law|direito constitucional|derecho constitucional",
 "direito_civil": r"civil law|direito civil|derecho civil",
 "direito_penal": r"criminal law|direito penal|derecho penal",
 "direito_tributario": r"tax law|direito tribut[aá]rio|derecho tributario",
 "processo_judicial": r"procedural law|direito processual|derecho procesal",
 "etica": r"\bethic|\b[eé]tica\b",
}
def topic_tags(text):
    return sorted(k for k, pat in TOPICS.items() if re.search(pat, text or "", re.I))

def field_hours(text):
    # Parse only explicit *contact/curriculum* hours, never ECTS or individual-study totals.
    patterns = [
        r"3\.4\.\s*Total\s*(?:of)?\s*hours\s*(?:in the curriculum)?\s*:?\s*(\d{2,3})\b",
        r"3\.4\.\s*Total\s*(?:of)?\s*hours.{0,48}?\b(\d{2,3})\s*(?:of which|3\.5\.)",
        r"total\s*de\s*horas\s*presenciais\s*:?\s*(\d{2,3})\b",
        r"carga\s*horária\s*presencial\s*:?\s*(\d{2,3})\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            h = int(m.group(1))
            if 10 <= h <= 300:
                return h
    return None

def field_total(text):
    for p in [r"3\.8\.\s*Total\s*hours\s*per\s*semester\s*:?\s*(\d{2,3})",
              r"carga\s*horária\s*total\s*:?\s*(\d{2,3})"]:
        m = re.search(p, text, re.I)
        if m and 10 <= int(m.group(1)) <= 500:
            return int(m.group(1))
    return None

def ubb_links():
    try:
        r = requests.get(UBB, headers={"User-Agent": UA}, timeout=(8, 20))
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        output = {}
        for row in soup.select("tr"):
            anchor = row.find("a", href=True)
            if not anchor:
                continue
            url = urljoin(UBB, anchor["href"])
            if ".pdf" not in url.lower() or not urlparse(url).hostname.endswith("ubbcluj.ro"):
                continue
            rowtext = normalize(row.get_text(" ", strip=True))
            m = re.search(r"\b(?:MLE|MLR|MME|FEU|FAU)[A-Z0-9]{3,8}\b", rowtext)
            if not m:
                continue
            code = m.group(0)
            if code not in output:
                output[code] = {"code": code, "name": normalize(anchor.get_text(" ", strip=True)), "pdf": url, "catalogue": UBB, "academicYear": "2026/2027"}
        return output, None
    except Exception as e:
        return {}, repr(e)

def extract_official_program(text, url):
    """Require an identifiable teaching-content section before calling a public guide a syllabus."""
    host=(urlparse(str(url or "")).hostname or "").lower()
    path=(urlparse(str(url or "")).path or "").lower()
    # Provider-specific routes point to an individual teaching guide, not the course catalog.
    routes=[
        ("guias.usal.es", r"^/node/\d+$"),
        ("apps.uab.cat", r"/guies/public/html/\d{4}/assignatura/\d+"),
        ("uvirtual.ujaen.es", r"catalogofichasdocentesasignaturas/.+\.html$"),
        ("asignaturas.uca.es", r"/\d{4}-\d{2}/\d+$"),
    ]
    allowed=any(host==h and re.search(route,path) for h,route in routes)
    if not allowed:
        return "", False
    # Find curriculum text itself, not navigation bar, syllabus metadata, or ECTS alone.
    patterns=[
        r"(?:\b5\.\s*CONTENIDOS\b|\b5\.\s*Continguts\b|\bCONTINGUTS\b|\bContenidos\s+te[oó]ricos\b|\bPrograma de la asignatura\b)",
        r"\bContents\s+of\s+the\s+course\b",
    ]
    start=None
    for pat in patterns:
        m=re.search(pat,text,re.I)
        if m:
            start=m.end()
            break
    if start is None:
        return "", False
    remaining=text[start:start+38000]
    stop=re.search(r"(?:\b6\.\s*METODOLOG[IÍ]A\b|\b6\.\s*Metodolog|\bMetodologia\s+docent\b|\b7\.\s*SISTEMA\s+DE\s+EVALUACI[OÓ]N\b|\bBibliograf[ií]a\b)",remaining,re.I)
    programme=remaining[:stop.start()] if stop else remaining[:14000]
    programme=normalize(programme)
    identified=len(programme)>=160 and len(re.findall(r"\b(?:tema|bloque|unitat|unit|chapter|pr[aá]ctica|contenid|dret|sistema|programa|objectiu)\b",programme,re.I))>=2
    return programme,identified

def course_quality(foreign, document, ubb=False):
    status = document.get("status")
    base = {"status": "indisponivel", "source": foreign.get("source"), "document": None, "contactHours": None, "totalHours": None, "reason": status}
    if status != "lido":
        if status == "aguardando_coleta":
            base["status"] = "nao_tentada"
            base["reason"] = "Fonte aguardando coleta; não indica inacessibilidade"
        return base
    text = document["_text"]
    name, code = foreign.get("name", ""), foreign.get("originalCode") or foreign.get("code", "")
    by_name = len(clean(name)) >= 10 and clean(name) in clean(text[:15000])
    by_code = len(str(code)) >= 4 and str(code).casefold() in text[:10000].casefold()
    official_unit = document["type"] == "html" and "/unit/" in str(document.get("finalUrl") or "")
    section_markers = sum(bool(re.search(p, text, re.I)) for p in
        [r"programa|contents", r"learning outcomes|resultados de aprendizagem|objetivos", r"bibliograf|assessment|avalia[cç][aã]o"])
    provider_program,provider_guide=extract_official_program(text,document.get("finalUrl"))
    individual = bool(ubb or (document["type"] == "pdf" and document.get("pages") and document["pages"] <= 25) or (official_unit and section_markers >= 2) or (provider_guide and by_code))
    rich = bool(MARKERS.search(text[:13000])) and len(text) >= 650 or provider_guide
    has_identity = by_name or by_code
    q = "ementa_individual" if individual and rich and has_identity else ("pagina_com_conteudo" if has_identity and rich else "catalogo_ou_matriz")
    if q == "ementa_individual":
        hours = field_hours(text)
        total = field_total(text)
        # Universidad de Jaén publishes a clear table headed HORAS PRESENCIALES.
        # Only use the first column of the TOTALES row in that specific guide.
        finalhost=(urlparse(str(document.get("finalUrl") or "")).hostname or "").lower()
        if hours is None and finalhost=="uvirtual.ujaen.es" and "HORAS PRESENCIALES" in text.upper():
            h=re.search(r"TOTALES\s*:?\s*(\d{2,3}(?:[.,]\d{1,2})?)\s+(?:\d{1,3}(?:[.,]\d{1,2})?\s+){1,3}",text,re.I)
            if h:
                value=float(h.group(1).replace(",","."))
                if 10<=value<=300: hours=value
    else:
        hours = total = None
    base.update({"topicTags": topic_tags(provider_program if provider_guide else text[text.lower().find("8. contents"):] if "8. contents" in text.lower() else text) if q == "ementa_individual" else [],
                 "programEvidenceChars": len(provider_program) if provider_guide else None,
                 "documentClassification": "guia_oficial_programa_extraido" if provider_guide and q=="ementa_individual" else ("pdf_individual" if q=="ementa_individual" and document["type"]=="pdf" else "pagina_matriz_ou_programa_parcial"),
                 "status": q, "document": document.get("finalUrl"), "source": document.get("finalUrl"), "sha256": document.get("sha256"),
                 "format": document.get("type"), "pages": document.get("pages"), "identifiedBy": [v for v, b in (("title", by_name), ("code", by_code)) if b],
                 "contactHours": hours, "totalHours": total, "reason": "Documento identificado; requer confrontação humana de ementas e CH" if q == "ementa_individual" else "Fonte não comprova ementa individual completa"})
    return base

def main():
    data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
    foreign = data["foreignCourses"]
    courses = data["courses"]
    universities = {u["id"]: u for u in data["universities"]}
    sources = collections.Counter(f.get("source") for f in foreign if valid_url(f.get("source")))
    hosts = collections.Counter(urlparse(u).hostname for u in sources)
    ubb, ubb_error = ubb_links()
    print("foreign:", len(foreign), "unique urls:", len(sources), "ubb-index:", len(ubb), "ubb-error:", ubb_error, flush=True)
    # Verify UBB course PDFs and all unique direct programme URLs. Shared catalogue pages remain catalogues.
    url_list = []
    for f in foreign:
        u = universities.get(f["universityId"], {})
        if "babe" in str(u.get("name", "")).casefold() or "bolyai" in str(u.get("name", "")).casefold():
            if f.get("code") in ubb:
                u = ubb[f["code"]]["pdf"]
                if u not in url_list: url_list.append(u)
    for u in sources:
        if u not in url_list: url_list.append(u)
    urls = url_list[:MAX_URLS]
    rawdocs = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        future = {pool.submit(get_document, u): u for u in urls}
        for n, done in enumerate(as_completed(future), 1):
            u = future[done]
            try: rawdocs[u] = done.result()
            except Exception as e: rawdocs[u] = {"status": "erro_interno", "error": repr(e)}
            if n % 50 == 0: print(f"Fetched {n}/{len(urls)} sources", flush=True)
    results = []
    for f in foreign:
        uni = universities.get(f["universityId"], {})
        source = f.get("source")
        proof = None
        if "babe" in str(uni.get("name", "")).casefold() or "bolyai" in str(uni.get("name", "")).casefold():
            proof = ubb.get(f.get("code"))
        url = proof["pdf"] if proof else source
        doc = rawdocs.get(url, {"status": "aguardando_coleta", "reason": "Source not processed in current batch"})
        record = {"universityId": f["universityId"], "foreignCode": f["code"], "name": f.get("name"), "catalogueUrl": source}
        record.update(course_quality(f, doc, bool(proof)))
        if proof: record["academicYear"] = proof["academicYear"]
        results.append(record)
    mack = []
    for course in courses:
        for r in course["rows"]:
            mack.append({"courseId": course["id"], "code": r.get("id"), "name": r.get("name"),
                         "hasAbstractInData": bool(r.get("abstract")), "hasHoursInData": r.get("hours") is not None,
                         "source": r.get("syllabusUrl") or course.get("source"),
                         "status": "ementa_no_banco_nao_auditada" if r.get("abstract") else "ementa_nao_extraida",
                         "hoursInData": r.get("hours"), "topicTags": topic_tags(r.get("abstract", "")) if r.get("abstract") else []})
    counts = collections.Counter(item["status"] for item in results)
    catalog = {"meta": {"collectedAt": TODAY, "scope": "audit not equivalence", "universities": len(universities),
             "foreignCourses": len(foreign), "urlsUnique": len(sources), "urlsAttempted": len(urls), "unattemptedUniqueUrls": max(0, len(url_list) - len(urls)),
             "ubbIndexCourses": len(ubb), "ubbIndexError": ubb_error, "statusCounts": dict(counts), "hoursPolicy": "Never convert ECTS to contact hours; missing is null"},
             "foreign": results, "mackenzie": mack}
    (OUT / "records.json").write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    # Research backlog by institution, not false assertions of incompatibility.
    group = collections.defaultdict(list)
    for f in results:
        if f["status"] != "ementa_individual" or f["contactHours"] is None:
            group[f["universityId"]].append(f["foreignCode"])
    backlog = [{"universityId": k, "university": universities.get(k, {}).get("name"), "pendingCourseCount": len(v), "sampleCodes": v[:12]} for k,v in group.items()]
    backlog.sort(key=lambda x: -x["pendingCourseCount"])
    (OUT / "backlog.json").write_text(json.dumps({"generated": TODAY, "pending": backlog}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "source-inventory.json").write_text(json.dumps({"generated": TODAY, "hosts": hosts.most_common(), "individualSourceUrls": len(sources), "processed": len(urls), "unprocessed": max(0,len(url_list)-len(urls))}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Audit written. Status:", dict(counts), flush=True)

if __name__ == "__main__":
    main()
