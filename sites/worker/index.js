import { Server, createMcpHandler, ProtocolError, ProtocolErrorCode, originValidationResponse } from "@modelcontextprotocol/server";
import contract from "./contract.json";

const tools = new Map(contract.tools.map((tool) => [tool.name, tool]));
const failure = (message) => ({ content: [{ type: "text", text: message }], isError: true });

function validateArguments(tool, args) {
  if (!args || typeof args !== "object" || Array.isArray(args)) throw new Error("arguments must be an object");
  const schema = tool.inputSchema;
  for (const key of schema.required ?? []) {
    if (!(key in args)) throw new Error(`${key} is required`);
  }
  for (const [key, value] of Object.entries(args)) {
    const property = schema.properties[key];
    if (!Object.hasOwn(schema.properties, key)) throw new Error(`Unknown argument: ${key}`);
    const types = (property.anyOf ?? [property]).map((item) => item.type);
    const type = value === null ? "null" : typeof value;
    if (!(types.includes(type) || (types.includes("integer") && Number.isSafeInteger(value)))) {
      throw new Error(`${key} has an invalid type`);
    }
  }
  if (args.corporate_number != null && !/^\p{Decimal_Number}{13}$/u.test(args.corporate_number)) {
    throw new Error("corporate_number must be a 13-digit string");
  }
  if (args.page != null && args.page < 1) throw new Error("page must be greater than or equal to 1");
  if (args.limit != null && !(args.limit >= 0 && args.limit <= 5000)) throw new Error("limit must be between 0 and 5000");
  for (const key of ["from_date", "to_date"]) {
    if (!(key in args)) continue;
    const value = args[key];
    if (!/^[0-9]{8}$/.test(value)) throw new Error(`${key} must be in yyyyMMdd format`);
    const year = Number(value.slice(0, 4)), month = Number(value.slice(4, 6)), day = Number(value.slice(6));
    const date = new Date(`${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6)}T00:00:00Z`);
    if (year < 1 || date.getUTCFullYear() !== year || date.getUTCMonth() + 1 !== month || date.getUTCDate() !== day) {
      throw new Error(`${key} must be a valid date in yyyyMMdd format`);
    }
  }
  if (args.from_date > args.to_date) throw new Error("from_date must be less than or equal to to_date");
  const query = { ...args };
  if (args.prefecture != null) {
    const raw = args.prefecture.normalize("NFKC").trim();
    if (!raw) throw new Error("prefecture must not be empty");
    query.prefecture = raw.split(",").map((part) => {
      const token = part.trim();
      if (!token) throw new Error("prefecture must not contain empty values");
      if (/^\p{Decimal_Number}+$/u.test(token)) {
        const length = Array.from(token).length;
        if (length > 2) throw new Error("prefecture code must be 1 or 2 digits");
        return length === 1 ? `0${token}` : token;
      }
      if (Object.hasOwn(contract.prefectures, token)) return contract.prefectures[token];
      throw new Error("prefecture must be a 1-2 digit code or Japanese prefecture name (e.g. '13' or '東京都')");
    }).join(",");
  }
  return query;
}

async function callTool(name, args, env, signal, capturePayload) {
  const tool = tools.get(name);
  if (!tool) throw new ProtocolError(ProtocolErrorCode.InvalidParams, `Unknown tool: ${name}`);
  let query;
  try { query = validateArguments(tool, args); }
  catch (error) { return failure(error.message); }
  try {
    if (!env.GBIZINFO_API_TOKEN) return failure("GBIZINFO_API_TOKEN is required; configure the Site runtime secret");
    const route = contract.routes[name];
    const url = new URL(contract.baseUrl + route.path.replace("{corporate_number}", encodeURIComponent(query.corporate_number)));
    for (const [key, value] of Object.entries(query)) {
      if (value == null || (route.kind === "get" && key === "corporate_number")) continue;
      url.searchParams.set(key === "from_date" ? "from" : key === "to_date" ? "to" : key, String(value));
    }
    for (let attempt = 0; ; attempt++) {
      const response = await fetch(url, {
        headers: { "X-hojinInfo-api-token": env.GBIZINFO_API_TOKEN },
        redirect: "manual",
        signal: AbortSignal.any([signal, AbortSignal.timeout(contract.timeoutSeconds * 1000)]),
      });
      if (contract.retryableStatuses.includes(response.status) && attempt < contract.maxRetries) {
        await response.body?.cancel();
        await new Promise((resolve) => setTimeout(resolve, 250 * 2 ** attempt));
        continue;
      }
      if (!response.ok) {
        await response.body?.cancel();
        // Never reflect an upstream error body: it can contain the API token or request details.
        return failure(`gBizINFO API request failed (${response.status}): HTTP error; check parameters/token or retry later`);
      }
      const rawPayload = await response.text();
      let payload;
      try { payload = JSON.parse(rawPayload); }
      catch { return failure(`gBizINFO API request failed (${response.status}): Response body is not valid JSON`); }
      if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
        return failure(`gBizINFO API request failed (${response.status}): Response JSON root must be an object`);
      }
      capturePayload(rawPayload);
      return { content: [{ type: "text", text: rawPayload }], structuredContent: payload, isError: false };
    }
  } catch {
    return failure("gBizINFO API request failed: network/timeout; retry later");
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== "/mcp") return new Response("Not found", { status: 404 });
    // Identity headers are trusted only behind Sites Dispatch; do not expose this Worker directly.
    if (!request.headers.get("oai-authenticated-user-id")) return new Response("Site user identity required", { status: 401 });
    const originError = originValidationResponse(request, [url.hostname]);
    if (originError) return originError;
    let rawPayload;
    const handler = createMcpHandler(() => {
      const server = new Server({ name: "gbizinfo-mcp", version: contract.version }, { capabilities: { tools: {} } });
      server.setRequestHandler("tools/list", async () => ({ tools: contract.tools }));
      server.setRequestHandler("tools/call", async ({ params }, ctx) => {
        const result = await callTool(params.name, params.arguments ?? {}, env, ctx.mcpReq.signal, (text) => { rawPayload = text; });
        return server.projectCallToolResult(result, tools.get(params.name)?.outputSchema);
      });
      return server;
    });
    try {
      const response = await handler.fetch(request);
      const body = await response.text();
      const headers = new Headers(response.headers);
      headers.delete("content-length");
      if (rawPayload === undefined) return new Response(body || null, { status: response.status, headers });
      // gBizINFO int64 values must survive the SDK's JavaScript Number serialization.
      const exactPayload = JSON.parse(rawPayload, (_, value, context) =>
        typeof value === "number" ? JSON.rawJSON(context.source) : value);
      const restore = (data) => {
        const message = JSON.parse(data);
        if (message.result?.structuredContent) message.result.structuredContent = exactPayload;
        return JSON.stringify(message);
      };
      const exactBody = response.headers.get("content-type").includes("text/event-stream")
        ? body.replace(/^data: (.+)$/gm, (_, data) => `data: ${restore(data)}`)
        : restore(body);
      return new Response(exactBody, { status: response.status, headers });
    }
    finally { await handler.close(); }
  },
};
