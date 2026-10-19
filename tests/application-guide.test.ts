import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";

test("application preview preserves official sources and conflicting deadlines", () => {
  const page = readFileSync("app/teste-candidatura/page.tsx", "utf8");
  assert.match(page, /VMKaSyTrJz/);
  assert.match(page, /14\/12\/2026/);
  assert.match(page, /14\/12\/2027/);
  assert.match(page, /20%/);
  assert.match(page, /90%/);
  assert.match(page, /B2/);
  assert.match(page, /#page=15/);
  assert.match(page, /robots: \{ index: false, follow: false \}/);
});

test("checklist is local and does not collect documents", () => {
  const checklist = readFileSync("app/teste-candidatura/checklist.tsx", "utf8");
  assert.match(checklist, /type="checkbox"/);
  assert.match(checklist, /aria-live="polite"/);
  assert.doesNotMatch(checklist, /type="file"|fetch\(|localStorage/);
});
