const state = {
  view: "sites",
  properties: [],
  sites: [],
  queries: [],
  pages: [],
  errors: [],
  generation: 0,
  range: null,
  controller: null,
  loading: false,
  listError: null,
};

const elements = Object.fromEntries(
  [
    "login-view",
    "dashboard-view",
    "login-form",
    "password",
    "login-error",
    "logout",
    "period",
    "sort-by",
    "filter",
    "refresh",
    "status-panel",
    "status-title",
    "status-detail",
    "progress-bar",
    "metric-sites",
    "metric-errors",
    "metric-clicks",
    "metric-impressions",
    "metric-ctr",
    "last-updated",
    "table-head",
    "table-body",
    "row-count",
    "empty-state",
    "load-errors",
    "error-list",
    "retry-failed",
  ].map((id) => [id.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase()), document.getElementById(id)]),
);

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function safePageUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:" ? url.href : null;
  } catch {
    return null;
  }
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value || 0);
}

function formatPercent(value) {
  return new Intl.NumberFormat("en-US", { style: "percent", maximumFractionDigits: 2 }).format(
    value || 0,
  );
}

function formatPosition(value) {
  return value ? Number(value).toFixed(1) : "—";
}

function pause(milliseconds, signal) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(new DOMException("Cancelled", "AbortError"));
    const finish = () => { signal?.removeEventListener("abort", abort); resolve(); };
    const timer = setTimeout(finish, milliseconds);
    const abort = () => { clearTimeout(timer); signal?.removeEventListener("abort", abort);
      reject(new DOMException("Cancelled", "AbortError")); };
    signal?.addEventListener("abort", abort, { once: true });
  });
}

async function request(path, options = {}) {
  const { retry = false, signal, ...init } = options;
  for (let attempt = 0; ; attempt += 1) {
    if (signal?.aborted) throw new DOMException("Cancelled", "AbortError");
    const controller = new AbortController();
    const abort = () => controller.abort();
    signal?.addEventListener("abort", abort, { once: true });
    const timeout = setTimeout(abort, 60_000);
    let failure;
    try {
      const response = await fetch(path, { ...init, signal: controller.signal,
        headers: { "Content-Type": "application/json", ...(init.headers || {}) } });
      let payload;
      try { payload = await response.json(); } catch { payload = null; }
      if (!response.ok || !payload || typeof payload !== "object") {
        const error = new Error(payload?.error || `Dashboard request failed (HTTP ${response.status}). Retry.`);
        error.status = response.status;
        error.code = payload?.code;
        error.retryable = payload?.retryable ?? (response.status === 429 || response.status >= 500 || response.ok);
        const header = response.headers.get("Retry-After");
        const delay = header === null ? 0 : Number.isFinite(Number(header))
          ? Number(header) * 1000 : Date.parse(header) - Date.now();
        error.retryAfterMs = Math.max(0, Number.isFinite(delay) ? delay : 0, payload?.retryAfterMs || 0);
        throw error;
      }
      return payload;
    } catch (error) {
      if (signal?.aborted) throw new DOMException("Cancelled", "AbortError");
      failure = error;
      if (error.status === undefined) {
        failure = new Error(controller.signal.aborted ? "Dashboard request timed out. Retry."
          : "Could not reach the dashboard. Check your connection and retry.");
        failure.retryable = true;
      }
    } finally {
      clearTimeout(timeout);
      signal?.removeEventListener("abort", abort);
    }
    const delay = Math.max(failure.retryAfterMs || 0, 1000 + Math.floor(Math.random() * 500));
    if (!retry || !failure.retryable || attempt >= 1 || delay > 10_000) throw failure;
    await pause(delay, signal);
  }
}

function pacificDate(date) {
  const parts = Object.fromEntries(new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Los_Angeles", year: "numeric", month: "2-digit", day: "2-digit",
  }).formatToParts(date).map((part) => [part.type, part.value]));
  return `${parts.year}-${parts.month}-${parts.day}`;
}

