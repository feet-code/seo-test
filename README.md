# SEO site automation

This repository is a reusable Next.js static blog template plus a portfolio automation system for launching and monitoring 100+ independent SEO sites.

## One command

After the required API credentials are configured:

```bash
pip install -r requirements.txt
npm install
python scripts/launch.py
```

That command generates the editable 99-idea portfolio, creates/updates site configs, provisions hosting and monitoring, generates posts, builds each site, deploys it, and health-checks the result.

Use a one-site smoke test first:

```bash
python scripts/launch.py --limit 1
```

## Easy frontend/blog redeployment

The Next.js frontend is shared by every site. You do **not** need to copy frontend changes into 99 projects.

After changing files under `src/`, shared assets, or other frontend code:

```bash
python scripts/launch.py --frontend-only
```

This skips Gemini and rebuilds/redeploys the current Markdown for every site.

To regenerate all blog content and redeploy:

```bash
python scripts/launch.py --blogs-only
```

To publish existing/manual Markdown without regenerating it:

```bash
python scripts/launch.py --skip-generation
```

To work on one site:

```bash
python scripts/launch.py --site my-site
```

## Editable idea portfolio

`ideas.json` is deliberately a normal editable file. The first run generates 99 ranked micro-SaaS opportunities. You can delete ideas, edit them, or append your own ideas. Existing `site.json` files are preserved.

The idea prompt prioritizes narrow painful problems, identifiable buyers, recurring revenue, willingness to pay, low infrastructure cost, solo-founder feasibility, and SEO potential. The scores are heuristic AI judgments, not guarantees of profitability.

## Gemini free-model failover

Blog generation automatically cycles through a configurable model list. The current defaults are:

```text
gemini-3.5-flash-lite
gemini-3.1-flash-lite
gemini-2.5-flash-lite
gemini-2.5-flash
```

If a model returns a rate-limit or temporary availability error, it retries briefly and then switches to the next model. Configure the list without editing code:

```bash
GEMINI_MODELS=gemini-3.5-flash-lite,gemini-2.5-flash-lite python scripts/launch.py --blogs-only
```

Google's rate limits are model/project dependent, so failover improves resilience but cannot bypass a quota that is shared by the project. Keep the list to models available on your current free tier. The repository does not use the shut-down Gemini 2.0 models.

## One shared PostHog project

All websites intentionally use **one PostHog project**, which is appropriate for a free-tier portfolio. The first run creates/reuses the project named `SEO Site Portfolio` and stores its public project information in `.deploy/posthog.json` (ignored by git). Every site's frontend receives the same PostHog project key.

Set:

```text
POSTHOG_PERSONAL_API_KEY=...
POSTHOG_ORGANIZATION_ID=...
```

Optional:

```text
POSTHOG_PROJECT_NAME=SEO Site Portfolio
POSTHOG_HOST=https://us.posthog.com
POSTHOG_INGEST_HOST=https://us.i.posthog.com
```

## Deployment providers

The content/build layer is provider-neutral. `out/` remains the portable static artifact.

```bash
python scripts/launch.py --provider cloudflare-pages
python scripts/launch.py --provider cloudflare-workers
python scripts/launch.py --provider vercel
python scripts/launch.py --provider netlify
python scripts/launch.py --provider static
```

Cloudflare Pages projects are created/reused automatically when the Cloudflare API credentials are supplied. Custom domains can be associated when configured, but the automation cannot purchase domains or change registrar DNS that you do not control.

## Monitoring

An hourly GitHub Actions monitor checks every configured site's URL. The launcher also writes per-site deployment state under `.deploy/state/`.

Google Search Console automation requests URL-prefix verification tokens, embeds them in the build, verifies the live property after deployment, adds it to Search Console, and submits `sitemap.xml` when Google credentials are configured.

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
               |                    CF / shared PostHog / GSC
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

## Credentials

Never commit API keys. Use environment variables or CI secrets:

```text
GEMINI_API_KEY=...
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
POSTHOG_PERSONAL_API_KEY=...
POSTHOG_ORGANIZATION_ID=...
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Rotate the Gemini key that was previously committed in the old `geminirequest.py`.
