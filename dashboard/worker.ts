interface Env {
  ASSETS: { fetch(request: Request): Promise<Response> };
  GOOGLE_CLIENT_ID: string;
  GOOGLE_CLIENT_SECRET: string;
  GOOGLE_REFRESH_TOKEN: string;
  DASHBOARD_PASSWORD: string;
  SESSION_SECRET: string;
}

interface WorkerContext {
  waitUntil(promise: Promise<unknown>): void;
}

interface GoogleTokenResponse {
  access_token?: string;
  expires_in?: number;
  error?: string;
  error_description?: string;
}

interface SearchRow {
  keys?: string[];
  clicks?: number;
  impressions?: number;
  ctr?: number;
  position?: number;
}

interface SearchResponse {
  rows?: SearchRow[];
  metadata?: { first_incomplete_hour?: string; first_incomplete_date?: string };
}

type DataState = "final" | "all" | "hourly_all";
interface HourWindow { start: number; end: number }

interface PropertyEntry {
  siteUrl?: string;
  permissionLevel?: string;
}

const SESSION_COOKIE = "gsc_dashboard_session";
const SESSION_SECONDS = 60 * 60 * 24 * 7;
const encoder = new TextEncoder();
let accessTokenCache: { token: string; expiresAt: number } | undefined;

interface GoogleRequest {
  requests: number;
  deadline: number;
  tokenRefresh?: Promise<string>;
}

function googleRequest(): GoogleRequest {
  return { requests: 0, deadline: Date.now() + 45_000 };
}

class GoogleError extends Error {
  constructor(message: string, readonly code: string, readonly retryable = false,
    readonly upstreamStatus = 0, readonly retryAfterMs = 0) { super(message); }
}

function errorDetails(error: unknown) {
  return error instanceof GoogleError
    ? { error: error.message, code: error.code, retryable: error.retryable,
        retryAfterMs: error.retryAfterMs, upstreamStatus: error.upstreamStatus }
    : { error: "Unexpected dashboard error. Retry or inspect the Worker logs.",
        code: "INTERNAL_ERROR", retryable: false };
}

function retryDelay(header: string | null): number {
  if (!header) return 0;
  const seconds = Number(header);
  const delay = Number.isFinite(seconds) ? seconds * 1000 : Date.parse(header) - Date.now();
  return Number.isFinite(delay) ? Math.max(0, delay) : 0;
}

async function googleFetch(url: string, init: RequestInit, scope: GoogleRequest): Promise<unknown> {
  for (let attempt = 0; ; attempt += 1) {
    // Shared across pagination, retries and OAuth; never consume the Worker's full budget.
    if (scope.requests >= 40 || scope.deadline <= Date.now()) {
      throw new GoogleError("Google requests reached the retry/time limit. Retry this property.", "GOOGLE_TIMEOUT", true);
    }
    scope.requests += 1;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), Math.min(15_000, scope.deadline - Date.now()));
    let failure: GoogleError;
    try {
      const response = await fetch(url, { ...init, signal: controller.signal });
      // Consume the body before retrying so the outgoing connection is released.
      const text = await response.text();
      let payload: any;
      try { payload = JSON.parse(text); } catch { payload = undefined; }
      if (response.ok && payload && typeof payload === "object") return payload;
      const reasons: string[] = payload?.error?.errors?.map((item: { reason?: string }) => item.reason) || [];
      const rateLimited = response.status === 429 || (response.status === 403 &&
        reasons.some((reason) => ["rateLimitExceeded", "userRateLimitExceeded", "concurrentLimitExceeded", "servingLimitExceeded"].includes(reason)));
      const transient = rateLimited || response.status === 408 || response.status >= 500 || response.ok;
      const oauth = url === "https://oauth2.googleapis.com/token";
      const code = rateLimited ? "GOOGLE_RATE_LIMIT" : transient ? "GOOGLE_UNAVAILABLE"
        : oauth ? "GOOGLE_RECONNECT_REQUIRED" : response.status === 401 ? "GOOGLE_ACCESS_TOKEN_EXPIRED"
        : response.status === 403 ? "GOOGLE_PERMISSION_DENIED" : "GOOGLE_REQUEST_REJECTED";
      const message = rateLimited ? "Google temporarily rate-limited requests. Wait and retry."
        : transient ? "Google is temporarily unavailable or returned an invalid response. Retry."
        : oauth ? "Google authorization expired or was revoked. Renew the local Google OAuth grant and redeploy its secrets."
        : response.status === 401 ? "Google rejected the access token."
        : response.status === 403 ? `Google denied access (${reasons[0] || "forbidden"}). Check property permissions, API access, or quota.`
        : `Google rejected the request (HTTP ${response.status}; ${reasons[0] || "unknown reason"}).`;
      failure = new GoogleError(message, code, transient, response.status, retryDelay(response.headers.get("Retry-After")));
    } catch (error) {
      failure = error instanceof GoogleError ? error : new GoogleError(
        controller.signal.aborted ? "Google request timed out. Retry." : "Could not reach Google. Retry.",
        controller.signal.aborted ? "GOOGLE_TIMEOUT" : "GOOGLE_NETWORK_ERROR", true);
    } finally {
      clearTimeout(timeout);
    }
    const delay = Math.max(failure.retryAfterMs, 500 * 2 ** attempt + Math.floor(Math.random() * 250));
    if (!failure.retryable || attempt >= 2 || Date.now() + delay >= scope.deadline) throw failure;
    await new Promise((resolve) => setTimeout(resolve, delay));
  }
}

