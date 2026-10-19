import { readFile, writeFile } from "node:fs/promises";
import sharp from "sharp";
import { createRequire } from "node:module";
import { geoOrthographic, geoPath } from "d3-geo";
import { feature } from "topojson-client";

const require = createRequire(import.meta.url);
// Natural Earth public-domain coastlines, distributed by world-atlas.
const topology = JSON.parse(
  await readFile(require.resolve("world-atlas/land-110m.json"), "utf8"),
);
const projection = geoOrthographic()
  .translate([32, 32])
  .scale(25)
  .rotate([28, -8])
  .precision(0.1);
const land = geoPath(projection).digits(1)(
  feature(topology, topology.objects.land),
);
const svg =
  Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#15110e"/>
  <circle cx="32" cy="32" r="25" fill="#f1ece3"/>
  <path id="continents" d="${land}" fill="#e63322"/>
</svg>\n`);
await writeFile(new URL("../app/icon.svg", import.meta.url), svg);
await writeFile(new URL("../public/brand.svg", import.meta.url), svg);
const sizes = [16, 32, 48];
const images = await Promise.all(
  sizes.map((size) => sharp(svg).resize(size, size).png().toBuffer()),
);
const directory = Buffer.alloc(6 + sizes.length * 16);
directory.writeUInt16LE(1, 2);
directory.writeUInt16LE(sizes.length, 4);
let offset = directory.length;
images.forEach((data, index) => {
  const entry = 6 + index * 16;
  directory[entry] = sizes[index];
  directory[entry + 1] = sizes[index];
  directory.writeUInt16LE(1, entry + 4);
  directory.writeUInt16LE(32, entry + 6);
  directory.writeUInt32LE(data.length, entry + 8);
  directory.writeUInt32LE(offset, entry + 12);
  offset += data.length;
});
await writeFile(
  new URL("../app/favicon.ico", import.meta.url),
  Buffer.concat([directory, ...images]),
);
await writeFile(
  new URL("../app/apple-icon.png", import.meta.url),
  await sharp(svg).resize(180, 180).png().toBuffer(),
);
