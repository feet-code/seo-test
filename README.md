# SEO site automation

This repository is a shared static blog generator and portfolio automation system for launching and monitoring 100+ independent SEO sites.

## One command

After credentials are configured:

```bash
pip install -r requirements.txt
npm install
python scripts/launch.py
```

Use a safe local/mock smoke test first. It does not call Gemini or external monitoring APIs:

```bash
python scripts/launch.py --mock --provider static --limit 1
```

## Editable ideas

The editable portfolio lives at `ideas/ideas.json`. The repository includes **one example idea** so you can copy its structure and manually add ideas. If `ideas/ideas.json` exists, the launcher does not generate a new idea list. Existing `sites/*/site.json` files are never overwritten.

If you intentionally want AI to create the 99-idea portfolio later, use:

```bash
python scripts/ideas.py --regenerate
```

For a deterministic example without an LLM:

```bash
python scripts/ideas.py --mock
```

## Deploy a subset

```bash
python scripts/launch.py --site my-site
python scripts/launch.py --site site-a --site site-b --site site-c
python scripts/launch.py --sites site-a,site-b,site-c
python scripts/launch.py --limit 5
```

## Easy redeployment

All sites share the same frontend code. Change the frontend, then:

```bash
python scripts/launch.py --frontend-only
```

This rebuilds/redeploys every selected site without calling Gemini. To regenerate blog content:

```bash
python scripts/launch.py --blogs-only
```

To publish existing/manual Markdown without regeneration:

```bash
python scripts/launch.py --skip-generation
```

Use `--mock` with any of these modes for fast iteration without LLM or monitoring API calls.

## Gemini model failover and resume

Blog generation automatically cycles through `GEMINI_MODELS` (or the default free-tier-capable list) when a model is rate-limited or temporarily unavailable. Configure the order with:

```text
GEMINI_MODELS=gemini-2.5-flash-lite,gemini-2.5-flash
```

If every configured model fails for a site, the process **terminates immediately** instead of silently skipping sites. It persists `.deploy/state/checkpoint.json` with the exact site/idea index where it stopped. After credits/rate limits recover:

```bash
python scripts/launch.py --resume
```

The launcher continues from that site. This also works with a selected subset when the same subset is supplied again.

## Product-interest email signup

Every site config can contain:

```json
"signup": {
  "enabled": true,
  "headline": "Interested? Get notified when this is available.",
  "endpoint": "https://your-form-endpoint.example/subscribe",
  "email": "hello@example.com"
}
```

The generated site displays an email signup form. If `endpoint` is configured, it POSTs `{ "email": "...", "product": "..." }` as JSON. If no endpoint is configured but `email` is present, it opens a pre-filled email message instead. This keeps the frontend static and lets you use any email/form backend you choose.

## Monitoring

All sites use **one shared PostHog project**, suitable for a free-tier portfolio. Google Search Console verification and sitemap submission are automated when Google credentials are configured. An hourly GitHub Actions workflow health-checks configured sites.

## Deployment

The build produces a portable `out/` static artifact. Deployment adapters support:

```bash
python scripts/launch.py --provider cloudflare-pages
python scripts/launch.py --provider cloudflare-workers
python scripts/launch.py --provider vercel
python scripts/launch.py --provider netlify
python scripts/launch.py --provider static
```

Cloudflare Pages projects are created/reused automatically when the required Cloudflare API credentials are supplied. Custom domains can be associated when configured, but domains must already be owned/controlled by you.

## Credentials

Never commit credentials:

```text
GEMINI_API_KEY=...
GEMINI_MODELS=gemini-2.5-flash-lite,gemini-2.5-flash
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
POSTHOG_PERSONAL_API_KEY=...
POSTHOG_ORGANIZATION_ID=...
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Rotate the Gemini key that was previously committed in the old generator.

## Architecture

```text
                 ideas/ideas.json (human editable)
                              |
                    optional AI generation of 99
                              |
                              v
                     sites/*/site.json
                              |
               +--------------+--------------+
               |                             |
               v                             v
         Gemini SEO posts             Monitoring setup
               |                 shared PostHog / GSC
               v                             |
        sites/*/_posts                       |
               +--------------+--------------+
                              v
                        static build
                              |
                              v
                            out/
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
      Cloudflare           Vercel              Netlify
      Pages/Workers
                              |
                              v
                    hourly health monitoring
```
