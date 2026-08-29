# SEO portfolio automation

This repository deploys NicheScout finalists as audience-grouped SEO portfolios. Each website contains the products that belong to one coherent audience; a site may contain one, three, seven, or another useful number of products. NicheScout decides group boundaries from audience similarity and a maximum-size guardrail, not an exact product quota.

Every product remains independently measurable through its landing page, blog frontmatter, signup payload, and PostHog properties.

## First deployment

Install dependencies:

```bash
pip install -r requirements.txt
npm ci
```

Preview and import the latest NicheScout export:

```bash
python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json --plan
python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json
python scripts/portfolio.py status
```

Deploy one audience portfolio first, then all remaining active sites:

```bash
python scripts/launch.py --site <site-id>
python scripts/launch.py
```

A failed run stops and writes a checkpoint. After fixing the failure, resume the same selected set with:

```bash
python scripts/launch.py --resume
```

For a no-network smoke test:

```bash
python -m unittest discover -s tests -v
python scripts/ideas.py --mock
python scripts/launch.py --mock --provider static --site freelancer-operations
```

`--mock` makes no Gemini, monitoring, or deployment API calls.

## Safe portfolio sync

The importer validates unique IDs, non-empty variable-size groups, `siteId`/`productIds` consistency, and orphaned products. `--plan` performs no writes.

Repeated imports update portfolio-managed content while preserving site-local operations:

- updated from `ideas.json`: site name, audience, topic, product membership, and product research/copy;
- preserved from `sites/<site-id>/site.json`: domain, hosting project/provider, signup, GSC/PostHog state, author/images, lifecycle status, and article count.

Sites missing from a newer export are reported as `STALE (kept)`. They are never silently deleted. Review them and explicitly retire or tear them down.

## Launch modes

```bash
python scripts/launch.py --site site-a
python scripts/launch.py --sites site-a,site-b
python scripts/launch.py --limit 1
python scripts/launch.py --frontend-only --site site-a
python scripts/launch.py --product product-id
python scripts/launch.py --blogs-only --site site-a
python scripts/launch.py --skip-generation --site site-a
```

A normal launch always invokes the restart-safe product generator. Products whose input fingerprint and required post count are complete are skipped. If one product's audience, problem, value proposition, topic, or SEO angle changes, only that product regenerates.

`--product product-id` finds the containing site, force-regenerates that product, then builds, deploys, registers, and checks that site.

`--limit 1` selects one site but still runs its complete pipeline, including Gemini for missing or changed products. Use `--frontend-only --limit 1` when only shared frontend/configuration changed.

`--blogs-only` force-regenerates all selected product posts. `--skip-generation` and `--frontend-only` publish existing Markdown.

## Product-attributed probes

For every product, the build creates:

- an indexable `/products/<product-id>` landing page;
- only that product's guides on its landing page;
- product-specific signup attribution;
- sitemap entries for product pages and posts;
- PostHog events `product_probe_viewed` and `product_interest_submitted`;
- cross-discovery links to complementary products on the same audience site.

Generated post frontmatter includes `productId`, `productName`, and a generation fingerprint.

## Google Search Console

Use desktop OAuth so verification, `sites.add`, and sitemap submission run as the same Google account visible in Search Console. Enable the Google Site Verification API and Search Console API, create a Desktop app OAuth client, then set:

```text
GOOGLE_OAUTH_CLIENT_SECRETS=/path/to/oauth-client.json
```

The first real launch opens one browser authorization. Choose the Google account you use in Search Console. Its refresh token is cached under `.deploy/state/`, so the remaining sites run unattended:

```text
META token -> deploy -> verify ownership -> sites.add -> submit sitemap
```

You do not register every site manually. Each successful launch calls `sites.add` for the exact URL-prefix property, so it appears in that OAuth user's GSC account.

A service account remains supported with `GOOGLE_APPLICATION_CREDENTIALS`, but its properties do not automatically appear in a human account. `GOOGLE_SEARCH_CONSOLE_OWNER_EMAIL` can delegate verified ownership; desktop OAuth is preferred.

## Deployment providers

The build produces a static `out/` artifact:

```bash
python scripts/launch.py --provider cloudflare-pages
python scripts/launch.py --provider cloudflare-workers
python scripts/launch.py --provider vercel
python scripts/launch.py --provider netlify
python scripts/launch.py --provider static
```

Cloudflare Pages projects are created or reused automatically. Custom domains must already be owned and controlled by you.

## Credentials

Never commit credentials:

```text
GEMINI_API_KEY=...
GEMINI_MODELS=gemini-3.5-flash-lite,gemini-3.1-flash-lite,gemini-2.5-flash-lite,gemini-2.5-flash
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
POSTHOG_PROJECT_ID=...
POSTHOG_PROJECT_API_KEY=...
GOOGLE_OAUTH_CLIENT_SECRETS=/path/to/desktop-oauth-client.json
GOOGLE_OAUTH_TOKEN_FILE=/optional/path/to/oauth-token.json
GOOGLE_SEARCH_CONSOLE_OWNER_EMAIL=you@example.com
```

All sites intentionally share one configured PostHog project.

## Editing, redeploying, and teardown

See [OPERATIONS.md](OPERATIONS.md) for exact workflows covering portfolio updates, shared frontend changes, product-only regeneration, domain changes, pause/reactivate, one-site teardown, and confirmed teardown of all external sites.

Safe lifecycle commands:

```bash
python scripts/portfolio.py status
python scripts/portfolio.py retire <site-id>
python scripts/portfolio.py activate <site-id>
python scripts/portfolio.py teardown <site-id>
python scripts/portfolio.py teardown --all
```

`teardown` is preview-only unless the exact confirmation printed by the command is supplied. It preserves local configs and content as an audit/redeployment source.

## Architecture boundary

```text
NicheScout research
        |
        v
variable audience groups in ideas/ideas.json
        |
        v
safe site-config sync
        |
        v
product-attributed posts + landing pages
        |
        v
build -> hosting -> GSC + PostHog + signups
```
