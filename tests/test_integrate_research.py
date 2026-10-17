"""Specs for integrating public-research discoveries only after independent re-verification."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from integrate_research import collect_candidates, reverify  # noqa: E402

PAGE = "Writing and Presentation Skills\nCourse Code COM114D\nCourse Content\n" + "texto " * 300


def test_collect_skips_quarantined_rejected_unknown_and_already_verified():
    ledgers = {
        "solbridge": {"foreign": [{"universityId": "kr", "code": "COM114D", "source": "https://a/x.pdf", "individualSyllabus": True},
                                  {"universityId": "kr", "code": "BUS405", "source": "https://a/y.pdf", "individualSyllabus": True}],
                      "quarantined": [{"code": "BUS405", "reason": "declares BUS202"}]},
        "europe": {"foreign": [{"universityId": "es", "code": "1", "source": "https://b", "individualSyllabus": True},
                               {"universityId": "es", "code": "2", "source": "https://c", "individualSyllabus": True},
                               {"universityId": "es", "code": "3", "source": "https://d", "individualSyllabus": False}],
                   "rejectedCandidates": [{"universityId": "es", "code": "2"}]},
        "asia": {"foreign": [{"universityId": "kr", "code": "ZZ9", "source": "https://e", "status": "verified", "individualSyllabus": True}]},
    }
    catalogue = {("kr", "COM114D"), ("kr", "BUS405"), ("es", "1"), ("es", "2"), ("es", "3")}
    out, skipped = collect_candidates(ledgers, catalogue, already_verified={("es", "1")})
    assert [(c["universityId"], c["code"]) for c in out] == [("kr", "COM114D")]
    reasons = {(s["code"]): s["reason"] for s in skipped}
    assert "quarentena" in reasons["BUS405"] and "rejeitado" in reasons["2"]
    assert "catálogo" in reasons["ZZ9"] and "já verificado" in reasons["1"]


def test_reverify_uses_our_catalogue_name_and_rejects_failures():
    cand = {"universityId": "kr", "code": "COM114D", "source": "https://a/x.pdf", "ledger": "solbridge"}
    ok = reverify(cand, "Writing and Presentation Skills", [], fetch=lambda url: ({"http": 200, "finalUrl": url, "sha256": "h", "format": "pdf"}, PAGE))
    assert ok["ok"] and ok["entry"]["code"] == "COM114D" and "reverificad" in ok["entry"]["method"]
    bad = reverify(cand, "Corporate Finance", [], fetch=lambda url: ({"http": 200, "finalUrl": url}, PAGE))
    assert not bad["ok"]
    down = reverify(cand, "Writing and Presentation Skills", [], fetch=lambda url: ({"http": 503, "finalUrl": url}, ""))
    assert not down["ok"] and "503" in down["reason"]
