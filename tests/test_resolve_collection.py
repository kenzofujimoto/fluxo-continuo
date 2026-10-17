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


def test_shared_fetch_cache_fetches_exact_url_only_once(monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Lock
    import time

    calls = []
    lock = Lock()

    def fetch(url):
        with lock:
            calls.append(url)
        time.sleep(0.02)
        return {"http": 503, "finalUrl": url, "_html": "temporary"}, ""

    monkeypatch.setattr(resolver, "fetch_text", fetch)
    cache = resolver.FetchCache()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(cache.fetch, ["https://example.edu/list"] * 16))
    assert calls == ["https://example.edu/list"]
    assert all(result == results[0] for result in results)
    cache.fetch("https://example.edu/list?year=2025")
    assert len(calls) == 2


def test_resolve_uses_shared_cache_but_verifies_each_course(monkeypatch):
    calls = []
    monkeypatch.setattr(resolver, "fetch_text", lambda url: (calls.append(url) or {"http": 200, "finalUrl": url}, "contents " * 200))
    monkeypatch.setattr(resolver, "verify_programme", lambda text, title, code, others, source_url=None: {"ok": code == "yes", "reason": "course-specific"})
    cache = resolver.FetchCache()
    target = {"universityId": "u", "name": "Course", "source": "https://example.edu", "titles": []}
    assert resolver.resolve({**target, "code": "yes"}, cache)["ok"] is True
    assert resolver.resolve({**target, "code": "no"}, cache)["ok"] is False
    assert calls == ["https://example.edu"]
