import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { getRepository } from "../lib/data";

test("official home presents interactive globe before direct course destinations", () => {
  const source = readFileSync("app/page.tsx", "utf8");
  assert.match(source, /Seu próximo semestre/);
  assert.match(source, /mais longe/);
  assert.match(source, /<PreviewGlobe/);
  assert.ok(
    source.indexOf("<PreviewGlobe") < source.indexOf('className="course-grid"'),
  );
  assert.match(source, /href=\{`\/disciplinas\?curso=\$\{course.id\}`\}/);
  assert.equal(getRepository().courses.length, 4);
  for (const removed of [
    "stats-strip",
    "ReviewCard",
    "missingPriority",
    "stage-picker",
  ]) {
    assert.ok(!source.includes(removed), `Home must not include ${removed}`);
  }
});

test("official home offers discreet application and study plan links", () => {
  const source = readFileSync("app/page.tsx", "utf8");
  assert.match(source, /href="\/candidatura"/);
  assert.match(source, /href="\/plano"/);
  assert.ok(!source.includes("/teste-".concat("candidatura")));
});
