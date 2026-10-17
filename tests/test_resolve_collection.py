"""Regression specifications for complete public-source collection and resumable history."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import resolve_syllabi as resolver


def fixture_load(monkeypatch):
    courses = [{"universityId": "u", "code": str(i), "name": f"Course {i}", "source": "https://example.edu"} for i in range(4)]
    sources = {
        "data.json": {"foreignCourses": courses},
        "syllabi/records.json": {"foreign": [{"universityId": "u", "foreignCode": "2", "status": "ementa_individual"}]},
        "syllabi/fontes-verificadas.json": {"foreign": [{"universityId": "u", "code": "1", "individualSyllabus": False}, {"universityId": "u", "code": "3", "individualSyllabus": True}]},
        "syllabi/pendencias-documentais.json": {"foreign": [{"universityId": "u", "missingSyllabi": [{"code": "0"}]}]},
    }
    monkeypatch.setattr(resolver, "_load", lambda path: sources[path])
    monkeypatch.setattr(resolver, "VERIFIED", Path(__file__))


def test_default_scope_preserves_priority(monkeypatch):
    fixture_load(monkeypatch)
    assert [x["code"] for x in resolver.targets(None)] == ["0"]


def test_all_missing_includes_unprioritized_and_rejected_sources(monkeypatch):
    fixture_load(monkeypatch)
    assert [x["code"] for x in resolver.targets(None, scope="all-missing")] == ["0", "1"]
    assert resolver.targets("other", scope="all-missing") == []


def test_attempt_history_survives_repeated_runs():
    first = {"verified": False, "checkedAt": "first", "tried": [{"http": 404}]}
    second = {"verified": False, "checkedAt": "second", "tried": [{"http": 503}]}
    third = {"verified": True, "checkedAt": "third", "tried": [{"http": 200}]}
    result = resolver.merge_attempt(resolver.merge_attempt(first, second), third)
    assert [x["checkedAt"] for x in result["history"]] == ["first", "second"]
    assert result["history"][0]["tried"][0]["http"] == 404
    assert result["verified"] is True


def test_resume_is_explicit_and_uses_attempt_timestamp():
    previous = {("u", "0"): {"checkedAt": "2026-10-01T00:00:00Z", "verified": False}}
    todo = [{"universityId": "u", "code": "0"}, {"universityId": "u", "code": "1"}]
    assert resolver.resume_targets(todo, previous, None) == todo
    assert resolver.resume_targets(todo, previous, "2026-10-01T00:00:00Z") == [todo[1]]
