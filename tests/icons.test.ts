import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
require.extensions[".css"] = (module) => {
  module.exports = {};
};

test("brand icons use font-independent vector geometry and browser-sized ICO entries", () => {
  const svg = readFileSync("app/icon.svg", "utf8");
  assert.match(svg, /viewBox="0 0 64 64"/);
  assert.match(svg, /#15110e/);
  assert.match(svg, /#e63322/);
  assert.doesNotMatch(svg, /<text|<image|https?:\/\/(?!www\.w3\.org)/);
  const ico = readFileSync("app/favicon.ico");
  assert.equal(ico.readUInt16LE(0), 0);
  assert.equal(ico.readUInt16LE(2), 1);
  assert.equal(ico.readUInt16LE(4), 3);
  assert.deepEqual(
    [0, 1, 2].map((index) => ico[6 + 16 * index]),
    [16, 32, 48],
  );
  const apple = readFileSync("app/apple-icon.png");
  assert.equal(apple.readUInt32BE(16), 180);
  assert.equal(apple.readUInt32BE(20), 180);
});

test("root title uses the middle dot and retains a page title template", async () => {
  const { metadata } = await import("../app/layout");
  assert.deepEqual(metadata.title, {
    default: "Fluxo Contínuo · Seu próximo semestre começa aqui",
    template: "%s · Fluxo Contínuo",
  });
});
