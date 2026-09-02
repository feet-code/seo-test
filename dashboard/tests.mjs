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

function workerHarness(responder = () => ({ rows: [] }), options = {}) {
  const calls = [], pending = [], cacheKeys = [], tokenCalls = [], delays = [];
  const cached = new Map();
  const sandbox = vm.createContext({ exports: {}, Request, Response, Headers, URL, URLSearchParams,
    TextEncoder, crypto: webcrypto, console, Date: FixedDate, AbortController,
    setTimeout(fn, ms) { delays.push(ms); return setTimeout(fn, ms < 10_000 || options.fastTimeout ? 0 : ms); }, clearTimeout,
    caches: { default: {
      async match(key) { cacheKeys.push(key.url); return cached.get(key.url)?.clone(); },
      async put(key, value) { cached.set(key.url, value.clone()); },
    } },
    async fetch(url, init) {
      if (url === "https://oauth2.googleapis.com/token") {
        tokenCalls.push(init);
        return options.token ? options.token(tokenCalls.length) : Response.json({ access_token: "test-token", expires_in: 3600 });
      }
      const body = init.body ? JSON.parse(init.body) : null;
      calls.push(body);
      const result = await responder(body, init, url);
      return result instanceof Response ? result : Response.json(result);
    },
  });
  vm.runInContext(workerSource, sandbox);
  const functions = vm.runInContext("({ propertyStats, searchAnalytics, sumMetrics, inWindow, breakdown, api, googleJson, googleRequest })", sandbox);
  const context = { waitUntil(promise) { pending.push(promise); } };
  return { ...functions, calls, cacheKeys, cached, pending, tokenCalls, delays, sandbox,
    dispatch(path, options = {}) { return sandbox.exports.default.fetch(new Request(`https://dashboard.test${path}`, options), env, context); },
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
  const delays = [];
  const sandbox = vm.createContext({ document, Date: FixedDate, Intl, URL, console, AbortController, DOMException,
    setTimeout(fn, ms) { delays.push(ms); return setTimeout(fn, ms < 10_000 ? 0 : ms); }, clearTimeout,
    async fetch(path, options) {
      if (path === "/api/session") return Response.json({}, { status: 401 });
      if (path === "/api/properties") return Response.json({ properties: [{ property: daily.property }] });
      calls.push(JSON.parse(options.body));
      return Response.json({ property: daily.property, total: { clicks: 0, impressions: 1 },
        queries: [], pages: [], fetchedAt: "2026-09-01T15:28:00Z" });
    },
  });
  const ready = vm.runInContext(readFileSync(new URL("public/app.js", import.meta.url), "utf8"), sandbox);
  const functions = vm.runInContext("({ dateRange, loadDashboard, state, request })", sandbox);
  return { elements, calls, sandbox, delays, ready, ...functions,
    async loadDashboard(...args) { await ready; return functions.loadDashboard(...args); } };
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

const googleFailure = (status, reason, headers = {}) => Response.json({
  error: { code: status, errors: [{ reason }], message: "upstream details" },
}, { status, headers });

test("Google retries 429 and rate-limit 403 with backoff; honors Retry-After", async () => {
  for (const status of [429, 403]) {
    let attempts = 0;
    const h = workerHarness(() => ++attempts === 1
      ? googleFailure(status, "userRateLimitExceeded", { "Retry-After": "2" })
      : { siteEntry: [] });
    await h.googleJson(env, "https://www.googleapis.com/webmasters/v3/sites");
    assert.equal(h.calls.length, 2);
    assert.ok(h.delays.includes(2000));
  }
});

test("Google permanent permissions and daily quota failures are not retried", async () => {
  for (const reason of ["insufficientPermissions", "dailyLimitExceeded"]) {
    const h = workerHarness(() => googleFailure(403, reason));
    await assert.rejects(h.googleJson(env, "https://www.googleapis.com/webmasters/v3/sites"),
      (error) => error.code === "GOOGLE_PERMISSION_DENIED" && error.retryable === false);
    assert.equal(h.calls.length, 1);
  }
});

test("Google retries network errors and malformed 502 responses", async () => {
  let attempts = 0;
  const h = workerHarness(() => {
    attempts += 1;
    if (attempts === 1) throw new Error("socket closed");
    if (attempts === 2) return new Response("upstream HTML error", { status: 502 });
    return { rows: [] };
  });
  await h.googleJson(env, "https://www.googleapis.com/webmasters/v3/sites");
  assert.equal(attempts, 3);
});

test("Google retries are bounded and do not ignore a long Retry-After", async () => {
  const h = workerHarness(() => googleFailure(503, "backendError"));
  await assert.rejects(h.googleJson(env, "https://www.googleapis.com/webmasters/v3/sites"),
    (error) => error.retryable === true);
  assert.equal(h.calls.length, 3);
  const rateLimited = workerHarness(() => googleFailure(429, "rateLimitExceeded", { "Retry-After": "120" }));
  await assert.rejects(rateLimited.googleJson(env, "https://www.googleapis.com/webmasters/v3/sites"),
    (error) => error.retryAfterMs === 120_000);
  assert.equal(rateLimited.calls.length, 1);
});

test("hung Google requests time out and stop after three attempts", async () => {
  const h = workerHarness((body, init) => new Promise((resolve, reject) => {
    init.signal.addEventListener("abort", () => reject(new DOMException("Timeout", "AbortError")), { once: true });
  }), { fastTimeout: true });
  await assert.rejects(h.googleJson(env, "https://www.googleapis.com/webmasters/v3/sites"),
    (error) => error.code === "GOOGLE_TIMEOUT");
  assert.equal(h.calls.length, 3);
});

test("parallel property queries share one OAuth refresh and refresh a rejected token once", async () => {
  const h = workerHarness((body, init) => init.headers.Authorization === "Bearer old-token"
    ? googleFailure(401, "authError") : { rows: [] }, {
    token: (attempt) => Response.json({ access_token: attempt === 1 ? "old-token" : "new-token", expires_in: 3600 }),
  });
  assert.equal((await h.request(daily)).status, 200);
  assert.equal(h.tokenCalls.length, 2);
  assert.equal(h.calls.length, 6);
  const success = workerHarness();
  await success.request(daily);
  assert.equal(success.tokenCalls.length, 1);
});

test("revoked OAuth grants return an actionable non-retryable error, not dashboard HTTP 401", async () => {
  const h = workerHarness(() => ({ rows: [] }), {
    token: () => Response.json({ error: "invalid_grant" }, { status: 400 }),
  });
  const login = await h.api("/api/login", { method: "POST", body: JSON.stringify({ password: env.DASHBOARD_PASSWORD }) });
  const response = await h.dispatch("/api/properties", { headers: { Cookie: login.headers.get("set-cookie").split(";")[0] } });
  assert.equal(response.status, 502);
  const result = await response.json();
  assert.equal(result.code, "GOOGLE_RECONNECT_REQUIRED");
  assert.equal(result.retryable, false);
  assert.equal(h.tokenCalls.length, 1);
});

test("one failed breakdown does not discard site totals or the other breakdown; partial results aren't cached", async () => {
  const h = workerHarness((body) => body.dimensions?.[0] === "query"
    ? googleFailure(503, "backendError")
    : { rows: [{ keys: ["https://example.test/page"], impressions: 13, clicks: 1 }] });
  const result = await (await h.request(daily)).json();
  assert.equal(result.total.impressions, 13);
  assert.equal(result.pages[0].impressions, 13);
  assert.equal(result.queries.length, 0);
  assert.equal(result.errors[0].component, "queries");
  assert.equal(result.errors[0].retryable, true);
  await Promise.all(h.pending);
  assert.equal(h.cached.size, 0);
});

test("failed totals are unknown, not zero, while successful breakdowns remain available", async () => {
  const h = workerHarness((body) => !body.dimensions ? googleFailure(403, "insufficientPermissions")
    : { rows: [{ keys: ["term"], impressions: 5 }] });
  const result = await (await h.request(daily)).json();
  assert.equal(result.total, null);
  assert.equal(result.queries[0].impressions, 5);
  assert.equal(result.errors[0].component, "totals");
});

test("cache read and write failures don't discard Google results", async () => {
  const h = workerHarness(() => ({ rows: [{ impressions: 3 }] }));
  h.sandbox.caches.default.match = async () => { throw new Error("cache read failed"); };
  h.sandbox.caches.default.put = async () => { throw new Error("cache write failed"); };
  assert.equal((await (await h.request(daily)).json()).total.impressions, 3);
  await Promise.all(h.pending);
});

test("subrequest budgets stop before the Worker platform limit", async () => {
  const h = workerHarness();
  const scope = h.googleRequest();
  scope.requests = 40;
  await assert.rejects(h.googleJson(env, "https://www.googleapis.com/webmasters/v3/sites", {}, scope),
    (error) => error.code === "GOOGLE_TIMEOUT");
  assert.equal(h.calls.length + h.tokenCalls.length, 0);
});

test("failed property listing preserves the previous report and can recover without a page reload", async () => {
  const h = browserHarness();
  await h.loadDashboard();
  const fetch = h.sandbox.fetch;
  h.sandbox.fetch = (path, options) => path === "/api/properties"
    ? Response.json({ error: "Google unavailable", retryable: true }, { status: 503 }) : fetch(path, options);
  await h.loadDashboard(true);
  assert.equal(h.state.sites.length, 1);
  assert.equal(h.state.sites[0].total.impressions, 1);
  assert.equal(h.state.sites[0].stale, true);
  assert.match(h.elements.get("error-list").innerHTML, /Google unavailable/);
  assert.match(h.elements.get("status-detail").textContent, /Previous results/);
  h.sandbox.fetch = fetch;
  await h.elements.get("retry-failed").listeners.click();
  assert.equal(h.state.listError, null);
  assert.equal(h.state.sites[0].stale, false);
});

test("retry failed properties only; keep successes and never duplicate their totals", async () => {
  const h = browserHarness();
  await h.ready;
  const fetch = h.sandbox.fetch;
  const failed = "https://failing.test/";
  let broken = true;
  const requested = [];
  h.sandbox.fetch = (path, options) => {
    if (path === "/api/properties") return Response.json({ properties: [daily.property, failed].map((property) => ({ property })) });
    if (path === "/api/property-stats") {
      const body = JSON.parse(options.body); requested.push(body.property);
      if (body.property === failed && broken) return Response.json({ error: "Try later", retryable: false }, { status: 503 });
      return Response.json({ property: body.property, total: { clicks: 1, impressions: 10 }, queries: [], pages: [], fetchedAt: "2026-09-01T15:28:00Z" });
    }
    return fetch(path, options);
  };
  await h.loadDashboard();
  assert.equal(h.state.sites.length, 1);
  assert.equal(h.state.errors.length, 1);
  assert.match(h.elements.get("status-title").textContent, /incomplete/);
  assert.match(h.elements.get("error-list").innerHTML, /failing.test/);
  broken = false; requested.length = 0;
  await h.elements.get("retry-failed").listeners.click();
  assert.deepEqual(requested, [failed]);
  assert.equal(h.state.sites.length, 2);
  assert.equal(h.state.errors.length, 0);
  assert.equal(h.elements.get("metric-impressions").textContent, "20");
});

test("frontend retries network failures and HTML 502 once, but not permanent Google errors", async () => {
  const h = browserHarness();
  await h.ready;
  let count = 0;
  h.sandbox.fetch = () => ++count === 1 ? new Response("bad gateway", { status: 502 }) : Response.json({ ok: true });
  assert.equal((await h.request("/api/properties", { retry: true })).ok, true);
  assert.equal(count, 2);
  count = 0;
  h.sandbox.fetch = () => { count += 1; return Response.json({ error: "Renew OAuth", code: "GOOGLE_RECONNECT_REQUIRED", retryable: false }, { status: 502 }); };
  await assert.rejects(h.request("/api/properties", { retry: true }), /Renew OAuth/);
  assert.equal(count, 1);
});

test("new periods do not reuse old values after failure; failure is not an empty zero report", async () => {
  const h = browserHarness();
  await h.loadDashboard();
  h.elements.get("period").value = "7";
  h.sandbox.fetch = () => Response.json({ error: "No access", retryable: false }, { status: 502 });
  await h.loadDashboard();
  assert.equal(h.state.sites.length, 0);
  assert.equal(h.elements.get("metric-impressions").textContent, "—");
  assert.match(h.elements.get("empty-state").textContent, /could not be loaded/);
});

test("partial results with missing totals show unavailable metrics and actionable component errors", async () => {
  const h = browserHarness();
  await h.ready;
  const fetch = h.sandbox.fetch;
  h.sandbox.fetch = (path, options) => path === "/api/property-stats"
    ? Response.json({ property: daily.property, total: null, queries: [{ key: "term", clicks: 1, impressions: 4, position: 2 }], pages: [],
      errors: [{ component: "totals", error: "Timed out", retryable: true }], fetchedAt: "2026-09-01T15:28:00Z" }) : fetch(path, options);
  await h.loadDashboard();
  assert.equal(h.elements.get("metric-impressions").textContent, "—");
  assert.equal(h.state.queries.length, 1);
  assert.match(h.elements.get("error-list").innerHTML, /totals/);
  assert.match(h.elements.get("table-body").innerHTML, /Partial result/);
});

test("a failed totals refresh keeps previous same-period totals with a stale warning", async () => {
  const h = browserHarness();
  await h.loadDashboard();
  const fetch = h.sandbox.fetch;
  h.sandbox.fetch = (path, options) => path === "/api/property-stats"
    ? Response.json({ property: daily.property, total: null, queries: [], pages: [],
      errors: [{ component: "totals", error: "Timed out", retryable: true }], fetchedAt: "2026-09-01T15:30:00Z" }) : fetch(path, options);
  await h.loadDashboard(true);
  assert.equal(h.elements.get("metric-impressions").textContent, "1");
  assert.equal(h.state.sites[0].stale, true);
  assert.equal(h.state.sites[0].fetchedAt, "2026-09-01T15:28:00Z");
  assert.match(h.elements.get("table-body").innerHTML, /Includes previous data/);
});
