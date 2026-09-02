import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { webcrypto } from "node:crypto";
import ts from "typescript";

const now = Date.parse("2026-09-01T15:30:00Z");
class FixedDate extends Date {
  constructor(...args) { super(...(args.length ? args : [now])); }
  static now() { return now; }
}
const workerSource = ts.transpileModule(readFileSync(new URL("worker.ts", import.meta.url), "utf8"), {
  compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS },
}).outputText;
const env = { GOOGLE_CLIENT_ID: "test", GOOGLE_CLIENT_SECRET: "test",
  GOOGLE_REFRESH_TOKEN: "test", SESSION_SECRET: "test-session", DASHBOARD_PASSWORD: "test-password" };

function workerHarness(responder = () => ({ rows: [] })) {
  const calls = [], pending = [], cacheKeys = [];
  const cached = new Map();
  const sandbox = vm.createContext({ exports: {}, Request, Response, Headers, URL, URLSearchParams,
    TextEncoder, crypto: webcrypto, console, Date: FixedDate,
    caches: { default: {
      async match(key) { cacheKeys.push(key.url); return cached.get(key.url)?.clone(); },
      async put(key, value) { cached.set(key.url, value.clone()); },
    } },
    async fetch(url, init) {
      if (url === "https://oauth2.googleapis.com/token") {
        return Response.json({ access_token: "test-token", expires_in: 3600 });
      }
      const body = JSON.parse(init.body);
      calls.push(body);
      return Response.json(responder(body));
    },
  });
  vm.runInContext(workerSource, sandbox);
  const functions = vm.runInContext("({ propertyStats, searchAnalytics, sumMetrics, inWindow, breakdown, api })", sandbox);
  const context = { waitUntil(promise) { pending.push(promise); } };
  return { ...functions, calls, cacheKeys, cached, pending,
    request(body) { return functions.propertyStats(new Request("https://dashboard.test/api/property-stats", {
      method: "POST", body: JSON.stringify(body),
    }), env, context); },
    api(path, options = {}) { return functions.api(new Request(`https://dashboard.test${path}`, options), env, context); },
  };
}
const daily = { property: "https://example.test/", startDate: "2026-08-26", endDate: "2026-09-01", dataState: "all" };
const hourly = { ...daily, startDate: "2026-08-31", dataState: "hourly_all",
  startHour: "2026-08-31T15:00:00.000Z", endHour: "2026-09-01T15:00:00.000Z" };
const metric = (hour, clicks, impressions, position = 2, key) => ({
  keys: key ? [hour, key] : [hour], clicks, impressions, position,
});

test("daily API includes preliminary impressions, independently of query rows", async () => {
  const h = workerHarness((body) => ({ rows: body.dimensions ? [] : [{ clicks: 0, impressions: 7, position: 4 }] }));
  const result = await (await h.request(daily)).json();
  assert.equal(result.total.impressions, 7);
  assert.equal(result.queries.length, 0);
  assert.equal(result.preliminary, true);
  assert.ok(h.calls.every((body) => body.dataState === "all" && body.endDate === "2026-09-01"));
});

test("hourly API filters exact bounds and combines duplicate keys with weighted metrics", async () => {
  const h = workerHarness((body) => ({
    rows: [
      metric("2026-08-31T07:00:00-07:00", 99, 999, 1, body.dimensions[1] && "same"),
      metric("2026-08-31T08:00:00-07:00", 1, 10, 2, body.dimensions[1] && "same"),
      metric("2026-09-01T07:00:00-07:00", 3, 30, 6, body.dimensions[1] && "same"),
      metric("2026-09-01T08:00:00-07:00", 99, 999, 1, body.dimensions[1] && "same"),
    ], metadata: { first_incomplete_hour: "2026-09-01T07:00:00-07:00" },
  }));
  const result = await (await h.request(hourly)).json();
  assert.deepEqual(result.total, { clicks: 4, impressions: 40, ctr: 0.1, position: 5 });
  assert.equal(result.queries.length, 1);
  assert.equal(result.queries[0].impressions, 40);
  assert.equal(result.pages[0].position, 5);
  assert.equal(result.metadata.first_incomplete_hour, "2026-09-01T07:00:00-07:00");
  assert.deepEqual(h.calls.map((body) => body.dimensions), [["hour"], ["hour", "query"], ["hour", "page"]]);
  assert.ok(h.calls.every((body) => body.dataState === "hourly_all"));
});