function dateRange(now = new Date()) {
  const days = Number(elements.period.value);
  if (days === 1) {
    // A shared, fixed window for every property; never slide back to its last traffic event.
    const end = new Date(Math.floor(now.getTime() / 3_600_000) * 3_600_000);
    const start = new Date(end.getTime() - 24 * 3_600_000);
    return {
      startDate: pacificDate(start),
      endDate: pacificDate(new Date(end.getTime() - 1)),
      startHour: start.toISOString(), endHour: end.toISOString(), dataState: "hourly_all",
    };
  }
  const endDate = pacificDate(now);
  const start = new Date(`${endDate}T00:00:00Z`);
  start.setUTCDate(start.getUTCDate() - days + 1);
  return {
    startDate: start.toISOString().slice(0, 10), endDate, dataState: "all",
  };
}

function showLogin() {
  state.controller?.abort();
  elements.dashboardView.classList.add("hidden");
  elements.loginView.classList.remove("hidden");
  elements.password.focus();
}

function showDashboard() {
  elements.loginView.classList.add("hidden");
  elements.dashboardView.classList.remove("hidden");
}

function status(title, detail, progress) {
  elements.statusPanel.classList.remove("hidden");
  elements.statusTitle.textContent = title;
  elements.statusDetail.textContent = detail;
  elements.progressBar.style.width = `${Math.max(0, Math.min(progress, 100))}%`;
}

function aggregate() {
  const queryMap = new Map();
  const pages = [];
  for (const site of state.sites) {
    for (const row of site.queries) {
      const current = queryMap.get(row.key) || {
        label: row.key,
        clicks: 0,
        impressions: 0,
        positionNumerator: 0,
        properties: new Set(),
      };
      current.clicks += row.clicks;
      current.impressions += row.impressions;
      current.positionNumerator += row.position * row.impressions;
      current.properties.add(site.property);
      queryMap.set(row.key, current);
    }
    for (const row of site.pages) pages.push({ ...row, property: site.property, label: row.key });
  }
  state.queries = [...queryMap.values()].map((row) => ({
    label: row.label,
    clicks: row.clicks,
    impressions: row.impressions,
    ctr: row.impressions ? row.clicks / row.impressions : 0,
    position: row.impressions ? row.positionNumerator / row.impressions : 0,
    propertyCount: row.properties.size,
  }));
  state.pages = pages;
}

function updateMetrics() {
  const totals = state.sites.reduce(
    (current, site) => ({
      clicks: current.clicks + (site.total?.clicks || 0),
      impressions: current.impressions + (site.total?.impressions || 0),
    }),
    { clicks: 0, impressions: 0 },
  );
  elements.metricSites.textContent = formatNumber(state.sites.length);
  elements.metricErrors.textContent = `${state.sites.filter((site) => site.total).length} with totals / ${state.properties.length} properties`;
  const hasTotals = state.sites.some((site) => site.total);
  elements.metricClicks.textContent = hasTotals ? formatNumber(totals.clicks) : "—";
  elements.metricImpressions.textContent = hasTotals ? formatNumber(totals.impressions) : "—";
  elements.metricCtr.textContent = hasTotals ? formatPercent(
    totals.impressions ? totals.clicks / totals.impressions : 0,
  ) : "—";
}

function renderErrors() {
  const errors = state.listError ? [{ property: "Property list", error: state.listError }, ...state.errors] : state.errors;
  elements.loadErrors.classList.toggle("hidden", errors.length === 0);
  elements.errorList.innerHTML = errors.map((item) => `<li><strong>${escapeHtml(item.property)}</strong>` +
    `${item.component ? ` (${escapeHtml(item.component)})` : ""}: ${escapeHtml(item.error)}</li>`).join("");
  elements.retryFailed.disabled = state.loading;
  elements.retryFailed.textContent = state.listError ? "Retry loading properties" : "Retry failed properties";
}

function rowsForView() {
  if (state.view === "sites") {
    return state.sites.map((site) => ({
      label: site.property,
      property: site.property,
      unavailable: !site.total,
      stale: site.stale,
      partial: Boolean(site.errors?.length),
      ...site.total,
    }));
  }
  return state[state.view];
}

