# SEO portfolio automation

This repository generates and deploys audience-grouped SEO product portfolios. Each website contains the products that belong to one coherent audience; a site may contain one, three, seven, or another useful number of products. Audience fit decides group boundaries, with a maximum-size guardrail rather than an exact product quota.

Every product remains independently measurable through its landing page, blog frontmatter, signup payload, and PostHog properties.

## Main workflow

Install dependencies:

```bash
pip install -r requirements.txt
npm ci
```

Then use the same workflow for 1 product or 100+ products:

```bash
python scripts/ideas.py --generate --count 100
# Inspect/edit ideas/ideas.json; optionally preview with:
python scripts/ideas.py --plan
python scripts/launch.py --limit 1
python scripts/launch.py
```

The first command writes `ideas/ideas.json` and materializes its grouped site configs. Gemini first plans specific audience websites, then generates each website's complementary products. Five products is only a soft target; `--max-products-per-site 8` is the default hard guardrail.

Before deploying, inspect and freely edit the file. Every idea has one authoritative `"siteId"` naming the website/audience group in `sites[]`. To add a product to an existing website, copy an idea object, give it a unique `id`, edit its research fields, and set `siteId`; there is no duplicate `productIds` list to maintain. To create a new website, first add its metadata to `sites[]`, then point one or more ideas at its `id`. `python scripts/ideas.py --plan` validates the file and previews site-config changes without writing them; `launch.py` applies the sync automatically.

### Included editorial batches

This branch already includes a reviewed `ideas/ideas.json` and 970 committed probes for 97 products across 45 audience websites. Batch 001 contributed 10 sites, 22 products, and 220 probes; batch 002 added 20 sites, 42 products, and 420 probes; batch 003 adds 15 sites, 33 products, and 330 probes. Group sizes range from one to three products according to audience fit. The old `example` verification fixture is retired, so it is excluded from bulk launches.

Deploy the included batch directly:

```bash
python scripts/ideas.py --plan
python scripts/launch.py --limit 1
python scripts/launch.py
```

The normal launcher recognizes the committed post fingerprints and does not call Gemini for complete products. Future reviewed batches can be reproduced from each idea's `probeContext` with `python scripts/editorial_probes.py`; use `--site SITE_ID` for one website and `--force` only when intentionally replacing that site's existing probes.

Idea generation checkpoints after every audience group in `.deploy/state/ideas-generation.json`. Rerun the same `--generate` command to resume. Use `--regenerate` only when you intentionally want a completely new portfolio:

```bash
python scripts/ideas.py --regenerate --count 100
```

The second command runs the complete production pipeline for one site: product posts, build, deployment, Google verification/`sites.add`, sitemap submission, and health check. Only after it passes should you run the third command. The full run safely skips already-complete product generation by fingerprint, so the smoke-tested site does not consume duplicate Gemini work.

A failed deployment stops and writes a separate launch checkpoint. After fixing the failure, resume with the same selection flags. For a full rollout:

```bash
python scripts/launch.py --resume
```

For the one-site smoke test, use `python scripts/launch.py --limit 1 --resume`.

For a no-network smoke test:

```bash
python -m unittest discover -s tests -v
python scripts/ideas.py --mock
python scripts/launch.py --mock --provider static --site freelancer-operations
```

`--mock` makes no Gemini, monitoring, or deployment API calls.

## Optional NicheScout import

`seo-test` can generate its own portfolio, but a NicheScout export remains supported as an optional research source:

```bash
python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json --plan
python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json
```

## Safe portfolio sync

The sync step validates unique IDs, idea `siteId` references, variable-size groups, and legacy `productIds` imports. `--plan` performs no writes.

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
META token -> deploy -> wait for public token -> verify ownership -> sites.add -> submit sitemap
```

Cloudflare's production alias and Google's verifier can observe a new deployment at different times. The launcher therefore waits until the exact META token is visible at the public URL, then retries only Google's specific “verification token could not be found” response. The default shared deadline is five minutes; set `GOOGLE_VERIFICATION_TIMEOUT_SECONDS=600` if a custom domain or host propagates more slowly. Progress is printed during the wait, so a normal bulk launch should not require repeated `--resume` commands.

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
seo-test generation or optional NicheScout research
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