test("zero-traffic hourly window stays zero; old traffic never shifts the window", async () => {
  const h = workerHarness(() => ({ rows: [metric("2026-08-31T01:00:00-07:00", 1, 99)] }));
  const result = await (await h.request(hourly)).json();
  assert.equal(result.total.impressions, 0);
  assert.equal(result.startHour, hourly.startHour);
  assert.equal(result.endHour, hourly.endHour);
});

test("hourly breakdown pagination includes impressions beyond the first page", async () => {
  const h = workerHarness((body) => ({ rows: body.startRow === 0
    ? Array.from({ length: 25_000 }, (_, i) => metric("2026-09-01T06:00:00-07:00", 0, 1, 3, `query-${i}`))
    : [metric("2026-09-01T07:00:00-07:00", 0, 9, 4, "last-query")] }));
  const result = await h.searchAnalytics(env, daily.property, hourly.startDate, hourly.endDate, "hourly_all", "query");
  assert.equal(result.rows.length, 25_001);
  assert.equal(result.rows.at(-1).impressions, 9);
  assert.equal(result.truncated, false);
  assert.deepEqual(h.calls.map((body) => body.startRow), [0, 25_000]);
});

test("ordinary loads hit cache; Refresh bypasses and replaces it", async () => {
  let impressions = 1;
  const h = workerHarness(() => ({ rows: [{ impressions }] }));
  assert.equal((await (await h.request(daily)).json()).total.impressions, 1);
  await Promise.all(h.pending);
  impressions = 9;
  assert.equal((await (await h.request(daily)).json()).total.impressions, 1);
  assert.equal(h.calls.length, 3);
  assert.equal((await (await h.request({ ...daily, forceRefresh: true })).json()).total.impressions, 9);
  await Promise.all(h.pending);
  assert.equal(h.calls.length, 6);
  assert.equal((await (await h.request(daily)).json()).total.impressions, 9);
  assert.match([...h.cached.keys()][0], /property-v2/);
});

test("hour bounds separate cache entries even within the same Pacific date range", async () => {
  const h = workerHarness();
  await h.request(hourly);
  await Promise.all(h.pending);
  await h.request({ ...hourly, startHour: "2026-08-31T14:00:00Z", endHour: "2026-09-01T14:00:00Z" });
  assert.equal(h.calls.length, 6);
  assert.equal(h.cached.size, 2);
});

test("rejects malformed dates, missing hourly bounds, wrong ranges and invalid states before Google", async () => {
  const h = workerHarness();
  for (const body of [
    { ...daily, startDate: "2026-02-30" }, { ...hourly, startHour: undefined },
    { ...hourly, startHour: "2026-08-30T15:00:00Z" },
    { ...hourly, startDate: "2026-08-30" }, { ...daily, dataState: "invalid" },
  ]) assert.equal((await h.request(body)).status, 400);
  assert.equal(h.calls.length, 0);
});

test("API still requires login before stats or force-refresh requests", async () => {
  const h = workerHarness();
  assert.equal((await h.api("/api/property-stats", { method: "POST", body: JSON.stringify({ ...daily, forceRefresh: true }) })).status, 401);
  const login = await h.api("/api/login", { method: "POST", body: JSON.stringify({ password: env.DASHBOARD_PASSWORD }) });
  const cookie = login.headers.get("set-cookie").split(";")[0];
  assert.equal((await h.api("/api/property-stats", { method: "POST", headers: { Cookie: cookie }, body: JSON.stringify(daily) })).status, 200);
});