function renderTable() {
  const sortBy = elements.sortBy.value;
  const secondary = sortBy === "clicks" ? "impressions" : "clicks";
  const filter = elements.filter.value.trim().toLowerCase();
  const rows = rowsForView()
    .filter((row) => !filter || row.label.toLowerCase().includes(filter))
    .sort((left, right) => right[sortBy] - left[sortBy] || right[secondary] - left[secondary]);
  const contextHeading = state.view === "sites" ? "Property" : state.view === "queries" ? "Query" : "Page";
  const extraHeading = state.view === "queries" ? "Sites" : "";
  elements.tableHead.innerHTML = `<tr>
    <th>#</th><th>${contextHeading}</th><th>Clicks</th><th>Impressions</th>
    <th>CTR</th><th>Position</th>${extraHeading ? `<th>${extraHeading}</th>` : ""}
  </tr>`;
  elements.tableBody.innerHTML = rows
    .slice(0, 250)
    .map((row, index) => {
      const pageUrl = state.view === "pages" ? safePageUrl(row.label) : null;
      const label = pageUrl
        ? `<a href="${escapeHtml(pageUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(row.label)}</a>`
        : escapeHtml(row.label);
      return `<tr>
        <td class="rank">${index + 1}</td><td class="label-cell">${label}${row.stale ? ' <span class="load-note">Includes previous data — refresh failed or pending</span>' : row.partial ? ' <span class="load-note">Partial result</span>' : ""}</td>
        <td>${row.unavailable ? "—" : formatNumber(row.clicks)}</td><td>${row.unavailable ? "—" : formatNumber(row.impressions)}</td>
        <td>${row.unavailable ? "—" : formatPercent(row.ctr)}</td><td>${row.unavailable ? "—" : formatPosition(row.position)}</td>
        ${extraHeading ? `<td>${formatNumber(row.propertyCount)}</td>` : ""}
      </tr>`;
    })
    .join("");
  elements.rowCount.textContent = `${formatNumber(rows.length)} rows${rows.length > 250 ? " · showing 250" : ""}`;
  elements.emptyState.classList.toggle("hidden", rows.length > 0);
  elements.emptyState.textContent = state.loading ? "Loading Search Console data…"
    : state.errors.length || state.listError ? "Some data could not be loaded. See the errors above and retry."
    : "No matching Search Console data.";
}

async function loadProperty(property, range, forceRefresh = false, signal) {
  return request("/api/property-stats", {
    method: "POST",
    body: JSON.stringify({ property, ...range, forceRefresh }),
    retry: true, signal,
  });
}

