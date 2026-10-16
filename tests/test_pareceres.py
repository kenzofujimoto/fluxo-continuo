"""Specs for parecer validation rules: evidence, hours units, classification and anti-boilerplate."""
from pathlib import Path
import copy
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_pareceres import (  # noqa: E402
    compare_hours, coverage_summary, derive_class, validate_parecer, find_boilerplate, ParecerError,
)


def topic(status, essential=True, ev="C4. MPI", loc="8.1 C4"):
    t = {"brTopic": "x", "essential": essential, "status": status}
    if status in ("coberto", "parcial"):
        t.update({"foreignEvidence": ev, "foreignLocation": loc})
    if status == "nao_encontrado":
        t["scopeExamined"] = "Seções 7, 8.1 e 8.2"
    return t


# ---------- hours ----------

def test_hours_comparable_when_both_semester_contact_with_known_unit():
    r = compare_hours({"value": 63.33, "unit": "hora_relogio", "basis": "semestre"},
                      {"contactTotal": 60, "basis": "semestre", "hourLengthMinutes": 60})
    assert r["state"] == "comparavel"
    assert r["diffAbs"] == pytest.approx(-3.33, abs=0.01)
    assert r["ratio"] == pytest.approx(60 / 63.33, abs=0.001)


def test_hours_conditional_when_foreign_hour_length_unknown():
    r = compare_hours({"value": 63.33, "unit": "hora_relogio", "basis": "semestre"},
                      {"contactTotal": 70, "basis": "semestre", "hourLengthMinutes": None})
    assert r["state"] == "comparavel_condicional"
    assert r["diffPct"] == pytest.approx((70 - 63.33) / 63.33 * 100, abs=0.05)
    # 50-minute scenario is reported as a bound, not as the answer
    assert r["ratioIf50min"] == pytest.approx(70 * 50 / 60 / 63.33, abs=0.001)


def test_hours_never_compares_ects_or_weekly_values():
    assert compare_hours({"value": 63.33, "unit": "hora_relogio", "basis": "semestre"},
                         {"contactTotal": None, "ects": 6, "basis": None})["state"] == "nao_comparavel"
    assert compare_hours({"value": 63.33, "unit": "hora_relogio", "basis": "semestre"},
                         {"contactTotal": 4, "basis": "semana"})["state"] == "nao_comparavel"
    assert compare_hours({"value": None, "unit": None, "basis": None},
                         {"contactTotal": 70, "basis": "semestre"})["state"] == "nao_comparavel"


# ---------- coverage & classification ----------

def test_coverage_counts_only_essential_topics():
    s = coverage_summary([topic("coberto"), topic("coberto"), topic("parcial"), topic("nao_encontrado"),
                          topic("coberto", essential=False)])
    assert s == {"essential": 4, "coberto": 2, "parcial": 1, "nao_encontrado": 1, "nao_verificavel": 0,
                 "fullRatio": 0.5, "anyRatio": 0.75}


def test_high_affinity_requires_topics_and_analysable_hours():
    cov = coverage_summary([topic("coberto")] * 4)
    assert derive_class(cov, {"state": "comparavel_condicional", "ratio": 1.1}, docs_ok=True) == "alta_afinidade"
    # hours not analysable -> cannot be high affinity
    assert derive_class(cov, {"state": "nao_comparavel"}, docs_ok=True) == "afinidade_parcial"
    # foreign hours far lower -> partial
    assert derive_class(cov, {"state": "comparavel", "ratio": 0.5}, docs_ok=True) == "afinidade_parcial"


def test_missing_documents_or_unverifiable_topics_mean_insufficient_evidence():
    cov = coverage_summary([topic("coberto")] * 4)
    assert derive_class(cov, {"state": "comparavel", "ratio": 1}, docs_ok=False) == "evidencia_insuficiente"
    cov = coverage_summary([topic("coberto"), topic("nao_verificavel"), topic("nao_verificavel")])
    assert derive_class(cov, {"state": "comparavel", "ratio": 1}, docs_ok=True) == "evidencia_insuficiente"


def test_low_affinity_when_most_topics_absent():
    cov = coverage_summary([topic("parcial"), topic("nao_encontrado"), topic("nao_encontrado")])
    assert derive_class(cov, {"state": "comparavel", "ratio": 1}, docs_ok=True) == "baixa_afinidade"


