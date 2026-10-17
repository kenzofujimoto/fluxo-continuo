"""Specs for verifying that a fetched page is the individual official programme of one course."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from resolve_syllabi import verify_programme, find_course_link, academic_year, candidate_urls  # noqa: E402

GUIDE = ("ADMINISTRACIÓN DE RECURSOS HUMANOS GRADO EN ADMINISTRACIÓN Y DIRECCIÓN DE EMPRESAS Curso 2025/2026 "
         "1. Datos de la asignatura Código 103848 ECTS 6.00 Periodicidad Segundo Semestre "
         "3. Objetivos Conocimientos del marco competitivo. 5. Contenidos Tema 1. Planificación de plantillas. "
         "Tema 2. Reclutamiento y selección. Tema 3. Retribución. " + "texto " * 200)


def test_verifies_individual_guide_by_title_and_content_section():
    v = verify_programme(GUIDE, "ADMINISTRACIÓN DE RECURSOS HUMANOS", "CAT-USAL-210314", other_titles=["Contabilidad", "Marketing"])
    assert v["ok"] and "title" in v["identifiedBy"] and v["contentMarker"]


def test_rejects_catalogue_listing_many_courses():
    listing = "Plan de estudios " + " ".join(f"Asignatura {t} contenidos" for t in ["Contabilidad", "Marketing", "Estadística", "Derecho Civil", "Microeconomía"]) + " ADMINISTRACIÓN DE RECURSOS HUMANOS " + "x " * 500
    v = verify_programme(listing, "ADMINISTRACIÓN DE RECURSOS HUMANOS", "X", other_titles=["Contabilidad", "Marketing", "Estadística", "Derecho Civil", "Microeconomía"])
    assert not v["ok"] and "listagem" in v["reason"]


def test_rejects_page_without_content_section_or_identity():
    assert not verify_programme("Página institucional sobre a universidade " * 100, "Direito Civil", "X", [])["ok"]
    assert not verify_programme("Contenidos Tema 1 " + "x " * 600, "Direito Civil", "X", [])["ok"]


def test_academic_year():
    assert academic_year("Curso 2025/2026 Datos") == "2025/2026"
    assert academic_year("Programa docente (2026-27)") == "2026/2027"
    assert academic_year("sem ano") is None


def test_find_course_link_by_normalized_anchor_text():
    html = ('<ul><li><a href="/ins/1">Diritto amministrativo I</a></li><li><a href="/ins/2">Diritto amministrativo II</a></li>'
            '<li><a href="/ins/3">Diritto costituzionale</a></li></ul>')
    assert find_course_link(html, "https://x.it/lista/", "Diritto amministrativo I") == "https://x.it/ins/1"
    assert find_course_link(html, "https://x.it/lista/", "Diritto costituzionale") == "https://x.it/ins/3"
    assert find_course_link(html, "https://x.it/lista/", "Diritto penale") is None


def test_candidate_urls_for_constructible_providers():
    assert candidate_urls("es-cadiz", "21714038", "https://esingenieria.uca.es/docencia/") == ["https://asignaturas.uca.es/2026-27/21714038", "https://asignaturas.uca.es/2025-26/21714038"]
    assert candidate_urls("es-salamanca", "CAT-USAL-1", "https://guias.usal.es/node/210314") == ["https://guias.usal.es/node/210314"]


def test_code_match_with_another_course_title_is_rejected():
    page = ("Programa docente (2026-27) <21719027 | ELECTRÓNICA DIGITAL> Asignatura: 21719027 | ELECTRÓNICA DIGITAL "
            "Temario Tema 1 Sistemas de numeración. " + "texto " * 300)
    v = verify_programme(page, "Proyectos Informáticos", "21719027", [])
    assert not v["ok"] and "outra disciplina" in v["reason"]
    ok = ("Programa docente <21714014 | ANÁLISIS DE ALGORITMOS Y ESTRUCTURAS DE DATOS> Temario Tema 1. " + "x " * 500)
    assert verify_programme(ok, "Análisis de Algoritmos y Estructura de Datos", "21714014", [])["ok"]
