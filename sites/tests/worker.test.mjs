import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { test, mock } from "node:test";
import { fileURLToPath } from "node:url";
import { Client, StreamableHTTPClientTransport } from "@modelcontextprotocol/client";
import { Miniflare, convertV4MiniflareOptions } from "miniflare";

const source = await readFile(new URL("../dist/server/index.js", import.meta.url), "utf8");
const { default: worker } = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
const contract = JSON.parse(await readFile(new URL("../worker/contract.json", import.meta.url), "utf8"));
const fixtureRun = spawnSync("uv", ["run", "--project", "..", "python", "tests/export_fixtures.py"], { encoding: "utf8" });
assert.equal(fixtureRun.status, 0, fixtureRun.stderr);
const fixtures = JSON.parse(fixtureRun.stdout);
const env = { GBIZINFO_API_TOKEN: "synthetic-runtime-secret" };
let id = 0;
function request(method, params = {}, extraHeaders = {}, modern = false) {
  if (modern) params = { ...params, _meta: {
    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
    "io.modelcontextprotocol/clientInfo": { name: "fixture", version: "1" },
    "io.modelcontextprotocol/clientCapabilities": {},
  } };
  return new Request("https://fixture.test/mcp", {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json, text/event-stream",
      "oai-authenticated-user-id": "synthetic-site-user", ...(modern ? {
        "MCP-Protocol-Version": "2026-07-28", "Mcp-Method": method,
        ...(params.name ? { "Mcp-Name": params.name } : {}),
      } : {}), ...extraHeaders },
    body: JSON.stringify({ jsonrpc: "2.0", id: ++id, method, params }),
  });
}
async function rpc(method, params, secrets = env, modern = false) {
  const response = await worker.fetch(request(method, params, {}, modern), secrets);
  assert.equal(response.status, 200, await response.clone().text());
  if (response.headers.get("content-type").includes("text/event-stream")) {
    const data = (await response.text()).split("\n").filter((line) => line.startsWith("data: "));
    return JSON.parse(data.at(-1).slice(6));
  }
  return response.json();
}

test("stateless legacy initialization, discovery and modern discovery", async () => {
  const init = await rpc("initialize", { protocolVersion: "2025-11-25", capabilities: {}, clientInfo: { name: "fixture", version: "1" } });
  assert.equal(init.result.serverInfo.name, "gbizinfo-mcp");
  const discovered = await rpc("tools/list", {});
  assert.deepEqual(discovered.result.tools, contract.tools);
  assert.equal(discovered.result.tools.length, 19);
  assert.equal((await rpc("server/discover", {}, env, true)).result._meta["io.modelcontextprotocol/serverInfo"].name, "gbizinfo-mcp");
  assert.deepEqual((await rpc("tools/list", {}, env, true)).result.tools, contract.tools);
  assert.equal((await rpc("ping", {})).result && true, true);
});

test("authentication, origin, routing and malformed protocol fail closed", async () => {
  let req = request("tools/call", { name: "hojin_search" });
  req.headers.delete("oai-authenticated-user-id");
  assert.equal((await worker.fetch(req, env)).status, 401);
  req.headers.set("OAI-Sites-Authorization", "Bearer synthetic-service-access");
  assert.equal((await worker.fetch(req, env)).status, 401);
  assert.equal((await worker.fetch(request("tools/list", {}, { origin: "https://evil.test" }), env)).status, 403);
  assert.equal((await worker.fetch(request("tools/list", {}, { origin: "null" }), env)).status, 403);
  assert.equal((await worker.fetch(new Request("https://fixture.test/other"), env)).status, 404);
  assert.equal((await worker.fetch(new Request("https://fixture.test/mcp", { headers: { "oai-authenticated-user-id": "fixture" } }), env)).status, 405);
  req = request("tools/list");
  const badJson = new Request(req.url, { method: "POST", headers: req.headers, body: "{" });
  assert.equal((await worker.fetch(badJson, env)).status, 400);
  const unknown = await rpc("tools/call", { name: "__proto__", arguments: {} });
  assert.equal(unknown.error.code, -32602);
});