# ---------- validation ----------

def base_parecer():
    return {
        "id": "cc|ENEC61020|ro-babes|MLE5077",
        "schemaVersion": 2,
        "brazil": {"courseId": "cc", "code": "ENEC61020", "name": "Computação Paralela",
                   "source": "https://www.mackenzie.br/x.pdf", "location": "p. 118", "documentYear": 2025,
                   "hours": {"value": 63.33, "unit": "hora_relogio", "basis": "semestre"}},
        "foreign": [{"universityId": "ro-babes", "code": "MLE5077", "name": "Parallel and Distributed Programming",
                     "source": "https://www.cs.ubbcluj.ro/x.pdf", "location": "Secções 3, 8", "academicYear": "2026/2027",
                     "hours": {"contactTotal": 70, "basis": "semestre", "hourLengthMinutes": None}}],
        "topics": [topic("coberto")] * 4,
        "synthesis": "Programas convergem em arquitetura paralela e desempenho.",
        "justification": "Cobertura dos quatro eixos da ementa brasileira com evidência nas unidades C2-C9.",
        "conclusionClass": "alta_afinidade",
        "institutionalStatus": "aguardando_validacao_institucional",
        "confidence": "moderada",
        "confidenceRationale": "Ambos os documentos oficiais; hora estrangeira sem duração declarada.",
        "limitations": ["Oferta 2027.2 não confirmada"],
        "practical": {"offer2027": "nao_confirmada"},
    }


def test_valid_parecer_passes_and_gets_computed_fields():
    out = validate_parecer(base_parecer(), docs_ok=True)
    assert out["coverage"]["fullRatio"] == 1.0
    assert out["hoursComparison"]["state"] == "comparavel_condicional"
    assert out["derivedClass"] == "alta_afinidade"


def test_rejects_upgrade_beyond_derived_class():
    p = base_parecer()
    p["topics"] = [topic("coberto"), topic("nao_encontrado"), topic("nao_encontrado")]
    with pytest.raises(ParecerError, match="class"):
        validate_parecer(p, docs_ok=True)


def test_allows_justified_conservative_downgrade_only():
    p = base_parecer()
    p["conclusionClass"] = "afinidade_parcial"
    with pytest.raises(ParecerError, match="downgradeReason"):
        validate_parecer(p, docs_ok=True)
    p["downgradeReason"] = "Profundidade estrangeira introdutória frente ao nível exigido."
    assert validate_parecer(p, docs_ok=True)["conclusionClass"] == "afinidade_parcial"


def test_rejects_topic_without_evidence_location():
    p = base_parecer()
    p["topics"] = [dict(topic("coberto"), foreignLocation="")] + [topic("coberto")] * 3
    with pytest.raises(ParecerError, match="evidence"):
        validate_parecer(p, docs_ok=True)


def test_rejects_homologation_language_and_status():
    p = base_parecer()
    p["institutionalStatus"] = "homologada"
    with pytest.raises(ParecerError, match="institutionalStatus"):
        validate_parecer(p, docs_ok=True)
    p = base_parecer()
    p["synthesis"] = "Disciplina equivalente homologada pelo Mackenzie."
    with pytest.raises(ParecerError, match="homolog"):
        validate_parecer(p, docs_ok=True)
    p = base_parecer()
    p["synthesis"] = "Não há equivalência homologada; parecer preliminar."
    validate_parecer(p, docs_ok=True)


def test_rejects_non_https_sources():
    p = base_parecer()
    p["foreign"][0]["source"] = "javascript:alert(1)"
    with pytest.raises(ParecerError, match="source"):
        validate_parecer(p, docs_ok=True)


def test_detects_boilerplate_between_pareceres():
    a = base_parecer()
    b = copy.deepcopy(a)
    b["id"] = "cc|X|ro-babes|Y"
    c = copy.deepcopy(a)
    c["id"] = "cc|Z|ro-babes|W"
    c["synthesis"] = "Lógica proposicional coincide, mas teoria dos conjuntos falta no programa romeno."
    c["justification"] = "Circuitos combinacionais excedem a ementa; indução matemática não aparece."
    dup = find_boilerplate([a, b, c])
    assert dup == [(a["id"], b["id"])]
