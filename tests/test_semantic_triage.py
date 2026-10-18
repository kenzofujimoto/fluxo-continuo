"""Specs for concept-based (not title-based) discovery and per-crossing research states."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from semantic_triage import concepts, coverage_score, row_kind, crossing_state, STATES  # noqa: E402


def test_concepts_are_multilingual():
    assert "redes" in concepts("Reti di calcolatori")
    assert "redes" in concepts("Rețele de calculatoare")
    assert "redes" in concepts("Redes de Computadores")
    assert "banco_dados" in concepts("Bases de Datos")
    assert "trabalho" in concepts("Derecho del Trabajo")
    assert "trabalho" in concepts("Dret del Treball")
    assert "obrigacoes_contratos" in concepts("Direito das Obrigações e Responsabilidade Civil")
    assert "estrategia" in concepts("Strategic Management")


def test_semantic_match_without_shared_title_words():
    br = concepts("Sistemas Operacionais: processos, threads, escalonamento, sincronização, deadlock e memória virtual")
    fr = concepts("Programación concurrente y sistemas operativos")
    assert {"sistemas_operacionais", "concorrencia"} <= br & fr


def test_coverage_score_weights_specific_concepts_and_is_not_a_percentage_of_equivalence():
    idf = {"redes": 3.0, "etica": 0.5, "seguranca": 2.0}
    s = coverage_score({"redes", "seguranca", "etica"}, {"redes", "etica"}, idf)
    assert s["shared"] == ["etica", "redes"]
    assert abs(s["score"] - 3.5 / 5.5) < 1e-6
    assert s["kind"] == "indicador_conceitual"


def test_row_kind_specific_rules():
    assert row_kind("Trabalho de Conclusão de Curso I") == "tcc"
    assert row_kind("TCC II") == "tcc"
    assert row_kind("Estagio Supervisionado") == "estagio"
    assert row_kind("Optativa III") == "optativa_livre"
    assert row_kind("OPTATIVA IX") == "optativa_livre"
    assert row_kind("Marketing I") == "disciplina"


def test_crossing_states_never_declare_incompatibility():
    assert set(STATES) >= {"parecer_concluido", "candidata_registrada", "candidata_semantica", "regra_especifica",
                           "sem_candidata_no_catalogo_indexado", "catalogo_insuficiente"}
    assert all("incompat" not in s for s in STATES)
    st = crossing_state(kind="disciplina", pareceres=[], registered=[], semantic=[], area_courses=3)
    assert st["state"] == "catalogo_insuficiente"
    st = crossing_state(kind="disciplina", pareceres=[], registered=[], semantic=[], area_courses=40)
    assert st["state"] == "sem_candidata_no_catalogo_indexado"
    assert "40" in st["note"] and "não" in st["note"].lower()
    st = crossing_state(kind="tcc", pareceres=[], registered=[], semantic=[], area_courses=40)
    assert st["state"] == "regra_especifica"
    st = crossing_state(kind="disciplina", pareceres=[{"id": "x", "conclusionClass": "afinidade_parcial"}],
                        registered=["A"], semantic=[], area_courses=40)
    assert st["state"] == "parecer_concluido"


def test_candidate_requires_identity_concepts_on_both_sides():
    from semantic_triage import is_candidate
    idf = {c: 2.0 for c in ("pesquisa_operacional", "programacao", "algoritmos", "paralelismo", "complexidade")}
    br_title = concepts("Pesquisa Operacional I")
    br_all = br_title | {"programacao"}
    # programming course shares only a generic concept and nothing of the Brazilian title
    assert not is_candidate(br_title, br_all, concepts("Elementary Programming"), {"programacao"}, idf)
    assert is_candidate(br_title, br_all, concepts("Investigación Operativa"), {"pesquisa_operacional"}, idf)


def test_linear_programming_is_not_programming():
    assert "programacao" not in concepts("Programação linear e método simplex")
    assert "pesquisa_operacional" in concepts("Programação linear e método simplex")


def test_social_security_is_not_information_security_and_generic_concepts_are_not_identity():
    from semantic_triage import is_candidate
    assert "seguranca" not in concepts("Seguridad Social")
    assert "seguridade" in concepts("Seguridad Social")
    assert "calculo" not in concepts("limites da coisa julgada")
    idf = {c: 2.0 for c in ("economia", "direitos_humanos")}
    # only the generic 'economia' concept is shared
    assert not is_candidate({"direitos_humanos"}, {"direitos_humanos", "economia"}, {"economia"}, {"economia"}, idf)


def test_code_optimisation_is_not_operations_research():
    assert "pesquisa_operacional" not in concepts("Compiler Design & Optimisation")
    assert "pesquisa_operacional" in concepts("Optimisation models and linear programming")
    assert "pesquisa_operacional" in concepts("Otimização linear e métodos quantitativos")


def test_outside_agreement_courses_never_become_new_suggestions(tmp_path, monkeypatch):
    import json
    import semantic_triage

    fixture = {
        "universities": [{"id": "university", "courses": {"cc": True}}],
        "courses": [{"id": "cc", "rows": [{"id": "BR", "name": "Database SQL"}]}],
        "foreignCourses": [
            {"universityId": "university", "code": "LEGACY", "name": "Database SQL"},
            {"universityId": "university", "code": "OUTSIDE", "name": "Database SQL", "sourceEligibility": "outside_agreement"},
        ],
        "matches": [],
    }
    (tmp_path / "syllabi").mkdir()
    (tmp_path / "data.json").write_text(json.dumps(fixture), encoding="utf-8")
    (tmp_path / "triagem.json").write_text(json.dumps({"pairs": [["cc", 0, 0]]}), encoding="utf-8")
    (tmp_path / "syllabi/records.json").write_text(json.dumps({"foreign": []}), encoding="utf-8")
    monkeypatch.setattr(semantic_triage, "ROOT", tmp_path)
    monkeypatch.setattr(semantic_triage, "OUT", tmp_path / "output.json")
    assert semantic_triage.main() == 0
    output = json.loads((tmp_path / "output.json").read_text(encoding="utf-8"))
    assert [candidate[0] for candidate in output["crossings"][0][4]] == ["LEGACY"]
    assert all("OUTSIDE" not in item["foreign"] for item in output["combined"])

    # Historical registered relations and reviews remain available even after scope correction.
    fixture["matches"] = [{"courseId": "cc", "mackCode": "BR", "universityId": "university", "foreignCode": "OUTSIDE"}]
    (tmp_path / "data.json").write_text(json.dumps(fixture), encoding="utf-8")
    (tmp_path / "syllabi/pareceres-index.json").write_text(json.dumps({"pareceres": [
        {"id": "historical-review", "cell": ["cc", 0, 0], "conclusionClass": "afinidade_parcial"}
    ]}), encoding="utf-8")
    assert semantic_triage.main() == 0
    output = json.loads((tmp_path / "output.json").read_text(encoding="utf-8"))
    assert output["crossings"][0][3] == "parecer_concluido"
    assert [candidate[0] for candidate in output["crossings"][0][4]] == ["LEGACY"]


def test_worklist_excludes_outside_agreement_from_registered_and_stale_semantic_candidates(tmp_path, monkeypatch):
    import worklist

    sources = {
        "data.json": {
            "universities": [{"id": "university"}],
            "courses": [{"id": "cc", "rows": [{"id": "BR", "name": "Database SQL"}]}],
            "foreignCourses": [
                {"universityId": "university", "code": "LEGACY"},
                {"universityId": "university", "code": "OUTSIDE", "sourceEligibility": "outside_agreement"},
            ],
            "matches": [
                {"courseId": "cc", "mackCode": "BR", "universityId": "university", "foreignCode": code}
                for code in ["LEGACY", "OUTSIDE"]
            ],
        },
        "syllabi/programas.json": {
            "brazil": {"cc|BR": {"status": "lido"}},
            "foreign": {f"university|{code}": {"status": "lido"} for code in ["LEGACY", "OUTSIDE"]},
        },
        "syllabi/records.json": {"foreign": [
            {"universityId": "university", "foreignCode": code, "status": "ementa_individual"}
            for code in ["LEGACY", "OUTSIDE"]
        ]},
        "syllabi/pareceres-index.json": {"pareceres": []},
        "syllabi/triagem-semantica.json": {"crossings": [["cc", 0, 0, "candidata_semantica", [["OUTSIDE", 1, [], "ementa_individual"]], ""]]},
    }
    monkeypatch.setattr(worklist, "ROOT", tmp_path)
    monkeypatch.setattr(worklist, "_load", sources.__getitem__)
    assert [pair["foreign"] for pair in worklist.ready_pairs()] == ["LEGACY"]
    assert len(sources["data.json"]["matches"]) == 2
