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


def test_mackenzie_si_inline_layout_variants():
    txt = ("Coordenador Adjunto \n\n\x0c\n \nCurso \nSISTEMAS DE INFORMAÇÃO \nNúcleo Temático \n"
           "Formação Cidadã e Profissional Etapa \n3 \nComp. Curricular DESENVOLVIMENTO WEB II \nCódigo \n"
           "Carga horária (horas) \n31,67 \nPresencial \n2 \nEspecífico \nPrática como CC \nX \nPercentual \n50,00 \n% \n"
           "Ementa \nConceitos de integração de sistemas web. Práticas de Extensão. \nBibliografia básica \nX")
    b = parse_mackenzie_blocks(txt)
    assert len(b) == 1
    assert b[0]["name"] == "DESENVOLVIMENTO WEB II"
    assert b[0]["stage"] == 3 and b[0]["theme"] == "Formação Cidadã e Profissional"
    assert b[0]["hours"] == 31.67
    assert b[0]["extensionPercent"] == 50.0
    # SI layout drops empty cells: weekly split cannot be read reliably
    assert b[0]["weekly"] is None


# ---------- CCSA / Direito ficha layout ----------
from program_fields import parse_ficha_blocks  # noqa: E402


def test_ficha_blocks_read_name_hours_stage_ementa_and_content():
    text = (FIX / "ccsa_ficha_excerpt.txt").read_text(encoding="utf-8")
    blocks = {b["name"]: b for b in parse_ficha_blocks(text)}
    amb = blocks["Ambiente Profissional do Administrador"]
    assert amb["hours"] == 63.3 and amb["hourUnit"] == "hora_relogio"
    assert amb["stage"] == 1
    assert amb["ementa"].startswith("Estudo do conceito de organização")
    assert "Tomada de decisão em administração" in amb["programContent"]
    cts = blocks["Ciência, Tecnologia e Sociedade na Administração e nos Negócios"]
    # '2 aulas' is a weekly class-period count, never semester hours
    assert cts["hours"] is None and cts["weeklyClassPeriods"] == 2
    assert cts["programContent"][0] == "Métodos de leitura científica"
    info = blocks["Informática Básica para Administradores"]
    assert info["hours"] == 31.7


def test_ficha_weekly_law_hours():
    txt = ("Nome do Componente Curricular: \nDIREITO CIVIL I \nCódigo do Componente Curricular: \n"
           "Carga horária: 4 horas aula \nEtapa: 2ª \nEmenta: \nParte geral do Código Civil. Pessoas naturais e jurídicas. \n"
           "Bibliografia Básica: \nX")
    b = parse_ficha_blocks(txt)[0]
    assert b["name"] == "DIREITO CIVIL I" and b["stage"] == 2
    assert b["hours"] is None and b["weeklyClassPeriods"] == 4
    assert b["ementa"] == "Parte geral do Código Civil. Pessoas naturais e jurídicas."


def test_ficha_ignores_code_label_and_keeps_ementa_with_word_objetivos():
    txt = ("Disciplina: Logística Empresarial \nCódigo \nda \nDisciplina: \nENEX01259 \nCarga horária: 63,3 \nhoras \n"
           "Etapa: 6 \nEmenta: \nObjetivos financeiros e estudo dos objetivos do governo. \nConteúdo Programático: \n"
           "1) Conceitos de logística; \n2. Serviço aos Clientes \nBibliografia Básica: \nX")
    b = parse_ficha_blocks(txt)
    assert [x["name"] for x in b] == ["Logística Empresarial"]
    assert b[0]["hours"] == 63.3 and b[0]["stage"] == 6
    assert b[0]["ementa"] == "Objetivos financeiros e estudo dos objetivos do governo."
    assert b[0]["programContent"] == ["Conceitos de logística", "Serviço aos Clientes"]


def test_ficha_code_label_does_not_swallow_next_header_and_small_hours_are_weekly():
    txt = ("Disciplina: Logística Empresarial \nCódigo \nda \nDisciplina: \nENEX01259 \nCarga horária: 63,3 horas \n"
           "Etapa: 6 \nEmenta: \nCaracterização dos recursos. \nBibliografia Básica: \nX\n"
           "Disciplina: Metodologia de Pesquisa em Ciências Sociais \nAplicadas \nCódigo da Disciplina: \nENEX01329 \n"
           "Carga horária: 4 horas \nEtapa: 6 \nEmenta: \nEstudo de métodos de pesquisa científica. \nBibliografia Básica: \nX")
    b = {x["name"]: x for x in parse_ficha_blocks(txt)}
    assert set(b) == {"Logística Empresarial", "Metodologia de Pesquisa em Ciências Sociais Aplicadas"}
    met = b["Metodologia de Pesquisa em Ciências Sociais Aplicadas"]
    assert met["hours"] is None and met["weeklyClassPeriods"] == 4


def test_split_ementa_fine_breaks_long_legal_paragraphs_on_sentences_and_semicolons():
    from program_fields import split_ementa_fine
    t = ("Estudo do pluralismo jurídico. A análise suscita reflexões como: a discussão do pluralismo; "
         "exame da aculturação jurídica; análise dos direitos humanos.")
    assert split_ementa_fine(t) == ["Estudo do pluralismo jurídico",
                                    "A análise suscita reflexões como: a discussão do pluralismo",
                                    "exame da aculturação jurídica", "análise dos direitos humanos"]


def test_mackenzie_page_header_inside_ementa_is_removed_and_anomalies_flagged():
    txt = ("Curso \nCIÊNCIA DA COMPUTAÇÃO \nNúcleo Temático \nX \nEtapa \n7 \nComp. Curricular \nPARADIGMAS DE PROGRAMAÇÃO \n"
           "Código\n \nCarga horária (horas) \n63,33 \nPresencial \n2 \n \n \nEspecífico \nEmenta  \n"
           "\n\x0c\nUNIVERSIDADE PRESBITERIANA MACKENZIE \nFaculdade de Computação e Informática \n \n \n105 \n \n"
           "Estudo evolutivo das linguagens. \nBibliografia básica \nX")
    b = parse_mackenzie_blocks(txt.replace("\n\x0c\n", "\n"))[0]
    assert b["ementa"] == "Estudo evolutivo das linguagens."
    assert any("h-a semanais" in a for a in b["anomalies"])


def test_ubb_older_tables_with_split_seminar_lab_or_dash():
    a = parse_ubb("x", "  3.4. Total of hours in the curriculum    70   of which: 3.5. course  28     3.6. seminar/ laboratory         14+28\n Time allocation")
    assert a["hours"]["contact"] == {"total": 70, "course": 28, "seminarLab": 42}
    b = parse_ubb("x", " 3.4. Total hours in the curriculum       28    of which: 3.5 course       -                            28  seminar\nTime allotment")
    assert b["hours"]["contact"] == {"total": 28, "course": 0, "seminarLab": 28}
    c = parse_ubb("x", " 3.4. Total hours in the curriculum       84    of which: 3.5 course   28\n  seminar/laboratory/project   + 28 lab\nTime allotment")
    assert c["hours"]["contact"] == {"total": 84, "course": 28, "seminarLab": None}
