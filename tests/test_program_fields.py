"""Specs for structured extraction of official syllabus fields (no network)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from program_fields import parse_ubb, parse_mackenzie_blocks, split_ementa  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


def ubb_text():
    return (FIX / "ubb_course_description.txt").read_text(encoding="utf-8")


def ubb_sorted():
    return (FIX / "ubb_course_description_sorted.txt").read_text(encoding="utf-8")


def mack_text():
    return (FIX / "mackenzie_stage8_excerpt.txt").read_text(encoding="utf-8")


def test_ubb_identification_fields():
    f = parse_ubb(ubb_text())
    assert f["academicYear"] == "2026/2027"
    assert f["code"] == "MLE5077"
    assert f["level"] == "Bachelor"
    assert f["yearOfStudy"] == 3
    assert f["semester"] == 5
    assert f["courseStatus"] == "Compulsory"
    assert f["faculty"] == "Faculty of Mathematics and Computer Science"


def test_ubb_hours_are_split_and_never_derived_from_ects():
    h = parse_ubb(ubb_text(), ubb_sorted())["hours"]
    assert h["weekly"] == {"total": 5, "course": 2, "seminarLab": 3}
    assert h["contact"] == {"total": 70, "course": 28, "seminarLab": 42}
    assert h["selfStudy"] == 55
    assert h["totalWorkload"] == 125
    assert h["ects"] == 5
    assert h["contactBasis"] == "semestre"
    # Hour length is not declared in the UBB form: must stay unknown.
    assert h["hourLengthMinutes"] is None


def test_ubb_prerequisites_and_topics():
    f = parse_ubb(ubb_text())
    assert "Operating Systems" in f["prerequisites"]
    course = f["courseTopics"]
    assert course[0]["id"] == "C1"
    assert "parallel" in course[0]["text"].lower()
    assert any("MPI" in t["text"] for t in course)
    assert any("CUDA" in t["text"] for t in course)
    # teaching-method column must not leak into topic text
    assert all("Exposure" not in t["text"] for t in course)
    lab = f["labTopics"]
    assert lab and lab[0]["id"].startswith("L1")
    assert any("OpenMP" in t["text"] for t in lab)
    assert all("Dialogue" not in t["text"] for t in lab)


def test_mackenzie_block_hours_split_and_ementa():
    blocks = parse_mackenzie_blocks(mack_text())
    par = next(b for b in blocks if b["name"] == "COMPUTAÇÃO PARALELA")
    assert par["course"] == "CIÊNCIA DA COMPUTAÇÃO"
    assert par["stage"] == 8
    assert par["hours"] == 63.33
    assert par["weekly"] == {"teorica": 2, "pratica": 2, "atelie": 0}
    assert par["hourUnit"] == "hora_relogio"
    assert par["ementa"].startswith("Estudo de arquiteturas de sistemas paralelos")
    assert "Bibliografia" not in par["ementa"]
    law = next(b for b in blocks if b["course"] == "DIREITO")
    assert law["weekly"]["teorica"] == 4 and law["weekly"]["pratica"] == 0
    assert law["optional"] is True
    assert par["optional"] is False


def test_split_ementa_into_topics():
    topics = split_ementa("Estudo de arquiteturas de sistemas paralelos. Metodologia de desenvolvimento de "
                          "programas paralelos. Análise de algoritmos paralelos.")
    assert topics == ["Estudo de arquiteturas de sistemas paralelos",
                      "Metodologia de desenvolvimento de programas paralelos",
                      "Análise de algoritmos paralelos"]
    assert split_ementa("Variáveis; decisões; repetições") == ["Variáveis", "decisões", "repetições"]
    assert split_ementa("") == []


def test_ubb_older_template_row_layout():
    sorted_rows = ("SYLLABUS\nUniversity year 2025-2026\n"
                   " 3.4. Total hours in the curriculum         56                   28                           28\n"
                   "  3.8. Total hours per semester   125\n 3.9. Number of ECTS credits 5\n")
    f = parse_ubb("SYLLABUS\nComputer Networks\nUniversity year 2025-2026\n1.5. Study cycle\nBachelor\n1.6. Study programme", sorted_rows)
    assert f["academicYear"] == "2025/2026"
    assert f["level"] == "Bachelor"
    assert f["hours"]["contact"] == {"total": 56, "course": 28, "seminarLab": 28}
    assert f["hours"]["ects"] == 5
    assert f["hours"]["totalWorkload"] == 125


def test_ubb_inconsistent_hour_row_is_rejected():
    f = parse_ubb("x", " 3.1. Hours per week 2 2 2\n")
    assert f["hours"]["weekly"] is None