test("all 19 tools preserve Python path/query and upstream JSON including paging/provenance", async () => {
  const calls = [];
  const payload = { "hojin-infos": [{ name: "架空法人", source: "synthetic fixture" }], page: 2, total: 5001, metadata: { provenance: "fixture-v1" } };
  mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(init.headers["X-hojinInfo-api-token"], env.GBIZINFO_API_TOKEN);
    assert.equal(init.redirect, "manual");
    assert.equal(url.origin, "https://api.info.gbiz.go.jp");
    calls.push({ path: url.pathname.slice("/hojin".length), query: Object.fromEntries(url.searchParams) });
    return Response.json(payload);
  });
  try {
    for (const fixture of fixtures.filter((f) => !f.invalid)) {
      const result = (await rpc("tools/call", { name: fixture.name, arguments: fixture.args })).result;
      assert.equal(result.isError, false);
      assert.deepEqual(result.structuredContent, payload);
      assert.deepEqual(JSON.parse(result.content[0].text), payload);
      assert.deepEqual(calls.at(-1), fixture.expected);
    }
    const modern = (await rpc("tools/call", { name: "hojin_search", arguments: {} }, env, true)).result;
    assert.deepEqual(modern.structuredContent, payload);
  } finally { mock.restoreAll(); }
});

test("Python domain-invalid and schema-invalid arguments never reach upstream", async () => {
  mock.method(globalThis, "fetch", () => { throw new Error("must not call upstream"); });
  try {
    for (const fixture of fixtures.filter((f) => f.invalid)) {
      assert.equal((await rpc("tools/call", { name: fixture.name, arguments: fixture.args })).result.isError, true);
    }
    for (const args of [{ corporate_number: null }, {}, { corporate_number: 1234567890123 }, { corporate_number: "1234567890123", url: "https://evil.test" }]) {
      assert.equal((await rpc("tools/call", { name: "hojin_get_basic", arguments: args })).result.isError, true);
    }
    for (const args of [{ page: 1.2 }, { page: true }, { limit: "3" }, { metadata_flg: 1 }]) {
      assert.equal((await rpc("tools/call", { name: "hojin_search", arguments: args })).result.isError, true);
    }
    assert.equal(globalThis.fetch.mock.callCount(), 0);
  } finally { mock.restoreAll(); }
});

test("429/5xx retry budget and sanitized terminal errors", async () => {
  let count = 0;
  mock.method(globalThis, "fetch", async () => {
    count++;
    return count < 3 ? Response.json({ message: env.GBIZINFO_API_TOKEN }, { status: count === 1 ? 503 : 429 }) : Response.json({ ok: true });
  });
  try {
    assert.deepEqual((await rpc("tools/call", { name: "hojin_search" })).result.structuredContent, { ok: true });
    assert.equal(count, 3);
  } finally { mock.restoreAll(); }
  for (const status of [400, 401, 403, 404, 429, 500, 502, 503, 504, 302]) {
    mock.method(globalThis, "fetch", async () => Response.json({ message: env.GBIZINFO_API_TOKEN }, { status }));
    try {
      const result = (await rpc("tools/call", { name: "hojin_search" })).result;
      assert.equal(result.isError, true);
      assert.match(result.content[0].text, new RegExp(`\\(${status}\\)`));
      assert(!JSON.stringify(result).includes(env.GBIZINFO_API_TOKEN));
      assert.equal(globalThis.fetch.mock.callCount(), contract.retryableStatuses.includes(status) ? 3 : 1);
    } finally { mock.restoreAll(); }
  }
});