function required(env: Env, key: keyof Env): string {
  const value = env[key];
  if (typeof value !== "string" || !value.trim()) {
    throw new GoogleError(`Missing Worker secret: ${String(key)}. Run the dashboard setup script.`, "CONFIGURATION_ERROR");
  }
  return value;
}

function baseHeaders(): HeadersInit {
  return {
    "Cache-Control": "no-store",
    "Content-Security-Policy":
      "default-src 'self'; connect-src 'self'; img-src 'self' data:; " +
      "script-src 'self'; style-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-Robots-Tag": "noindex, nofollow, noarchive",
  };
}

function json(data: unknown, status = 200, extraHeaders: HeadersInit = {}): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      ...baseHeaders(),
      "Content-Type": "application/json; charset=utf-8",
      ...extraHeaders,
    },
  });
}

function cookies(request: Request): Map<string, string> {
  const values = new Map<string, string>();
  for (const part of (request.headers.get("Cookie") || "").split(";")) {
    const separator = part.indexOf("=");
    if (separator < 0) continue;
    values.set(part.slice(0, separator).trim(), part.slice(separator + 1).trim());
  }
  return values;
}

function toHex(bytes: ArrayBuffer): string {
  return [...new Uint8Array(bytes)].map((value) => value.toString(16).padStart(2, "0")).join("");
}

async function signature(secret: string, message: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  return toHex(await crypto.subtle.sign("HMAC", key, encoder.encode(message)));
}

function constantTimeEqual(left: string, right: string): boolean {
  const leftBytes = encoder.encode(left);
  const rightBytes = encoder.encode(right);
  let difference = leftBytes.length ^ rightBytes.length;
  const length = Math.max(leftBytes.length, rightBytes.length);
  for (let index = 0; index < length; index += 1) {
    difference |= (leftBytes[index] || 0) ^ (rightBytes[index] || 0);
  }
  return difference === 0;
}

function cookieSecurity(request: Request): string {
  return new URL(request.url).protocol === "https:" ? "; Secure" : "";
}

async function sessionCookie(request: Request, env: Env): Promise<string> {
  const expires = Math.floor(Date.now() / 1000) + SESSION_SECONDS;
  const value = `${expires}.${await signature(required(env, "SESSION_SECRET"), String(expires))}`;
  return (
    `${SESSION_COOKIE}=${value}; Path=/; Max-Age=${SESSION_SECONDS}; ` +
    `HttpOnly; SameSite=Strict${cookieSecurity(request)}`
  );
}

async function isAuthenticated(request: Request, env: Env): Promise<boolean> {
  const value = cookies(request).get(SESSION_COOKIE);
  if (!value) return false;
  const [expiresRaw, suppliedSignature] = value.split(".", 2);
  const expires = Number(expiresRaw);
  if (!Number.isInteger(expires) || expires <= Math.floor(Date.now() / 1000) || !suppliedSignature) {
    return false;
  }
  const expected = await signature(required(env, "SESSION_SECRET"), expiresRaw);
  return constantTimeEqual(suppliedSignature, expected);
}

