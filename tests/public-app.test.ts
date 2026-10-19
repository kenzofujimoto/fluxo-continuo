import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { filterDestinations, parseLocations } from "../lib/locations";

test("destination filters distinguish eligibility from course selection and normalize accents", () => {
  const universities = getRepository().universities;
  assert.equal(
    filterDestinations(universities, { q: "zz-no-result" }).length,
    0,
  );
  assert.deepEqual(
    filterDestinations(universities, { course: "cc", eligible: true }),
    universities.filter((u) => u.courses.cc),
  );
  assert.equal(
    filterDestinations(universities, { course: "cc", eligible: false }).length,
    universities.length,
  );
  assert.deepEqual(
    filterDestinations(universities, { eligible: true }),
    universities.filter((u) => Object.values(u.courses).some(Boolean)),
  );
  assert.deepEqual(
    filterDestinations(universities, { q: "espanha" }),
    universities.filter((u) => u.country === "Espanha"),
  );
});

test("map locations reject unsafe sources and out-of-range coordinates", () => {
  const origin = {
    name: "Origin",
    city: "City",
    lat: 0,
    lng: 0,
    precision: "city",
    source: "https://example.org",
    verifiedAt: "2026-10-16",
  };
  assert.throws(() =>
    parseLocations({ origin: { ...origin, lat: 91 }, universities: [] }),
  );
  assert.throws(() =>
    parseLocations({
      origin,
      universities: [
        { ...origin, universityId: "test", source: "javascript:alert(1)" },
      ],
    }),
  );
  assert.throws(() =>
    parseLocations({
      origin,
      universities: [
        { ...origin, universityId: "test" },
        { ...origin, universityId: "test" },
      ],
    }),
  );
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

test("public syllabus and university tables expose course limitations and agreement exclusions", async () => {
  const { renderToStaticMarkup } = await import("react-dom/server");
  const { default: Syllabi } = await import("../app/ementas/page");
  const { default: UniversityDetail } =
    await import("../app/universidades/[id]/page");
  const repository = getRepository();
  const original = repository.foreignCourses[0];
  const sentinel = "Scope limitation regression sentinel";
  repository.foreignCourses.push({
    ...original,
    code: "SCOPE-REGRESSION",
    name: sentinel,
    limitations: "Only another faculty; mobility access unconfirmed.",
    sourceEligibility: "outside_agreement",
  });
  try {
    const library = renderToStaticMarkup(
      await Syllabi({
        searchParams: Promise.resolve({ origem: "exterior", q: sentinel }),
      }),
    );
    const university = renderToStaticMarkup(
      await UniversityDetail({
        params: Promise.resolve({ id: original.universityId }),
        searchParams: Promise.resolve({ q: sentinel }),
      }),
    );
    for (const html of [library, university]) {
      assert.match(html, /Only another faculty; mobility access unconfirmed\./);
      assert.match(html, /Fora do escopo do acordo/);
    }
  } finally {
    repository.foreignCourses.pop();
  }
});

test("local flag comparison preserves country color roles in all 21 preview assets", () => {
  const codes = [
    ...new Set(
      getRepository().universities.map((item) => item.flag.toLowerCase()),
    ),
  ];
  assert.equal(codes.length, 21);
  for (const code of codes) {
    const original = readFileSync(`public/flags/${code}.svg`, "utf8");
    const preview = readFileSync(`public/flags-preview/${code}.svg`, "utf8");
    assert.equal(
      (preview.match(/<path\b/g) ?? []).length,
      (original.match(/<path\b/g) ?? []).length,
    );
    assert.doesNotMatch(
      preview,
      /<filter\b|<image\b|https?:\/\/(?!www\.w3\.org)/,
    );
    for (const [, color] of preview.matchAll(/(?:fill|stroke)="([^"]+)"/g)) {
      assert.ok(
        ["none", "#15110e", "#e63322", "#f1ece3"].includes(color) ||
          /^url\(#[a-z0-9-]+\)$/.test(color),
        `${code}: ${color}`,
      );
    }
  }
  for (const code of ["de", "it", "fr", "ie", "in"]) {
    const svg = readFileSync(`public/flags-preview/${code}.svg`, "utf8");
    for (const color of ["#15110e", "#e63322", "#f1ece3"])
      assert.ok(svg.includes(color), `${code}: ${color}`);
  }
  for (const code of ["ar", "uy"])
    assert.match(
      readFileSync(`public/flags-preview/${code}.svg`, "utf8"),
      /fill="#e63322"/,
    );
  const page = readFileSync("app/teste-bandeiras/page.tsx", "utf8");
  assert.match(page, /flags-preview/);
  assert.doesNotMatch(page, /CountryFlag|dangerouslySetInnerHTML/);
});

test("country flags preserve original asset colors without duotone filters", () => {
  const component = readFileSync("app/country-flag.tsx", "utf8");
  assert.doesNotMatch(component, /<filter|feColorMatrix|feComponentTransfer|filter=/);
  assert.match(component, /\/flags\/\$\{normalizedCode\}\.svg/);
  assert.match(component, /availableFlags\.has\(normalizedCode\)/);
});