async function loadDashboard(forceRefresh = false, retryOnly = false) {
  state.controller?.abort();
  const controller = new AbortController();
  state.controller = controller;
  const generation = ++state.generation;
  const range = retryOnly && state.range ? state.range : dateRange();
  const sameRange = JSON.stringify(range) === JSON.stringify(state.range);
  const failed = [...new Set(state.errors.map((item) => item.property))];
  state.range = range;
  if (!sameRange) state.sites = [];
  else state.sites = state.sites.map((site) => ({ ...site,
    stale: !retryOnly || failed.includes(site.property) ? true : site.stale }));
  state.errors = [];
  state.listError = null;
  state.loading = true;
  aggregate();
  updateMetrics();
  renderTable();
  renderErrors();
  status("Loading properties", "Reading the websites available in your GSC account…", 2);
  try {
    if (!retryOnly) {
      const response = await request("/api/properties", { retry: true, signal: controller.signal });
      if (generation !== state.generation) return;
      if (!Array.isArray(response.properties)) throw new Error("The dashboard returned an invalid property list. Retry.");
      state.properties = [...new Set(response.properties.map((item) => item.property))];
      // A successful list refresh is authoritative: removed/revoked properties disappear.
      state.sites = state.sites.filter((site) => state.properties.includes(site.property));
    }
    const properties = retryOnly ? failed : [...state.properties];
    let nextIndex = 0;
    let completed = 0;
    const worker = async () => {
      while (nextIndex < properties.length && generation === state.generation) {
        const index = nextIndex++;
        const property = properties[index];
        try {
          const result = await loadProperty(property, range, forceRefresh, controller.signal);
          if (generation !== state.generation) return;
          if (result.property !== property || !Array.isArray(result.queries) || !Array.isArray(result.pages) ||
              !(result.total === null || typeof result.total === "object" && result.total)) {
            throw new Error("The dashboard returned an invalid property result. Retry.");
          }
          const previous = state.sites.find((site) => site.property === property);
          const retainedComponents = [];
          for (const error of result.errors || []) {
            const key = error.component === "totals" ? "total" : error.component;
            if (previous && ((key === "total" && previous.total) ||
                (["queries", "pages"].includes(key) && previous[key]?.length))) {
              result[key] = previous[key];
              retainedComponents.push(error.component);
            }
          }
          if (retainedComponents.length) result.fetchedAt = previous.fetchedAt;
          state.sites = state.sites.filter((site) => site.property !== property);
          state.sites.push({ ...result, retainedComponents, stale: retainedComponents.length > 0 });
          state.errors.push(...(result.errors || []).map((error) => ({ ...error, property })));
        } catch (error) {
          if (generation !== state.generation) return;
          if (error.status === 401) { state.generation += 1; return showLogin(); }
          state.errors.push({ property, error: error.message, code: error.code });
        }
        completed += 1;
        status(
          "Loading Search performance",
          `${completed} of ${properties.length} properties checked`,
          properties.length ? (completed / properties.length) * 100 : 100,
        );
        aggregate();
        updateMetrics();
        renderTable();
        renderErrors();
      }
    };
    await Promise.all(Array.from({ length: Math.min(3, properties.length) }, () => worker()));
    if (generation !== state.generation) return;
    aggregate();
    updateMetrics();
    renderTable();
    const interval = range.dataState === "hourly_all"
      ? `${range.startHour.slice(0, 16)} to ${range.endHour.slice(0, 16)} UTC (end exclusive)`
      : `${range.startDate} through ${range.endDate} (Pacific Time)`;
    const limited = state.sites.filter((site) => site.breakdownsTruncated).length;
    const failureCount = new Set(state.errors.map((item) => item.property)).size;
    status(failureCount ? "Report incomplete · retry failed properties" : "Report ready · preliminary data",
      `${state.sites.length} properties available · ${interval}` +
      (failureCount ? ` · ${failureCount} properties have errors; totals may be incomplete or include labeled previous results` : "") +
      (limited ? ` · ${limited} properties have partial query/page rankings` : ""), 100);
  } catch (error) {
    if (generation !== state.generation) return;
    if (error.status === 401) return showLogin();
    state.listError = error.message;
    status("Could not load properties", error.message + (state.sites.length ? " Previous results for this period are still shown." : ""), 0);
  } finally {
    if (generation === state.generation) {
      state.loading = false;
      aggregate(); updateMetrics(); renderTable(); renderErrors();
      const fetchedTimes = state.sites.map((site) => Date.parse(site.fetchedAt)).filter(Number.isFinite);
      elements.lastUpdated.textContent = fetchedTimes.length
        ? `Oldest fetch: ${new Date(Math.min(...fetchedTimes)).toLocaleString()}` : "No data fetched";
    }
  }
}

elements.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  elements.loginError.textContent = "";
  try {
    await request("/api/login", {
      method: "POST",
      body: JSON.stringify({ password: elements.password.value }),
    });
    elements.password.value = "";
    showDashboard();
    await loadDashboard();
  } catch (error) {
    elements.loginError.textContent = error.message;
  }
});

elements.logout.addEventListener("click", async () => {
  state.generation += 1;
  state.controller?.abort();
  await request("/api/logout", { method: "POST", body: "{}" });
  state.sites = []; state.properties = []; state.errors = []; state.range = null;
  showLogin();
});

elements.refresh.addEventListener("click", () => loadDashboard(true));
elements.retryFailed.addEventListener("click", () => loadDashboard(true, !state.listError));
elements.period.addEventListener("change", () => loadDashboard());
elements.sortBy.addEventListener("change", renderTable);
elements.filter.addEventListener("input", renderTable);
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    state.view = tab.dataset.view;
    document.querySelectorAll(".tab").forEach((item) => item.classList.toggle("active", item === tab));
    renderTable();
  });
});

(async function start() {
  try {
    await request("/api/session", { retry: true });
    showDashboard();
    await loadDashboard();
  } catch (error) {
    showLogin();
    if (error.status !== 401) elements.loginError.textContent = `Could not check your session: ${error.message}`;
  }
})();
