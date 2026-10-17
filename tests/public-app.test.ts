import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { filterDestinations, parseLocations } from "../lib/locations";

test("destination filters distinguish eligibility from course selection and normalize accents", () => {
  const universities = getRepository().universities;
  assert.equal(filterDestinations(universities, { q: "zz-no-result" }).length, 0);
  assert.deepEqual(filterDestinations(universities, { course: "cc", eligible: true }), universities.filter(u => u.courses.cc));
  assert.equal(filterDestinations(universities, { course: "cc", eligible: false }).length, universities.length);
  assert.equal(filterDestinations(universities, { eligible: true }).length, universities.length);
  assert.deepEqual(filterDestinations(universities, { q: "espanha" }), universities.filter(u => u.country === "Espanha"));
});

test("map locations reject unsafe sources and out-of-range coordinates", () => {
  const origin = { name: "Origin", city: "City", lat: 0, lng: 0, precision: "city", source: "https://example.org", verifiedAt: "2026-10-16" };
  assert.throws(() => parseLocations({ origin: { ...origin, lat: 91 }, universities: [] }));
  assert.throws(() => parseLocations({ origin, universities: [{ ...origin, universityId: "test", source: "javascript:alert(1)" }] }));
  assert.throws(() => parseLocations({ origin, universities: [{ ...origin, universityId: "test" }, { ...origin, universityId: "test" }] }));
});
import {
  getRepository,
  getDiscipline,
  getComparison,
  searchDisciplines,
  parseDataset,
  safeSource,
  comparisonId,
} from "../lib/data";

test("public counts are computed from versioned source records", () => {
  const repository = getRepository();
  const raw = JSON.parse(readFileSync("data.json", "utf8"));
  assert.equal(repository.stats.universities, raw.universities.length);
  assert.equal(
    repository.stats.disciplines,
    raw.courses.reduce(
      (sum: number, course: { rows: unknown[] }) => sum + course.rows.length,
      0,
    ),
  );
  assert.equal(repository.stats.foreignCourses, raw.foreignCourses.length);
  assert.equal(repository.stats.reviews, repository.reviews.length);
  assert.equal(
    repository.stats.homologated,
    repository.reviews.filter(
      (review) => review.institutionalStatus === "homologado",
    ).length,
  );
});

test("discipline identity includes degree and supports names without codes", () => {
  const repository = getRepository();
  for (const course of repository.courses)
    for (const row of course.rows) {
      const discipline = getDiscipline(course.id, row.id ?? row.name);
      assert.equal(discipline?.row.name, row.name);
    }
  assert.equal(getDiscipline("missing", "missing"), undefined);
});

test("search ignores accents and filters degree", () => {
  assert.ok(searchDisciplines("computacao", "cc").length > 0);
  assert.equal(searchDisciplines("computacao", "adm").length, 0);
  assert.equal(searchDisciplines("nonexistent-unfindable").length, 0);
});

test("every candidate relation resolves its Brazilian discipline", () => {
  for (const candidate of getRepository().matches) {
    assert.ok(
      getDiscipline(candidate.courseId, candidate.mackCode),
      `Unresolved candidate: ${candidate.courseId}|${candidate.mackCode}`,
    );
  }
});

test("encoded route parameters resolve named disciplines and malformed encodings return missing", () => {
  const name = "Administração Estratégica e Sustentabilidade";
  assert.equal(getDiscipline("adm", encodeURIComponent(name))?.row.name, name);
  assert.equal(getDiscipline("adm", "%E0%A4%A"), undefined);
});

test("comparison URLs resolve exact evidence and preserve hour uncertainty", () => {
  const repository = getRepository();
  for (const review of repository.reviews) {
    const resolved = getComparison(comparisonId(review.id));
    assert.equal(resolved?.id, review.id);
    assert.deepEqual(resolved?.hoursComparison, review.hoursComparison);
    assert.deepEqual(resolved?.topics, review.topics);
  }
  assert.equal(getComparison("unknown"), undefined);
});

test("invalid datasets fail visibly and unsafe source protocols are rejected", () => {
  assert.throws(() => parseDataset({ courses: [], universities: [{ id: 2 }] }));
  assert.equal(safeSource("javascript:alert(1)"), undefined);
  assert.equal(safeSource("file:///secret"), undefined);
  assert.equal(
    safeSource("https://www.mackenzie.br/"),
    "https://www.mackenzie.br/",
  );
});
