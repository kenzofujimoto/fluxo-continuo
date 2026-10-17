"""Specs for catalogue expansion parsers (no network)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from expand_catalogue import parse_leeds_module, merge_courses  # noqa: E402

LEEDS = ("2026/27 Undergraduate Module Catalogue LAW1101 PRIME: Professions, Reflections, Identities, Motivations and Ethics "
         "20 Credits Class Size: 550 Module manager: X Taught: Semesters 1 & 2 (Sep to Jun) View Timetable Year running 2026/27 "
         "Module summary The PRIME module. Objectives To develop. Learning outcomes 1. Reflect. Syllabus Details of the syllabus will be provided on the Minerva "
         "Teaching Methods Delivery type Number Length hours Student hours On-line Learning 8 1 8 Lecture 14 1 14 Seminar 7 2 14 "
         "Private study hours 164 Total Contact hours 36 Total hours (100hr per 10 credits) 200 Opportunities for Formative Feedback")


def test_parse_leeds_module_fields():
    m = parse_leeds_module(LEEDS, "LAW1101")
    assert m["name"] == "PRIME: Professions, Reflections, Identities, Motivations and Ethics"
    assert m["credits"] == 20 and m["creditUnit"] == "UK credits"
    assert m["period"] == "Semesters 1 & 2 (Sep to Jun)"
    assert m["contactHours"] == 36 and m["selfStudy"] == 164 and m["totalHours"] == 200
    assert m["delivery"] == [["On-line Learning", 8], ["Lecture", 14], ["Seminar", 14]]
    assert m["academicYear"] == "2026/2027"
    # the syllabus section only points to the VLE: content must be flagged as not published
    assert m["syllabusPublished"] is False


def test_merge_adds_only_new_courses_and_never_removes():
    existing = [{"universityId": "gb-leeds", "code": "COMP3270", "name": "HPC", "source": "https://a"}]
    new = [{"universityId": "gb-leeds", "code": "COMP3270", "name": "HPC2", "source": "https://b"},
           {"universityId": "gb-leeds", "code": "LAW1101", "name": "PRIME", "source": "https://c"}]
    merged, added = merge_courses(existing, new)
    assert [c["code"] for c in merged] == ["COMP3270", "LAW1101"]
    assert merged[0]["name"] == "HPC" and added == 1


def test_merge_skips_same_course_already_indexed_under_another_code():
    existing = [{"universityId": "es-salamanca", "code": "CAT-USAL-206909", "name": "DERECHO ROMANO", "source": "https://a"}]
    new = [{"universityId": "es-salamanca", "code": "102301", "name": "Derecho Romano", "source": "https://b"}]
    merged, added = merge_courses(existing, new)
    assert added == 0 and len(merged) == 1


def test_parse_usal_guide_fields():
    from expand_catalogue import parse_usal_guide
    t = ("DERECHO ROMANO GRADO EN DERECHO Curso 2026/2027 1. Datos de la asignatura (Fecha última modificación: x) "
         "Código 102301 Plan 223 ECTS 6.00 Carácter BÁSICA Curso 1 Periodicidad Primer Semestre Idioma ESPAÑOL Área DERECHO ROMANO")
    g = parse_usal_guide(t)
    assert g == {"code": "102301", "ects": 6.0, "character": "BÁSICA", "year": 1, "period": "Primer Semestre",
                 "language": "ESPAÑOL", "academicYear": "2026/2027"}
