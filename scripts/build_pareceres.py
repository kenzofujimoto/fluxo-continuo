#!/usr/bin/env python3
"""Validate individual curricular opinions (pareceres) and publish an index for the site.

Each parecer lives in syllabi/pareceres/<course>/<id>.json and is written after reading BOTH official
documents. This script never writes conclusions: it recomputes coverage counts and hour comparability,
checks that the author's class is not more favourable than the documented evidence allows, rejects
homologation language, missing evidence locations and copy-pasted boilerplate, then writes
syllabi/pareceres-index.json.

The thresholds below are an internal, documented project rule inspired by the COI 75% parameter
(Manual do Intercâmbio 2024, pending confirmation). They are NOT an official Mackenzie formula.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "syllabi" / "pareceres"
INDEX = ROOT / "syllabi" / "pareceres-index.json"

CLASSES = ("alta_afinidade", "afinidade_parcial", "baixa_afinidade", "evidencia_insuficiente")
RANK = {"alta_afinidade": 3, "afinidade_parcial": 2, "baixa_afinidade": 1, "evidencia_insuficiente": 0}
TOPIC_STATUS = ("coberto", "parcial", "nao_encontrado", "nao_verificavel")
CONFIDENCE = ("alta", "moderada", "baixa")
PENDING = "aguardando_validacao_institucional"
REFERENCE_RATIO = 0.75  # COI general parameter (Manual 2024), applied only as an internal indicator
MAX_UNVERIFIABLE = 1 / 3
BOILERPLATE_JACCARD = 0.8


class ParecerError(ValueError):
    pass


# ---------------------------------------------------------------- hours

def compare_hours(br: dict, foreign: dict) -> dict:
    """Compare semester contact hours only when both quantities share a basis."""
    br = br or {}
    foreign = foreign or {}
    bv, fv = br.get("value"), foreign.get("contactTotal")
    if bv is None or br.get("basis") != "semestre" or br.get("unit") != "hora_relogio":
        return {"state": "nao_comparavel", "reason": "Carga horária brasileira semestral em horas-relógio não comprovada."}
    if fv is None or foreign.get("basis") != "semestre":
        why = "Documento estrangeiro informa apenas créditos/ECTS" if foreign.get("ects") else "Horas de contato semestrais estrangeiras não declaradas"
        if foreign.get("basis") == "semana":
            why = "Documento estrangeiro informa horas semanais, não semestrais"
        return {"state": "nao_comparavel", "reason": why + "; não se converte ECTS em horas."}
    minutes = foreign.get("hourLengthMinutes")
    if minutes:
        fclock = fv * minutes / 60
        return {"state": "comparavel", "brClockHours": bv, "foreignClockHours": round(fclock, 2),
                "diffAbs": round(fclock - bv, 2), "diffPct": round((fclock - bv) / bv * 100, 1),
                "ratio": round(fclock / bv, 4),
                "basis": f"Horas de contato semestrais; hora estrangeira de {minutes} min declarada."}
    return {"state": "comparavel_condicional", "brClockHours": bv, "foreignDeclaredHours": fv,
            "diffAbs": round(fv - bv, 2), "diffPct": round((fv - bv) / bv * 100, 1),
            "ratio": round(fv / bv, 4), "ratioIf50min": round(fv * 50 / 60 / bv, 4),
            "basis": "Horas de contato semestrais declaradas; duração da hora estrangeira não informada no documento. "
                     "Mackenzie: horas-relógio (h-a de 50 min convertidas pelo próprio ementário)."}


def _combined_foreign_hours(foreign_list: list[dict]) -> dict:
    hs = [f.get("hours") or {} for f in foreign_list]
    if len(hs) == 1:
        return hs[0]
    if all(h.get("contactTotal") is not None and h.get("basis") == "semestre" for h in hs):
        mins = {h.get("hourLengthMinutes") for h in hs}
        return {"contactTotal": sum(h["contactTotal"] for h in hs), "basis": "semestre",
                "hourLengthMinutes": mins.pop() if len(mins) == 1 else None}
    return {"contactTotal": None, "basis": None}


# ---------------------------------------------------------------- coverage

def coverage_summary(topics: list[dict]) -> dict:
    ess = [t for t in topics if t.get("essential", True)]
    c = collections.Counter(t.get("status") for t in ess)
    n = len(ess)
    return {"essential": n, "coberto": c["coberto"], "parcial": c["parcial"], "nao_encontrado": c["nao_encontrado"],
            "nao_verificavel": c["nao_verificavel"],
            "fullRatio": round(c["coberto"] / n, 4) if n else 0.0,
            "anyRatio": round((c["coberto"] + c["parcial"]) / n, 4) if n else 0.0}


def derive_class(cov: dict, hours: dict, docs_ok: bool, current_br: bool = True) -> str:
    if not docs_ok or not cov.get("essential"):
        return "evidencia_insuficiente"
    if cov["nao_verificavel"] / cov["essential"] > MAX_UNVERIFIABLE:
        return "evidencia_insuficiente"
    hours_ok = hours.get("state") in ("comparavel", "comparavel_condicional") and hours.get("ratio", 0) >= REFERENCE_RATIO
    if cov["fullRatio"] >= REFERENCE_RATIO and cov["nao_encontrado"] == 0 and hours_ok and current_br:
        return "alta_afinidade"
    if cov["anyRatio"] >= 0.5:
        return "afinidade_parcial"
    return "baixa_afinidade"


# ---------------------------------------------------------------- validation

_NEG = re.compile(r"(?:n[ãa]o|nenhum[a]?|sem|nunca|jamais|zero|inexist\w*)\b[^.;]{0,30}$", re.I)
_HOMOLOG = re.compile(r"homologad[ao]s?|aprovad[ao]s?\s+pelo\s+mackenzie|equival[eê]ncia\s+aprovada", re.I)


def _https(u) -> bool:
    p = urlparse(str(u or ""))
    return p.scheme == "https" and bool(p.hostname)


def _check_language(text: str, field: str):
    for m in _HOMOLOG.finditer(text or ""):
        before = text[max(0, m.start() - 45):m.start()]
        if not _NEG.search(before):
            raise ParecerError(f"{field}: homologation language without formal decision ('{m.group(0)}')")


def validate_parecer(p: dict, docs_ok: bool, current_br: bool = True) -> dict:
    pid = p.get("id") or "?"
    for k in ("id", "brazil", "foreign", "topics", "synthesis", "justification", "conclusionClass", "confidence",
              "confidenceRationale", "limitations", "institutionalStatus"):
        if not p.get(k):
            raise ParecerError(f"{pid}: missing field {k}")
    if p["conclusionClass"] not in CLASSES:
        raise ParecerError(f"{pid}: unknown class {p['conclusionClass']}")
    if p["confidence"] not in CONFIDENCE:
        raise ParecerError(f"{pid}: unknown confidence {p['confidence']}")
    if p["institutionalStatus"] != PENDING:
        decision = p.get("decisionDocument") or {}
        if not (p["institutionalStatus"] == "decisao_formal_registrada" and _https(decision.get("url"))):
            raise ParecerError(f"{pid}: institutionalStatus must stay '{PENDING}' without a formal decision document")
    if not _https(p["brazil"].get("source")):
        raise ParecerError(f"{pid}: Brazilian source must be an https URL")
    for f in p["foreign"]:
        if not _https(f.get("source")):
            raise ParecerError(f"{pid}: foreign source must be an https URL ({f.get('code')})")
    for i, t in enumerate(p["topics"]):
        if t.get("status") not in TOPIC_STATUS:
            raise ParecerError(f"{pid}: topic {i} has invalid status")
        if t["status"] in ("coberto", "parcial") and not (str(t.get("foreignEvidence") or "").strip() and str(t.get("foreignLocation") or "").strip()):
            raise ParecerError(f"{pid}: topic {i} lacks foreign evidence and location")
        if t["status"] == "nao_encontrado" and not str(t.get("scopeExamined") or "").strip():
            raise ParecerError(f"{pid}: topic {i} 'nao_encontrado' must state the examined evidence scope")
    for field in ("synthesis", "justification", "confidenceRationale"):
        _check_language(p.get(field, ""), field)
    cov = coverage_summary(p["topics"])
    hours = compare_hours(p["brazil"].get("hours"), _combined_foreign_hours(p["foreign"]))
    derived = derive_class(cov, hours, docs_ok, current_br)
    chosen = p["conclusionClass"]
    if RANK[chosen] > RANK[derived]:
        raise ParecerError(f"{pid}: class '{chosen}' is more favourable than evidence-derived '{derived}'")
    if RANK[chosen] < RANK[derived] and not str(p.get("downgradeReason") or "").strip():
        raise ParecerError(f"{pid}: conservative class below '{derived}' requires downgradeReason")
    out = dict(p)
    out.update({"coverage": cov, "hoursComparison": hours, "derivedClass": derived,
                "referenceRatio": REFERENCE_RATIO})
    return out


def _norm(s) -> str:
    t = unicodedata.normalize("NFD", str(s or "")).casefold()
    return re.sub(r"\s+", " ", "".join(c for c in t if unicodedata.category(c) != "Mn")).strip()


DRIFT = "DRIFT: "


def split_drift(messages: list[str]) -> tuple[list[str], list[str]]:
    """Structural problems are errors; a document that changed after the parecer is a review flag."""
    return ([m for m in messages if not m.startswith(DRIFT)], [m[len(DRIFT):] for m in messages if m.startswith(DRIFT)])


def crosscheck(p: dict, programs: dict) -> list[str]:
    """Compare a parecer with values extracted from the cached official documents."""
    errs = []
    b = p["brazil"]
    bp = programs.get("brazil", {}).get(f"{b['courseId']}|{b['code']}")
    if bp and bp.get("status") == "lido":
        if b.get("sha256") and bp.get("sha256") and b["sha256"] not in (bp["sha256"], bp.get("contentSha256")):
            errs.append(DRIFT + "brazil.sha256 differs from fetched document")
        if bp.get("hours") is not None and (b.get("hours") or {}).get("value") not in (None, bp["hours"]):
            errs.append(DRIFT + "brazil.hours.value differs from official ementário")
        official = [_norm(t) for t in bp.get("topics") or []]
        if official:
            if [_norm(t) for t in b.get("topics") or []] != official:
                errs.append("brazil.topics must reproduce the official ementa topics")
            assessed = {_norm(t.get("brTopic")) for t in p["topics"]}
            for t in p["topics"]:
                if _norm(t.get("brTopic")) not in official:
                    errs.append(f"brTopic not in official ementa: {t.get('brTopic')!r}")
            for o in official:
                if o not in assessed:
                    errs.append(f"official topic not assessed: {o!r}")
    for f in p["foreign"]:
        fp = programs.get("foreign", {}).get(f"{f['universityId']}|{f['code']}")
        if not fp or fp.get("status") != "lido":
            continue
        if f.get("sha256") and fp.get("sha256") and f["sha256"] not in (fp["sha256"], fp.get("contentSha256")):
            errs.append(DRIFT + f"{f['code']}: sha256 differs from fetched document")
        h = fp.get("hours") or {}
        fh = f.get("hours") or {}
        if (h.get("contact") or {}).get("total") is not None and fh.get("contactTotal") != h["contact"]["total"]:
            errs.append(DRIFT + f"{f['code']}: hours.contactTotal {fh.get('contactTotal')} differs from document {h['contact']['total']}")
        if h.get("ects") is not None and fh.get("ects") not in (None, h["ects"]):
            errs.append(DRIFT + f"{f['code']}: hours.ects differs from document")
    return errs


def _tokens(p: dict) -> set[str]:
    t = unicodedata.normalize("NFD", (p.get("synthesis", "") + " " + p.get("justification", "")).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return set(re.findall(r"[a-z0-9]{4,}", t))


def find_boilerplate(pareceres: list[dict], threshold: float = BOILERPLATE_JACCARD) -> list[tuple[str, str]]:
    toks = [(p["id"], _tokens(p)) for p in pareceres]
    dup = []
    for i in range(len(toks)):
        for j in range(i + 1, len(toks)):
            a, b = toks[i][1], toks[j][1]
            if a and b and len(a & b) / len(a | b) >= threshold:
                dup.append((toks[i][0], toks[j][0]))
    return dup


# ---------------------------------------------------------------- build

def _load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    """Validate all pareceres and write the index; with --check FILE..., validate only and write nothing."""
    argv = sys.argv[1:] if argv is None else argv
    check_only = bool(argv) and argv[0] == "--check"
    data = _load("data.json")
    records = _load("syllabi/records.json")
    mack = _load("syllabi/mackenzie-docs.json")
    extra_path = ROOT / "syllabi" / "fontes-verificadas.json"
    extra = json.loads(extra_path.read_text(encoding="utf-8")) if extra_path.exists() else {"foreign": [], "brazil": []}
    foreign_ok = {(r["universityId"], r["foreignCode"]) for r in records["foreign"] if r["status"] == "ementa_individual"}
    foreign_ok |= {(r["universityId"], r["code"]) for r in extra.get("foreign", []) if r.get("individualSyllabus")}
    br_ok = {(r["courseId"], str(r["code"] or r["name"])) for r in mack["rows"] if r["status"] == "ementa_oficial_correspondente"}
    br_extra = {(r["courseId"], r["code"]): r for r in extra.get("brazil", [])}
    prog_path = ROOT / "syllabi" / "programas.json"
    programs = json.loads(prog_path.read_text(encoding="utf-8")) if prog_path.exists() else {}
    known_foreign = {(f["universityId"], f["code"]) for f in data["foreignCourses"]}
    uni_index = {u["id"]: i for i, u in enumerate(data["universities"])}
    row_index = {(c["id"], r.get("id") or r["name"]): i for c in data["courses"] for i, r in enumerate(c["rows"])}

    files = [Path(a).resolve() for a in argv[1:]] if check_only else (sorted(DIR.rglob("*.json")) if DIR.exists() else [])
    out, errors = [], []
    for fp in files:
        try:
            p = json.loads(fp.read_text(encoding="utf-8"))
            b = p["brazil"]
            key = (b["courseId"], b["code"])
            if key not in row_index:
                raise ParecerError(f"{p.get('id')}: Brazilian component not in matrix")
            for f in p["foreign"]:
                if (f["universityId"], f["code"]) not in known_foreign:
                    raise ParecerError(f"{p.get('id')}: foreign course {f['code']} not in catalogue")
            bprog = programs.get("brazil", {}).get(f"{key[0]}|{key[1]}", {})
            br_doc = key in br_ok or bool(bprog.get("officialSyllabus")) or bool(br_extra.get(key, {}).get("officialSyllabus"))
            current = key in br_ok or bool(bprog.get("current")) or bool(br_extra.get(key, {}).get("current"))
            docs_ok = br_doc and all((f["universityId"], f["code"]) in foreign_ok for f in p["foreign"])
            structural, drift = split_drift(crosscheck(p, programs))
            if structural:
                raise ParecerError(f"{p.get('id')}: " + "; ".join(structural))
            v = validate_parecer(p, docs_ok=docs_ok, current_br=current)
            v["documentDrift"] = drift  # official document changed after the parecer: needs review
            v["brazilDocumentCurrent"] = current
            v["documentsVerified"] = docs_ok
            v["cell"] = [b["courseId"], row_index[key], uni_index[p["foreign"][0]["universityId"]]]
            v["file"] = fp.relative_to(ROOT).as_posix()
            out.append(v)
        except (ParecerError, KeyError, json.JSONDecodeError) as e:
            errors.append(f"{fp.name}: {e}")
    ids = collections.Counter(p["id"] for p in out)
    errors += [f"duplicate id {k}" for k, n in ids.items() if n > 1]
    errors += [f"boilerplate: {a} ~ {b}" for a, b in find_boilerplate(out)]
    if check_only:
        # Also compare with pareceres outside this batch to catch boilerplate across batches.
        others = []
        for fp in sorted(DIR.rglob("*.json")):
            if fp.resolve() not in files:
                try:
                    others.append(json.loads(fp.read_text(encoding="utf-8")))
                except json.JSONDecodeError:
                    pass
        mine = {p["id"] for p in out}
        errors += [f"boilerplate vs other file: {a} ~ {b}" for a, b in find_boilerplate(out + others) if (a in mine) != (b in mine)]
    if errors:
        print("\n".join("ERROR " + e for e in errors), file=sys.stderr)
        return 1
    if check_only:
        for p in out:
            print("OK", p["id"], p["conclusionClass"], "derived=" + p["derivedClass"], p["coverage"], p["hoursComparison"]["state"])
        return 0
    meta = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "count": len(out),
        "byClass": dict(collections.Counter(p["conclusionClass"] for p in out)),
        "byConfidence": dict(collections.Counter(p["confidence"] for p in out)),
        "byCourse": dict(collections.Counter(p["brazil"]["courseId"] for p in out)),
        "combined": sum(p.get("type") == "combinada" for p in out),
        "documentDrift": sum(1 for p in out if p.get("documentDrift")),
        "institutionalDecisions": sum(p["institutionalStatus"] != PENDING for p in out),
        "referenceRatio": REFERENCE_RATIO,
        "rule": "Regra interna do projeto: alta afinidade exige >=75% dos tópicos essenciais integralmente cobertos, "
                "nenhum tópico essencial ausente e horas de contato semestrais analisáveis com razão >=0,75; "
                "não é fórmula oficial do Mackenzie.",
    }
    out.sort(key=lambda p: (p["brazil"]["courseId"], p["brazil"]["code"], -RANK[p["conclusionClass"]], p["id"]))
    INDEX.write_text(json.dumps({"meta": meta, "pareceres": out}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("pareceres:", meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