async function googleAccessToken(env: Env, scope: GoogleRequest): Promise<string> {
  if (accessTokenCache && accessTokenCache.expiresAt > Date.now() + 60_000) {
    return accessTokenCache.token;
  }
  if (scope.tokenRefresh) return scope.tokenRefresh;
  // Deduplicate the three parallel queries in this invocation, without sharing I/O
  // promises across unrelated Cloudflare Worker requests.
  scope.tokenRefresh = (async () => {
  const form = new URLSearchParams({
    client_id: required(env, "GOOGLE_CLIENT_ID"),
    client_secret: required(env, "GOOGLE_CLIENT_SECRET"),
    refresh_token: required(env, "GOOGLE_REFRESH_TOKEN"),
    grant_type: "refresh_token",
  });
  const payload = await googleFetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  }, scope) as GoogleTokenResponse;
  if (!payload.access_token) {
    throw new GoogleError("Google returned no access token. Renew the Google OAuth grant.", "GOOGLE_RECONNECT_REQUIRED");
  }
  accessTokenCache = {
    token: payload.access_token,
    expiresAt: Date.now() + (payload.expires_in || 3600) * 1000,
  };
  return payload.access_token;
  })();
  try { return await scope.tokenRefresh; }
  finally { scope.tokenRefresh = undefined; }
}

async function googleJson<T>(env: Env, url: string, init: RequestInit = {}, scope = googleRequest()): Promise<T> {
  let token = await googleAccessToken(env, scope);
  const fetchData = () => googleFetch(url, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  }, scope) as Promise<T>;
  try { return await fetchData(); }
  catch (error) {
    if (!(error instanceof GoogleError) || error.code !== "GOOGLE_ACCESS_TOKEN_EXPIRED") throw error;
    // Invalidate only the token this request used; another query may have refreshed it.
    if (accessTokenCache?.token === token) accessTokenCache = undefined;
    token = await googleAccessToken(env, scope);
    try { return await fetchData(); }
    catch (retryError) {
      if (retryError instanceof GoogleError && retryError.code === "GOOGLE_ACCESS_TOKEN_EXPIRED") {
        throw new GoogleError("Google authorization was rejected after refreshing. Renew the Google OAuth grant.", "GOOGLE_RECONNECT_REQUIRED");
      }
      throw retryError;
    }
  }
}

function normalizedMetric(row: SearchRow | undefined) {
  return {
    clicks: Number(row?.clicks || 0),
    impressions: Number(row?.impressions || 0),
    ctr: Number(row?.ctr || 0),
    position: Number(row?.position || 0),
  };
}

async function searchAnalytics(
  env: Env,
  property: string,
  startDate: string,
  endDate: string,
  dataState: DataState,
  dimension?: "query" | "page",
  scope = googleRequest(),
): Promise<SearchResponse & { rows: SearchRow[]; truncated: boolean }> {
  const hourly = dataState === "hourly_all";
  const pageSize = hourly && dimension ? 25_000 : dimension || hourly ? 250 : 1;
  // Up to four pages per breakdown: bounded well below Worker subrequest limits.
  const maxRows = hourly && dimension ? 100_000 : pageSize;
  const body: Record<string, unknown> = {
    startDate,
    endDate,
    type: "web",
    dataState,
    rowLimit: pageSize,
  };
  if (hourly) body.dimensions = dimension ? ["hour", dimension] : ["hour"];
  else if (dimension) body.dimensions = [dimension];
  const encoded = encodeURIComponent(property);
  const rows: SearchRow[] = [];
  let metadata: SearchResponse["metadata"];
  while (rows.length < maxRows) {
    const response = await googleJson<SearchResponse>(
      env,
      `https://www.googleapis.com/webmasters/v3/sites/${encoded}/searchAnalytics/query`,
      { method: "POST", body: JSON.stringify({ ...body, startRow: rows.length }) },
      scope,
    );
    metadata = response.metadata || metadata;
    const page = response.rows || [];
    rows.push(...page);
    if (page.length < pageSize) return { rows, metadata, truncated: false };
  }
  return { rows, metadata, truncated: Boolean(dimension) };
}

