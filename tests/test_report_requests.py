"""Specs for the documentary request report (what to ask Mackenzie and foreign universities)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from report_requests import brazil_requests  # noqa: E402


def test_every_brazilian_row_gets_exactly_one_request_category():
    courses = [{"id": "dir", "rows": [{"name": "A", "semester": 1}, {"name": "B", "semester": 2}, {"name": "TCC I", "semester": 9}]}]
    programs = {"dir|A": {"status": "lido", "current": False, "documentYear": 2022, "source": "https://x"}}
    out = brazil_requests(courses, programs, contacts={"dir": "x@y"})
    cats = {r["name"]: r["category"] for r in out["dir"]["rows"]}
    assert cats == {"A": "confirmar_vigencia", "B": "solicitar_ementa", "TCC I": "regra_especifica"}
    assert out["dir"]["contact"] == "x@y"


def test_current_official_rows_need_nothing():
    courses = [{"id": "cc", "rows": [{"id": "X1", "name": "Redes", "semester": 4}]}]
    programs = {"cc|X1": {"status": "lido", "current": True, "documentYear": 2025, "source": "https://x", "anomalies": []}}
    out = brazil_requests(courses, programs, contacts={})
    assert out["cc"]["rows"][0]["category"] == "vigente_vinculada"


def test_anomalies_are_surfaced_for_confirmation():
    courses = [{"id": "cc", "rows": [{"id": "X1", "name": "Paradigmas", "semester": 5}]}]
    programs = {"cc|X1": {"status": "lido", "current": True, "source": "https://x", "anomalies": ["Carga incompatível"]}}
    out = brazil_requests(courses, programs, contacts={})
    assert out["cc"]["rows"][0]["category"] == "confirmar_inconsistencia"
