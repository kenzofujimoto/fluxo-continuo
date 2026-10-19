"""Regression specs for cached document extraction and syllabus evidence flags."""
import json
from pathlib import Path
import sys

import pytest
import fitz
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_documents as documents  # noqa: E402


def test_fetch_preserves_complete_pdf_form_text_beyond_visible_widget_rectangle(tmp_path, monkeypatch):
    pdf = fitz.open()
    page = pdf.new_page(width=300, height=300)
    page.insert_text((20, 20), "Course 8022971")
    full = "Part one: introductory law.\nPart two: digital platforms.\nPart three: health data and artificial intelligence."
    widget = fitz.Widget()
    widget.field_name = "tb_programma_ita"
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_flags = fitz.PDF_TX_FIELD_IS_MULTILINE
    widget.rect = fitz.Rect(20, 40, 260, 62)
    widget.text_fontsize = 12
    widget.field_value = full
    page.add_widget(widget)
    raw = pdf.tobytes()
    url = "https://example.edu/programme.pdf"
    response = SimpleNamespace(status_code=200, url=url, headers={"content-type": "application/pdf"},
                               iter_content=lambda size: iter([raw]))
    monkeypatch.setattr(documents.requests, "get", lambda *args, **kwargs: response)
    monkeypatch.setattr(documents, "TXT", tmp_path)
    result = documents.fetch(url, None, True)
    assert result["status"] == "lido"
    text = documents.text_path(url).read_text(encoding="utf-8")
    assert "Part three: health data and artificial intelligence." in text
    assert text.count("Part one: introductory law.") == 1
    assert text.count("Course 8022971") == 1


def test_pdf_form_value_already_visible_is_not_duplicated():
    pdf = fitz.open()
    page = pdf.new_page()
    widget = fitz.Widget()
    widget.field_name = "objectives"
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = fitz.Rect(20, 20, 500, 100)
    widget.field_value = "Understand data protection and privacy."
    page.add_widget(widget)
    assert documents.extract_pdf_page_text(page).count(widget.field_value) == 1


@pytest.mark.parametrize("ementa", ["", "Estudo de requisitos e projeto de software."])
def test_fci_document_presence_does_not_make_an_empty_ementa_current(tmp_path, monkeypatch, ementa):
    """An official PDF may contain an empty syllabus field next to valid course blocks."""
    url = "https://www.mackenzie.br/FCI/5-etapa.pdf"
    syllabi = tmp_path / "syllabi"
    syllabi.mkdir()
    row = {"courseId": "cc", "code": "ENEC61012", "name": "PROJETO DE SOFTWARE",
           "documentName": "PROJETO DE SOFTWARE", "source": url, "stage": 5,
           "status": "ementa_oficial_correspondente"}
    (tmp_path / "data.json").write_text(json.dumps({"courses": [{"id": "cc", "rows": [
        {"id": "ENEC61012", "name": "PROJETO DE SOFTWARE", "semester": 5}]}]}), encoding="utf-8")
    (syllabi / "mackenzie-docs.json").write_text(json.dumps({"rows": [row]}), encoding="utf-8")
    monkeypatch.setattr(documents, "ROOT", tmp_path)
    monkeypatch.setattr(documents, "TXT", tmp_path / "text")
    monkeypatch.setattr(documents, "aliases", lambda: [])
    monkeypatch.setattr(documents, "brazil_registry", lambda: [])
    documents.TXT.mkdir()
    text = ("Curso\nCIÊNCIA DA COMPUTAÇÃO\nNúcleo Temático\nX\nEtapa\n5\n"
            "Comp. Curricular\nPROJETO DE SOFTWARE\nCódigo\nENEC61012\n"
            f"Ementa\n{ementa}\nBibliografia básica\nSoftware engineering textbook.\n")
    documents.text_path(url).write_text(text, encoding="utf-8")
    extracted = documents.extract_programs({url: {"status": "lido", "sha256": "official-pdf"}}, [], [url])
    syllabus = extracted["brazil"]["cc|ENEC61012"]
    assert syllabus["ementa"] == ementa
    assert syllabus["officialSyllabus"] is bool(ementa)
    assert syllabus["current"] is bool(ementa)
    assert extracted["meta"]["brazilCurrent"] == int(bool(ementa))
    if not ementa:
        assert syllabus["topics"] == []
        assert "vazi" in syllabus["currencyNote"].lower()
    else:
        assert syllabus["topics"] == ["Estudo de requisitos e projeto de software"]
        assert syllabus["currencyNote"] == "Ementário público FCI 2025, câmpus Alphaville"
