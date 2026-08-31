# SEO portfolio automation

This repository generates and deploys profitability-first SEO product probes. The default generator selects independent micro-SaaS hypotheses at the intersection of direct economic value and attainable organic-search demand. Every generated idea gets its own website; ideas are never weakened or discarded to make an audience group work.

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

The first command uses Google Search-grounded Gemini calls in restart-safe five-idea batches, writes `ideas/ideas.json` only after all 100 ideas pass validation, and materializes one site config per idea. It silently considers at least four candidates per finalist and scores each result on a 50-point profit, 40-point SEO, and 10-point build/support feasibility model. SEO qualification separately covers demand, commercial intent, content depth, and SERP winnability; each finalist needs six concrete query hypotheses and a ranking thesis.

Before deploying, inspect and freely edit the file. Every generated idea has one authoritative `"siteId"` matching its own entry in `sites[]`. `python scripts/ideas.py --plan` validates the file and previews site-config changes without writing them; `launch.py` applies the sync automatically. Legacy imported portfolios may still place several products on one site, but the built-in generator does not optimize for grouping.

### Included profitability portfolio and probes

This branch contains 100 independent ideas selected from 109 curated candidates. Every idea has a direct economic driver, monetization hypothesis, explicit buyer, six query hypotheses, SEO thesis, score breakdown, and structured `probeContext`.

The 100 one-product site configs and 340 editorial probes are committed. Each site has an indexable product page plus 2–5 articles selected from the idea's reviewed SEO content depth: 2 ideas have 2 posts, 60 have 3, 34 have 4, and 4 have 5. The planner prioritizes the useful search intents available for that product—decision model, buying guide, implementation, mistakes, and alternatives—without padding the corpus to a quota. Probes use normal headings and lists rather than Markdown tables or pipe characters.

Validate or intentionally rebuild the reviewed corpus with:

```bash
python scripts/ideas.py --plan
python scripts/ideas.py
python scripts/editorial_probes.py --batch profitability-001
```

The normal launcher recognizes the committed probes and only generates content that is missing or invalidated by a changed input. Reviewed batches can be reproduced from each idea's `probeContext` with `python scripts/editorial_probes.py --batch BATCH_ID`; use `--site SITE_ID` for one website and `--force` only when intentionally replacing existing probes.

Idea generation checkpoints after every independent batch in `.deploy/state/ideas-generation.json`. Rerun the same `--generate` command to resume. Use `--regenerate` only when you intentionally want a completely new portfolio:

```bash
python scripts/ideas.py --regenerate --count 100
```

The one-site launch runs the complete production pipeline: product posts, build, deployment, Google verification/`sites.add`, sitemap submission, and health check. Only after it passes should you run the full launch. The full run safely skips already-complete product generation by fingerprint, so the smoke-tested site does not consume duplicate Gemini work.

A failed deployment stops and writes a separate launch checkpoint. After fixing the failure, resume with the same selection flags. A plain resume skips checkpoint sites that have since been deleted or retired and keeps progress by site ID, so pruning the portfolio does not restart completed deployments. For a full rollout:

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
- preserved from `sites/<site-id>/site.json`: domain, hosting project/provider, signup, GSC/PostHog state, author name, lifecycle status, and article count.

Blog photos are intentionally disabled. Existing Markdown has no cover, author-picture, Open Graph image, Markdown-image, or HTML-image data; both generators enforce the same rule for future posts. Future model-generated prose also strips pipe-based table formatting and renders comparisons as headings and lists. Run `python scripts/remove_blog_images.py` after importing older content to make it image-free.

Sites missing from a newer export are reported as `STALE (kept)`. They are never silently deleted. Review them and explicitly retire or tear them down.

## Launch modes

```bash
python scripts/launch.py --site site-a
python scripts/launch.py --sites site-a,site-b
python scripts/launch.py --batch profitability-001
python scripts/launch.py --batches BATCH_A,BATCH_B
python scripts/launch.py --batch profitability-001 --limit 1
python scripts/launch.py --limit 1
python scripts/launch.py --frontend-only --site site-a
python scripts/launch.py --product product-id
python scripts/launch.py --blogs-only --site site-a
python scripts/launch.py --skip-generation --site site-a
```

A normal launch always invokes the restart-safe product generator. Products whose input fingerprint and required post count are complete are skipped. If one product's audience, problem, value proposition, topic, or SEO angle changes, only that product regenerates.

`--product product-id` finds the containing site, force-regenerates that product, then builds, deploys, registers, and checks that site.

`--limit 1` selects one site but still runs its complete pipeline, including Gemini for missing or changed products. Use `--frontend-only --limit 1` when only shared frontend/configuration changed.

`--batch` selects every website containing at least one product with that `contentBatch`. `--batches` unions several batches, and each affected website deploys only once. `--limit` is applied after batch selection, which makes `--batch profitability-001 --limit 1` the smoke test for this portfolio. A plain `--resume` restores the exact site subset saved by the failed run; repeating the batch flags is also valid.

`--blogs-only` force-regenerates all selected product posts. `--skip-generation` and `--frontend-only` publish existing Markdown.

## Product-attributed probes

For every product, the build creates:

- an indexable `/products/<product-id>` landing page;
- only that product's guides on its landing page;
- product-specific signup attribution;
- sitemap entries for product pages and posts;
- PostHog events `product_probe_viewed` and `product_interest_submitted`;
- cross-discovery links when a legacy imported site contains complementary products.

Generated post frontmatter includes `productId`, `productName`, and a generation fingerprint. It deliberately contains no image metadata.

Every product page states the target buyer, economic case, validation hypothesis, primary risk, and pricing hypothesis. This keeps each probe commercially specific while the related articles target narrow, rankable search decisions.

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
python scripts/launch.py --provider auto
python scripts/launch.py --provider cloudflare-pages
python scripts/launch.py --provider cloudflare-workers
python scripts/launch.py --provider vercel
python scripts/launch.py --provider netlify
python scripts/launch.py --provider static
```

New portfolio sites default to `cloudflare-auto`. The launcher first reuses a persisted provider or an existing Pages project. For a genuinely new site it reads the account's Pages project count: below the configured guardrail it creates Pages, at the limit it deploys the static export as an individual Worker on `*.workers.dev`. If Cloudflare returns capacity error `8000027`, the same run falls back to Workers even for an older config that explicitly named `cloudflare-pages`. The observed account limit is persisted so later sites go straight to Workers instead of repeating failed Pages creates; it is cleared automatically if the project count later drops. The resolved provider and exact URL are written to `site.json`, so redeploy, GSC verification, health checks, resume, and teardown all use the same host.

Cloudflare documents a 100-project Pages account limit and separate Worker limits. `CLOUDFLARE_PAGES_PROJECT_LIMIT=100` is the default and can be lowered for a controlled migration test. Workers deployment requires `Account > Workers Scripts > Edit` on `CLOUDFLARE_API_TOKEN`. The launcher does not list every script during provider selection. It discovers the account's existing workers.dev subdomain; set `CLOUDFLARE_WORKERS_SUBDOMAIN=name` only to override that lookup. The override does not replace the Workers Scripts permission required to deploy. Custom domains must already be owned and controlled by you.

## Credentials

Never commit credentials:

```text
GEMINI_API_KEY=...
GEMINI_MODELS=gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-2.5-flash
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_WORKERS_SUBDOMAIN=...  # optional override
CLOUDFLARE_PAGES_PROJECT_LIMIT=100  # optional test/guardrail override
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
independent profit + SEO finalists in ideas/ideas.json
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
