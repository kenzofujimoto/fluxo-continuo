import { test } from "node:test";
import assert from "node:assert/strict";
import { choosePlan, type PlanningOption } from "../lib/planning";
const option = (
  key: string,
  foreign: string[],
  level: "high" | "partial" = "partial",
): PlanningOption => ({
  key,
  universityId: "u",
  foreign,
  level,
  reviewId: key,
  href: "/comparacoes/" + key,
  name: key,
  foreignNames: foreign,
  hours: "Não confirmadas",
  limitations: [],
});
test("single-course alternatives avoid duplicate Brazilian disciplines and foreign reuse", () => {
  const result = choosePlan(
    [
      option("a", ["x", "y"]),
      option("b", ["y"]),
      option("a", ["z"]),
      option("c", ["w"]),
    ],
    ["a", "b", "c"],
  );
  assert.equal(new Set(result.map((x) => x.key)).size, result.length);
  assert.equal(
    new Set(result.flatMap((x) => x.foreign)).size,
    result.flatMap((x) => x.foreign).length,
  );
  assert.equal(result.length, 3);
});
test("selection excludes stale disciplines and prioritizes high affinity", () => {
  const result = choosePlan(
    [option("a", ["x"]), option("b", ["x"], "high"), option("c", ["y"])],
    ["a", "b"],
  );
  assert.deepEqual(
    result.map((x) => x.key),
    ["b"],
  );
  assert.deepEqual(choosePlan([option("a", ["x"])], []), []);
});

test("augmenting path improves a greedy assignment", () => {
  const result = choosePlan(
    [option("a", ["x"], "high"), option("a", ["y"]), option("b", ["x"])],
    ["a", "b"],
  );
  assert.equal(result.length, 2);
});
test("bundles are excluded, never partially consumed", () => {
  assert.deepEqual(choosePlan([option("a", ["x", "y"])], ["a"]), []);
});
import { buildPlanningOptions } from "../lib/planning";
import { comparisonPath, getRepository } from "../lib/data";
test("real transformation excludes undocumented, low, ineligible and outside-agreement reviews", () => {
  const repo = getRepository();
  const available = buildPlanningOptions(repo, comparisonPath);
  assert.ok(available.length > 0);
  for (const item of available) {
    const review = repo.reviews.find((review) => review.id === item.reviewId)!;
    assert.ok(
      ["alta_afinidade", "afinidade_parcial"].includes(review.conclusionClass),
    );
    assert.ok(
      review.brazil.sha256 && review.foreign.every((item) => item.sha256),
    );
    assert.ok(
      repo.universities.find(
        (university) => university.id === item.universityId,
      )?.courses[review.brazil.courseId],
    );
  }
  const review = repo.reviews.find(
    (review) => review.id === available[0].reviewId,
  )!;
  const isolated = { ...repo, reviews: [review] };
  assert.equal(
    buildPlanningOptions(
      {
        ...isolated,
        reviews: [{ ...review, conclusionClass: "baixa_afinidade" }],
      },
      comparisonPath,
    ).length,
    0,
  );
  assert.equal(
    buildPlanningOptions(
      {
        ...isolated,
        reviews: [{ ...review, brazil: { ...review.brazil, sha256: null } }],
      },
      comparisonPath,
    ).length,
    0,
  );
  assert.equal(
    buildPlanningOptions({ ...isolated, universities: [] }, comparisonPath)
      .length,
    0,
  );
  assert.equal(
    buildPlanningOptions(
      {
        ...isolated,
        foreignCourses: [
          {
            universityId: review.foreign[0].universityId,
            code: review.foreign[0].code,
            name: "x",
            source: "https://example.org",
            sourceEligibility: "outside_agreement",
          },
        ],
      },
      comparisonPath,
    ).length,
    0,
  );
  for (const university of repo.universities) {
    const plan = choosePlan(
      available.filter((item) => item.universityId === university.id),
      available.map((item) => item.key),
    );
    assert.equal(new Set(plan.map((item) => item.key)).size, plan.length);
    assert.equal(
      new Set(plan.flatMap((item) => item.foreign)).size,
      plan.length,
    );
  }
});

test("planner page validates incoming course and stage before initializing client selection", async () => {
  const { createRequire } = await import("node:module");
  const require = createRequire(import.meta.url);
  require.extensions[".css"] = (module) => {
    module.exports = {};
  };
  const { default: Page, metadata } = await import("../app/teste-plano/page");
  const element = await Page({
    searchParams: Promise.resolve({ curso: "dir", etapa: "10" }),
  });
  assert.equal(element.props.initialCourseId, "dir");
  assert.equal(element.props.initialStage, "10");
  assert.equal(element.key, "dir:10");
  const { renderToStaticMarkup } = await import("react-dom/server");
  const html = renderToStaticMarkup(element);
  assert.match(html, /value="dir" selected=""/);
  assert.match(html, /value="10" selected=""/);
  assert.doesNotMatch(html, /<main/);

  const invalid = await Page({
    searchParams: Promise.resolve({ curso: "unknown", etapa: "999" }),
  });
  assert.equal(invalid.props.initialCourseId, getRepository().courses[0].id);
  assert.equal(invalid.props.initialStage, "all");
  const wrongStage = await Page({
    searchParams: Promise.resolve({ curso: "cc", etapa: "10" }),
  });
  assert.equal(wrongStage.props.initialStage, "all");
  assert.deepEqual(metadata.robots, { index: false, follow: false });
});