function sumMetrics(rows: SearchRow[]) {
  let clicks = 0, impressions = 0, weightedPosition = 0;
  for (const row of rows) {
    const metric = normalizedMetric(row);
    clicks += metric.clicks;
    impressions += metric.impressions;
    weightedPosition += metric.position * metric.impressions;
  }
  return { clicks, impressions, ctr: impressions ? clicks / impressions : 0,
    position: impressions ? weightedPosition / impressions : 0 };
}

function inWindow(rows: SearchRow[], window: HourWindow): SearchRow[] {
  return rows.filter((row) => {
    const hour = Date.parse(row.keys?.[0] || "");
    return hour >= window.start && hour < window.end;
  });
}

function breakdown(rows: SearchRow[], hourly: boolean) {
  const grouped = new Map<string, SearchRow[]>();
  for (const row of rows) {
    const key = String(row.keys?.[hourly ? 1 : 0] || "");
    const group = grouped.get(key) || [];
    group.push(row);
    grouped.set(key, group);
  }
  return [...grouped.entries()].map(([key, group]) => ({ key, ...sumMetrics(group) }));
}

function pacificDate(milliseconds: number): string {
  const parts = Object.fromEntries(new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Los_Angeles", year: "numeric", month: "2-digit", day: "2-digit",
  }).formatToParts(new Date(milliseconds)).map((part) => [part.type, part.value]));
  return `${parts.year}-${parts.month}-${parts.day}`;
}

function validDate(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const time = Date.parse(`${value}T00:00:00Z`);
  return Number.isFinite(time) && new Date(time).toISOString().slice(0, 10) === value;
}

function validProperty(value: unknown): value is string {
  if (typeof value !== "string" || value.length > 500) return false;
  if (/^sc-domain:[a-z0-9.-]+$/i.test(value)) return true;
  try {
    const url = new URL(value);
    return (url.protocol === "https:" || url.protocol === "http:") && Boolean(url.hostname);
  } catch {
    return false;
  }
}

async function propertyStats(request: Request, env: Env, context: WorkerContext): Promise<Response> {
  const body = (await request.json()) as Record<string, unknown>;
  const property = body.property;
  const startDate = body.startDate;
  const endDate = body.endDate;
  const dataState = body.dataState ?? "all";
  if (dataState !== "all" && dataState !== "hourly_all" && dataState !== "final") {
    return json({ error: "Invalid data state" }, 400);
  }
  if (!validProperty(property) || !validDate(startDate) || !validDate(endDate) || startDate > endDate) {
    return json({ error: "Invalid property or date range" }, 400);
  }

  let window: HourWindow | undefined;
  if (dataState === "hourly_all") {
    const start = typeof body.startHour === "string" ? Date.parse(body.startHour) : NaN;
    const end = typeof body.endHour === "string" ? Date.parse(body.endHour) : NaN;
    if (!Number.isFinite(start) || !Number.isFinite(end) ||
        start % 3_600_000 !== 0 || end - start !== 24 * 3_600_000 ||
        end > Date.now() || start < Date.now() - 10 * 24 * 3_600_000 ||
        startDate !== pacificDate(start) || endDate !== pacificDate(end - 1)) {
      return json({ error: "Invalid 24-hour window" }, 400);
    }
    window = { start, end };
  }

  const cacheUrl = new URL("https://gsc-dashboard-cache.internal/property-v2");
  cacheUrl.searchParams.set("property", property);
  cacheUrl.searchParams.set("start", startDate);
  cacheUrl.searchParams.set("end", endDate);
  cacheUrl.searchParams.set("state", dataState);
  if (window) {
    cacheUrl.searchParams.set("hourStart", String(window.start));
    cacheUrl.searchParams.set("hourEnd", String(window.end));
  }
  const cacheKey = new Request(cacheUrl.toString());
  const cache = (caches as CacheStorage & { default: Cache }).default;
  try {
    const cached = body.forceRefresh === true ? undefined : await cache.match(cacheKey);
    if (cached) return json(await cached.json());
  } catch { /* Cache is an optimization; an edge-cache failure must not block Google. */ }

  const scope = googleRequest();
  const results = await Promise.allSettled([
    searchAnalytics(env, property, startDate, endDate, dataState, undefined, scope),
    searchAnalytics(env, property, startDate, endDate, dataState, "query", scope),
    searchAnalytics(env, property, startDate, endDate, dataState, "page", scope),
  ]);
  if (results.every((result) => result.status === "rejected")) {
    throw (results[0] as PromiseRejectedResult).reason;
  }
  const components = ["totals", "queries", "pages"];
  const errors = results.flatMap((result, index) => result.status === "rejected"
    ? [{ component: components[index], ...errorDetails(result.reason) }] : []);
  const [totals, queries, pages] = results.map((result) => result.status === "fulfilled" ? result.value : undefined);
  const selectRows = (response: SearchResponse) => window
    ? inWindow(response.rows || [], window) : response.rows || [];
  const payload = {
    property,
    total: totals ? sumMetrics(selectRows(totals)) : null,
    queries: queries ? breakdown(selectRows(queries), Boolean(window)) : [],
    pages: pages ? breakdown(selectRows(pages), Boolean(window)) : [],
    errors,
    dataState,
    preliminary: dataState !== "final",
    metadata: totals?.metadata,
    startDate, endDate,
    startHour: window ? new Date(window.start).toISOString() : undefined,
    endHour: window ? new Date(window.end).toISOString() : undefined,
    breakdownsTruncated: Boolean(queries?.truncated || pages?.truncated),
    fetchedAt: new Date().toISOString(),
  };
  // Partial failures must be retried rather than cached as complete/empty data.
  if (!errors.length) context.waitUntil(
    cache.put(
      cacheKey,
      new Response(JSON.stringify(payload), {
        headers: { "Cache-Control": "public, max-age=300", "Content-Type": "application/json" },
      }),
    ).catch(() => { /* Cache writes are best-effort. */ }),
  );
  return json(payload);
}

