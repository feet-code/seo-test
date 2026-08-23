# SEO site automation

This repository is a reusable Next.js static blog template plus a portfolio automation system for launching and monitoring 100+ independent SEO sites.

## One command

After the required API credentials are configured:

```bash
pip install -r requirements.txt
npm install
python scripts/launch.py
```

That command:

1. asks Gemini for exactly 99 ranked micro-SaaS opportunities when `ideas.json` does not exist;
2. writes the ideas to **editable `ideas.json`**;
3. creates one `sites/<site-id>/site.json` for every idea without overwriting existing/manual configs;
4. creates/reuses Cloudflare Pages projects and associates custom domains when Cloudflare credentials are available;
5. provisions/reuses one PostHog project per site and injects its public project key into each static build;
6. requests Google Search Console URL-prefix verification tokens, embeds them in each build, verifies the live sites, and submits `sitemap.xml`;
7. generates 3–10 SEO articles per site with Gemini when that site's `_posts/` is empty;
8. builds each site independently to `out/`;
9. deploys each site to the selected provider;
10. health-checks every deployed site and writes `.deploy/state/summary.json`.

Cloudflare Pages Direct Upload projects can be created programmatically through the Cloudflare API, then deployed with Wrangler. No manual Pages-project creation step is required when the Cloudflare API credentials are configured.

## Editable idea portfolio

`ideas.json` is deliberately a normal editable file. The first run generates 99 ideas. You can delete ideas, edit them, or append your own ideas. Existing `site.json` files are never overwritten by the idea materializer.

To intentionally regenerate the 99 AI ideas:

```bash
python scripts/ideas.py --regenerate
```

This replaces `ideas.json`, so only use it when you want to discard your edits.

Each generated site has its own config:

```text
sites/<site-id>/site.json
sites/<site-id>/_posts/*.md
```

The idea prompt prioritizes narrow painful problems, identifiable buyers, recurring revenue, willingness to pay, low infrastructure cost, solo-founder feasibility, and SEO acquisition. The scores are heuristic AI judgments, not guarantees of profitability.

## Credentials

Set these as environment variables/secrets and never commit them:

```text
GEMINI_API_KEY=...
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
POSTHOG_PERSONAL_API_KEY=...
POSTHOG_ORGANIZATION_ID=...
POSTHOG_HOST=https://us.posthog.com
POSTHOG_INGEST_HOST=https://us.i.posthog.com
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Google automation requires a Google service account with the Site Verification and Search Console APIs enabled. The service account is the authenticated Google identity used for verification and Search Console API operations.

For custom domains, the domain must actually be owned/configured by you. The automation can associate a domain with the Cloudflare Pages project, but it cannot buy a domain you do not own.

## Deployment providers

The content/build layer is provider-neutral. `out/` is the portable static artifact.

```bash
python scripts/launch.py --provider cloudflare-pages
python scripts/launch.py --provider cloudflare-workers
python scripts/launch.py --provider vercel
python scripts/launch.py --provider netlify
python scripts/launch.py --provider static
```

Cloudflare Pages is the default because it supports programmatic Direct Upload project creation. Cloudflare Workers uses Wrangler static assets. Vercel and Netlify use their CLIs.

Use `--limit 1` for a smoke test before launching the whole portfolio:

```bash
python scripts/launch.py --limit 1
```

## Monitoring

An hourly GitHub Actions workflow runs `scripts/monitor.py` and checks every configured site's URL. The launcher also writes per-site deployment status under `.deploy/state/`.

PostHog provides site analytics once its project is provisioned. Google Search Console is automatically verified and the sitemap submitted when Google credentials are configured.

## Architecture

```text
                    Gemini: 99 micro-SaaS ideas
                              |
                              v
                         ideas.json
                    (human editable)
                              |
                              v
                    sites/*/site.json
                              |
               +--------------+--------------+
               |                             |
               v                             v
        Gemini SEO posts                Monitoring setup
               |                    CF / PostHog / GSC
               v                             |
        sites/*/_posts                       |
               |                             |
               +--------------+--------------+
                              v
                        Next.js build
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

## Security

Rotate the Gemini key that was previously committed in the old `geminirequest.py`. API credentials belong in environment variables or CI secrets only.
