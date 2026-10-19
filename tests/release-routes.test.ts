import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { renderToStaticMarkup } from "react-dom/server";

const require = createRequire(import.meta.url);
require.extensions[".css"] = (module) => {
  module.exports = {};
};

test("published guide exposes official sources and application form without preview navigation", async () => {
  const { default: Guide, metadata } = await import("../app/candidatura/page");
  const html = renderToStaticMarkup(Guide());
  assert.match(html, /https:\/\/forms.cloud.microsoft\/r\/VMKaSyTrJz/);
  assert.match(html, /IN-RE 110\/2026/);
  assert.match(html, /14\/12\/2026/);
  assert.match(html, /14\/12\/2027/);
  assert.match(html, /href="\/plano"/);
  assert.match(html, /href="\/"/);
  assert.doesNotMatch(html, /teste-|prévia/i);
  assert.doesNotMatch(JSON.stringify(metadata), /false|prévia/i);
});

test("published planner renders the requested course and stage with official navigation", async () => {
  const { default: Planning, generateMetadata } =
    await import("../app/plano/page");
  const page = await Planning({
    searchParams: Promise.resolve({ curso: "cc", etapa: "2" }),
  });
  assert.equal(page.props.initialCourseId, "cc");
  assert.equal(page.props.initialStage, "2");
  const html = renderToStaticMarkup(page);
  assert.match(html, /href="\/candidatura"/);
  assert.match(html, /href="\/"/);
  assert.match(html, /value="2" selected=""/);
  assert.doesNotMatch(html, /teste-|prévia/i);
  assert.doesNotMatch(
    JSON.stringify(
      await generateMetadata({
        searchParams: Promise.resolve({ curso: "cc" }),
      }),
    ),
    /false|prévia|Pr\\u00e9via/i,
  );
  const fallback = await Planning({
    searchParams: Promise.resolve({ curso: "invalid", etapa: "999" }),
  });
  assert.equal(fallback.props.initialStage, "all");
  assert.notEqual(fallback.props.initialCourseId, "invalid");
});
