import { readFile, writeFile } from "node:fs/promises";
import sharp from "sharp";

const svg = await readFile(new URL("../app/icon.svg", import.meta.url));
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