async function api(request: Request, env: Env, context: WorkerContext): Promise<Response> {
  const url = new URL(request.url);
  if (url.pathname === "/api/login" && request.method === "POST") {
    const body = (await request.json()) as { password?: string };
    const accepted = constantTimeEqual(String(body.password || ""), required(env, "DASHBOARD_PASSWORD"));
    if (!accepted) return json({ error: "Incorrect password" }, 401);
    return json({ authenticated: true }, 200, { "Set-Cookie": await sessionCookie(request, env) });
  }
  if (url.pathname === "/api/logout" && request.method === "POST") {
    return json(
      { authenticated: false },
      200,
      {
        "Set-Cookie":
          `${SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict` +
          cookieSecurity(request),
      },
    );
  }

  const authenticated = await isAuthenticated(request, env);
  if (url.pathname === "/api/session") return json({ authenticated }, authenticated ? 200 : 401);
  if (!authenticated) return json({ error: "Authentication required" }, 401);

  if (url.pathname === "/api/properties" && request.method === "GET") {
    const response = await googleJson<{ siteEntry?: PropertyEntry[] }>(
      env,
      "https://www.googleapis.com/webmasters/v3/sites",
    );
    const properties = (response.siteEntry || [])
      .filter(
        (item) =>
          item.siteUrl && item.permissionLevel !== "siteUnverifiedUser",
      )
      .map((item) => ({ property: item.siteUrl, permissionLevel: item.permissionLevel }))
      .sort((left, right) => String(left.property).localeCompare(String(right.property)));
    return json({ properties });
  }
  if (url.pathname === "/api/property-stats" && request.method === "POST") {
    return propertyStats(request, env, context);
  }
  return json({ error: "Not found" }, 404);
}

function withSecurityHeaders(response: Response): Response {
  const secured = new Response(response.body, response);
  const headers = baseHeaders();
  for (const [name, value] of Object.entries(headers)) secured.headers.set(name, value);
  return secured;
}

export default {
  async fetch(request: Request, env: Env, context: WorkerContext): Promise<Response> {
    const url = new URL(request.url);
    try {
      if (url.pathname.startsWith("/api/")) return await api(request, env, context);
      return withSecurityHeaders(await env.ASSETS.fetch(request));
    } catch (error) {
      console.error(error);
      const detail = errorDetails(error);
      // Only the dashboard's own expired session is HTTP 401. Google OAuth errors
      // must stay visible in the dashboard, not kick the user back to the password form.
      return json(detail, detail.retryable ? 503 : 502,
        error instanceof GoogleError && error.retryAfterMs
          ? { "Retry-After": String(Math.ceil(error.retryAfterMs / 1000)) } : {});
    }
  },
};
