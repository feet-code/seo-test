# Private GSC dashboard

This is a password-protected Cloudflare Worker with static assets. It lists URL-prefix properties directly from the authenticated Google Search Console account, so it includes old properties even when their local site folders or blogs no longer exist.

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

## Local checks

```bash
npm run dashboard:check
npm run dashboard:dry-run
```

The live dashboard queries each property independently with limited browser concurrency. This stays below the Workers Free per-request subrequest limit while allowing progress to render as properties finish. Property results are cached at the edge for 15 minutes.