function browserHarness() {
  const elements = new Map(), calls = [];
  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, { value: id === "period" ? "28" : id === "sort-by" ? "impressions" : "",
        textContent: "", innerHTML: "", style: {}, listeners: {}, focus() {},
        classList: { add() {}, remove() {}, toggle() {} },
        addEventListener(type, handler) { this.listeners[type] = handler; } });
      return elements.get(id);
    }, querySelectorAll() { return []; },
  };
  const sandbox = vm.createContext({ document, Date: FixedDate, Intl, URL, console,
    async fetch(path, options) {
      if (path === "/api/session") return Response.json({}, { status: 401 });
      if (path === "/api/properties") return Response.json({ properties: [{ property: daily.property }] });
      calls.push(JSON.parse(options.body));
      return Response.json({ property: daily.property, total: { clicks: 0, impressions: 1 },
        queries: [], pages: [], fetchedAt: "2026-09-01T15:28:00Z" });
    },
  });
  vm.runInContext(readFileSync(new URL("public/app.js", import.meta.url), "utf8"), sandbox);
  return { elements, calls, sandbox, ...vm.runInContext("({ dateRange, loadDashboard, state })", sandbox) };
}

test("browser daily periods include Pacific today even before UTC/Pacific midnight align", () => {
  const h = browserHarness();
  const range = h.dateRange(new Date("2026-09-01T02:30:00Z"));
  assert.equal(range.endDate, "2026-08-31");
  assert.equal(range.startDate, "2026-08-04");
  assert.equal(range.dataState, "all");
});

test("browser hourly ranges remain exactly 24 hours across DST and midnight", () => {
  const h = browserHarness();
  h.elements.get("period").value = "1";
  for (const timestamp of ["2026-03-09T07:30:00Z", "2026-11-02T08:30:00Z", "2026-09-01T15:30:00Z"]) {
    const range = h.dateRange(new Date(timestamp));
    assert.equal(Date.parse(range.endHour) - Date.parse(range.startHour), 24 * 3_600_000);
    assert.equal(range.dataState, "hourly_all");
    assert.equal(Date.parse(range.endHour) % 3_600_000, 0);
  }
  assert.equal(h.dateRange(new Date("2026-03-09T07:30:00Z")).startDate, "2026-03-07");
});

test("Refresh sends a boolean bypass flag and reports the actual cached fetch time", async () => {
  const h = browserHarness();
  await h.loadDashboard();
  assert.equal(h.calls[0].forceRefresh, false);
  await h.elements.get("refresh").listeners.click();
  assert.equal(h.calls[1].forceRefresh, true);
  assert.equal(h.calls[1].dataState, "all");
  assert.match(h.elements.get("last-updated").textContent, /^Oldest fetch:/);
  assert.match(h.elements.get("status-title").textContent, /preliminary/);
});

test("a slow previous load cannot mix stale data into a refreshed report", async () => {
  const h = browserHarness();
  const fetch = h.sandbox.fetch;
  let releaseOld, notifyStarted, first = true;
  const started = new Promise((resolve) => { notifyStarted = resolve; });
  const oldResponse = new Promise((resolve) => { releaseOld = resolve; });
  h.sandbox.fetch = (path, options) => {
    if (path === "/api/property-stats" && first) {
      first = false;
      notifyStarted();
      return oldResponse;
    }
    return fetch(path, options);
  };
  const oldLoad = h.loadDashboard();
  await started;
  await h.loadDashboard(true);
  releaseOld(Response.json({ property: daily.property, total: { impressions: 99, clicks: 0 },
    queries: [], pages: [], fetchedAt: "2026-08-29T15:28:00Z" }));
  await oldLoad;
  assert.equal(h.state.sites.length, 1);
  assert.equal(h.state.sites[0].total.impressions, 1);
});
