const state = {
  view: "sites",
  properties: [],
  sites: [],
  queries: [],
  pages: [],
  errors: [],
  generation: 0,
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

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.error || `Request failed (${response.status})`);
    error.status = response.status;
    throw error;
  }
  return payload;
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
      clicks: current.clicks + site.total.clicks,
      impressions: current.impressions + site.total.impressions,
    }),
    { clicks: 0, impressions: 0 },
  );
  elements.metricSites.textContent = formatNumber(state.sites.length);
  elements.metricErrors.textContent = state.errors.length
    ? `${state.errors.length} properties could not be loaded`
    : `${state.properties.length} accessible in GSC`;
  elements.metricClicks.textContent = formatNumber(totals.clicks);
  elements.metricImpressions.textContent = formatNumber(totals.impressions);
  elements.metricCtr.textContent = formatPercent(
    totals.impressions ? totals.clicks / totals.impressions : 0,
  );
}

function rowsForView() {
  if (state.view === "sites") {
    return state.sites.map((site) => ({
      label: site.property,
      property: site.property,
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
        <td class="rank">${index + 1}</td><td class="label-cell">${label}</td>
        <td>${formatNumber(row.clicks)}</td><td>${formatNumber(row.impressions)}</td>
        <td>${formatPercent(row.ctr)}</td><td>${formatPosition(row.position)}</td>
        ${extraHeading ? `<td>${formatNumber(row.propertyCount)}</td>` : ""}
      </tr>`;
    })
    .join("");
  elements.rowCount.textContent = `${formatNumber(rows.length)} rows${rows.length > 250 ? " · showing 250" : ""}`;
  elements.emptyState.classList.toggle("hidden", rows.length > 0);
}

async function loadProperty(property, range, forceRefresh = false) {
  return request("/api/property-stats", {
    method: "POST",
    body: JSON.stringify({ property, ...range, forceRefresh }),
  });
}

async function loadDashboard(forceRefresh = false) {
  const generation = ++state.generation;
  const range = dateRange();
  state.sites = [];
  state.queries = [];
  state.pages = [];
  state.errors = [];
  elements.lastUpdated.textContent = "";
  updateMetrics();
  renderTable();
  status("Loading properties", "Reading the websites available in your GSC account…", 2);
  try {
    const response = await request("/api/properties");
    if (generation !== state.generation) return;
    state.properties = response.properties.map((item) => item.property);
    const properties = [...state.properties];
    let nextIndex = 0;
    let completed = 0;
    const worker = async () => {
      while (nextIndex < properties.length && generation === state.generation) {
        const index = nextIndex++;
        const property = properties[index];
        try {
          const result = await loadProperty(property, range, forceRefresh);
          if (generation !== state.generation) return;
          state.sites.push(result);
        } catch (error) {
          if (generation !== state.generation) return;
          if (error.status === 401) { state.generation += 1; return showLogin(); }
          state.errors.push({ property, error: error.message });
        }
        completed += 1;
        status(
          "Loading Search performance",
          `${completed} of ${state.properties.length} properties complete`,
          state.properties.length ? (completed / state.properties.length) * 100 : 100,
        );
        aggregate();
        updateMetrics();
        renderTable();
      }
    };
    await Promise.all(Array.from({ length: Math.min(6, state.properties.length) }, () => worker()));
    if (generation !== state.generation) return;
    aggregate();
    updateMetrics();
    renderTable();
    const interval = range.dataState === "hourly_all"
      ? `${range.startHour.slice(0, 16)} to ${range.endHour.slice(0, 16)} UTC (end exclusive)`
      : `${range.startDate} through ${range.endDate} (Pacific Time)`;
    const limited = state.sites.filter((site) => site.breakdownsTruncated).length;
    status("Report ready · preliminary data", `${state.sites.length} properties loaded · ${interval}` +
      (state.errors.length ? ` · ${state.errors.length} failed` : "") +
      (limited ? ` · ${limited} properties have partial query/page rankings` : ""), 100);
    const fetchedTimes = state.sites.map((site) => Date.parse(site.fetchedAt)).filter(Number.isFinite);
    elements.lastUpdated.textContent = fetchedTimes.length
      ? `Oldest fetch: ${new Date(Math.min(...fetchedTimes)).toLocaleString()}` : "No data fetched";
  } catch (error) {
    if (generation !== state.generation) return;
    if (error.status === 401) return showLogin();
    status("Could not load GSC", error.message, 0);
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
  await request("/api/logout", { method: "POST", body: "{}" });
  showLogin();
});

elements.refresh.addEventListener("click", () => loadDashboard(true));
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
    await request("/api/session");
    showDashboard();
    await loadDashboard();
  } catch {
    showLogin();
  }
})();
