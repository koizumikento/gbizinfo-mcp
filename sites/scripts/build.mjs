import assert from "node:assert/strict";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";

const root = new URL("../", import.meta.url);
const manifest = JSON.parse(await readFile(new URL(".openai/hosting.json", root), "utf8"));
assert(manifest.capabilities.includes("mcp"));
assert(!manifest.static, "Worker ESM does not use static.directory");
await mkdir(new URL("dist/server/", root), { recursive: true });
await mkdir(new URL("dist/.openai/", root), { recursive: true });
await build({
  entryPoints: [fileURLToPath(new URL("worker/index.js", root))],
  outfile: fileURLToPath(new URL("dist/server/index.js", root)),
  bundle: true,
  format: "esm",
  platform: "browser",
  conditions: ["workerd", "browser"],
  target: "es2022",
});
await writeFile(new URL("dist/.openai/hosting.json", root), JSON.stringify(manifest, null, 2) + "\n");
const source = await readFile(new URL("dist/server/index.js", root), "utf8");
const worker = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
assert.equal(typeof worker.default.fetch, "function");
console.log("Sites artifact: dist/server/index.js + dist/.openai/hosting.json; ESM fetch verified");
