# Private GSC dashboard

This is a password-protected Cloudflare Worker with static assets. It lists accessible properties directly from the authenticated Google Search Console account, so it includes old properties even when their local site folders or blogs no longer exist.

Google OAuth values and the dashboard password are stored only as encrypted Worker secrets. They are never committed or sent to the browser.

## Deploy

Use the same shell environment and cached Google OAuth token as `launch.py`:

```bash
npm ci
python scripts/deploy_gsc_dashboard.py
```

The setup command:

1. reads `.deploy/state/google-oauth-token.json` or `GOOGLE_OAUTH_TOKEN_FILE`;
2. asks for a private dashboard password;
3. deploys `seo-gsc-dashboard` to workers.dev;
4. uploads the Google client ID, client secret, refresh token, password, and a generated signing key with `wrangler secret put`.

The Cloudflare token needs `Account > Workers Scripts > Edit`. The cached Google user OAuth grant needs Search Console access. Never paste any of these secrets into `wrangler.jsonc`.

To update an already configured dashboard without replacing its secrets or password:

```bash
git pull
npx wrangler deploy --config dashboard/wrangler.jsonc
```

## Data freshness

- 7-, 28-, and 90-day reports include today in `America/Los_Angeles` (GSC's reporting timezone) and use `dataState: all` to include preliminary data.
- The 24-hour report uses `dataState: hourly_all`, grouped by hour. All properties use the same 24-hour interval ending at the start of the current hour, displayed explicitly in UTC. The API requests the encompassing Pacific calendar dates, then the Worker filters hourly rows to that exact half-open interval. This also handles daylight-saving transitions.
- This is not real-time data. Google's newest hours may be missing or incomplete, and preliminary numbers can change. GSC's own "last available 24 hours" window may differ; compare the displayed time range and Web search type before comparing totals. We do not move a quiet site's window back to its last impression.
- Ordinary loads cache results for five minutes; **Refresh data** bypasses the cache and replaces it. "Oldest fetch" shows the oldest actual Google fetch among loaded properties, not the time you opened the report or Google's processing timestamp.
- Totals are fetched independently of query/page rankings, which can omit anonymized or low-volume rows. Hourly rankings paginate up to 100,000 rows per breakdown; the UI warns when the cap is reached. Rankings are aggregated across hours with impression-weighted position, and the table displays its top 250 rows.

API reference: https://developers.google.com/webmaster-tools/v1/searchanalytics/query

## Local checks

```bash
npm run dashboard:check
npm run dashboard:test
npm run dashboard:dry-run
```

The live dashboard queries each property independently with limited browser concurrency. Pagination is bounded to stay below the Workers Free per-request subrequest limit while allowing progress to render as properties finish.