test("missing secret, network timeout and invalid response are tool errors", async () => {
  assert.equal((await rpc("tools/call", { name: "hojin_search" }, {})).result.isError, true);
  for (const response of [() => new Response("not JSON"), () => Response.json([]), () => Response.json(null),
    () => { throw new Error(env.GBIZINFO_API_TOKEN); },
    () => { throw new TypeError(env.GBIZINFO_API_TOKEN); },
    () => { throw new DOMException(env.GBIZINFO_API_TOKEN, "TimeoutError"); }]) {
    mock.method(globalThis, "fetch", response);
    try {
      const result = (await rpc("tools/call", { name: "hojin_search" })).result;
      assert.equal(result.isError, true);
      assert(!JSON.stringify(result).includes(env.GBIZINFO_API_TOKEN));
    } finally { mock.restoreAll(); }
  }
});

test("official SDK clients discover and call in both protocol eras", async () => {
  mock.method(globalThis, "fetch", async () => Response.json({ "hojin-infos": [], metadata: { source: "synthetic" } }));
  try {
    for (const mode of ["legacy", { pin: "2026-07-28" }]) {
      const client = new Client({ name: "gbizinfo-contract-test", version: "1" }, { versionNegotiation: { mode } });
      const transport = new StreamableHTTPClientTransport(new URL("https://fixture.test/mcp"), {
        fetch: (url, init) => {
          const req = new Request(url, init);
          req.headers.set("oai-authenticated-user-id", "synthetic-site-user");
          return worker.fetch(req, env);
        },
      });
      try {
        await client.connect(transport);
        assert.equal((await client.listTools()).tools.length, 19);
        const result = await client.callTool({ name: "hojin_get_basic", arguments: { corporate_number: "1234567890123" } });
        assert.equal(result.isError, false);
        assert.deepEqual(result.structuredContent, { "hojin-infos": [], metadata: { source: "synthetic" } });
      } finally { await client.close(); }
    }
  } finally { mock.restoreAll(); }
});

test("isolated workerd executes the artifact and preserves int64 on the wire", { timeout: 30000 }, async () => {
  const prefix = fileURLToPath(new URL("../.runtime-test-", import.meta.url));
  const temporary = await mkdtemp(prefix);
  const payload = '{"capital_stock":9007199254740993,"finance":[{"amount":9223372036854775807}],"metadata":{"source":"synthetic"}}';
  let calls = 0;
  let mf;
  try {
    mf = new Miniflare(convertV4MiniflareOptions({
      rootPath: temporary,
      script: source,
      modules: true,
      compatibilityDate: "2026-10-06",
      bindings: env,
      host: "127.0.0.1",
      port: 0,
      cf: false,
      outboundService: async (req) => {
        assert.equal(new URL(req.url).origin, "https://api.info.gbiz.go.jp");
        assert.equal(req.headers.get("X-hojinInfo-api-token"), env.GBIZINFO_API_TOKEN);
        calls++;
        return new Response(payload, { headers: { "content-type": "application/json" } });
      },
    }));
    for (const modern of [false, true]) {
      const req = request("tools/call", { name: "hojin_get_finance", arguments: { corporate_number: "1234567890123" } }, {}, modern);
      const response = await mf.dispatchFetch(req.url, { method: req.method, headers: req.headers, body: await req.text() });
      assert.equal(response.status, 200);
      const wire = await response.text();
      assert(wire.includes(`"structuredContent":${payload}`), wire);
      const message = modern ? JSON.parse(wire) : JSON.parse(wire.split("\n").find((line) => line.startsWith("data: ")).slice(6));
      assert.equal(message.result.isError, false);
      assert.equal(message.result.content[0].text, payload);
    }
    assert.equal(calls, 2);
    const denied = await mf.dispatchFetch("https://fixture.test/mcp", { method: "POST", body: "{}" });
    assert.equal(denied.status, 401);
  } finally {
    await mf?.dispose();
    assert(temporary.startsWith(prefix));
    await rm(temporary, { recursive: true, force: true });
  }
});
