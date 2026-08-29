# Portfolio operating workflows

Run commands from the repository root. Start with `python scripts/portfolio.py status` whenever you are unsure which sites are active.

## Command map

| Goal | Command | What it changes |
|---|---|---|
| Generate/resume 100 products | `python scripts/ideas.py --generate --count 100` | `ideas/ideas.json`, generation checkpoint, managed site/product fields |
| Intentionally start over | `python scripts/ideas.py --regenerate --count 100` | Replaces the generation checkpoint and, after success, `ideas/ideas.json` |
| Validate/preview manual edits | `python scripts/ideas.py --plan` | Nothing |
| Preview a NicheScout handoff | `python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json --plan` | Nothing |
| Apply a handoff | `python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json` | Portfolio file and managed site/product fields |
| Smoke-test one generated site | `python scripts/launch.py --limit 1` | Complete pipeline for the first active site |
| Deploy every active site | `python scripts/launch.py` | Complete pipeline, skipping unchanged product generation |
| Deploy one site | `python scripts/launch.py --site SITE_ID` | Changed/missing product content, frontend, hosting, GSC |
| Deploy a batch | `python scripts/launch.py --limit 10` | Full pipeline for the first ten active sites |
| Resume a stopped batch | `python scripts/launch.py --resume` | Continues from saved site/product checkpoints |
| Publish a shared UI change | `python scripts/launch.py --frontend-only` | Every active site, no Gemini |
| Rebuild one UI/config change | `python scripts/launch.py --frontend-only --site SITE_ID` | One site, no Gemini |
| Regenerate one product | `python scripts/launch.py --product PRODUCT_ID` | That product's posts and containing site |
| Regenerate all posts on a site | `python scripts/launch.py --blogs-only --site SITE_ID` | Every product's posts on that site |
| Pause future automation | `python scripts/portfolio.py retire SITE_ID` | Local status only; deployment stays live |
| Resume a paused site | `python scripts/portfolio.py activate SITE_ID` | Local status; launch separately |
| Preview one teardown | `python scripts/portfolio.py teardown SITE_ID` | Nothing |
| Preview full teardown | `python scripts/portfolio.py teardown --all` | Nothing |

## Initial 100+ product rollout

Generate the durable portfolio handoff:

```bash
python scripts/ideas.py --generate --count 100
python scripts/portfolio.py status
```

Review the site count and product distribution in `ideas/ideas.json`. Counts vary because audience fit closes or grows a website; five is only a soft preferred size. To change the guardrails for a new run:

```bash
python scripts/ideas.py --regenerate --count 150 \
  --preferred-products-per-site 4 --max-products-per-site 7
```

An interrupted idea run is safe to resume with the exact same `--generate` command. `ideas/ideas.json` is replaced atomically only after every audience group is complete.

Before deploying, inspect `ideas/ideas.json`. Each idea's `siteId` is its single source of truth for website membership. You can change copy, add ideas, remove ideas, or move an idea to another existing audience website without editing a second membership list. Run `python scripts/ideas.py --plan` after manual edits; the launcher applies the same validated sync automatically.

Deploy one site end to end before starting the batch:

```bash
python scripts/launch.py --limit 1
python scripts/launch.py
```

The first real run opens Google OAuth once. It includes post generation, so it is a real production smoke test rather than a frontend-only preview. If that smoke test fails, fix it and run `python scripts/launch.py --limit 1 --resume`. During the full rollout, resume with `python scripts/launch.py --resume`.

If you prefer NicheScout's research pipeline, import its finalized export instead of running `--generate`:

```bash
python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json --plan
python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json
```

## Change an idea, audience, or grouping

Edit `ideas/ideas.json`, not a generated site's managed product fields.

For a copy/product change:

1. Edit the idea.
2. Run `python scripts/ideas.py --plan`.
3. Run `python scripts/ideas.py`.
4. Run `python scripts/launch.py --site SITE_ID`.

The fingerprint checkpoint regenerates only products whose generation inputs changed.

For regrouping, change only the idea's `siteId`. Preview and apply the sync, then deploy both the old and new site. A full generator run removes attributed posts for products no longer assigned to the old site.

To add an idea to an existing website, copy an idea object and edit its unique `id`, `name`, `product`, `audience`, `problem`, `valueProposition`, `topic`, and `siteId` (plus the research fields you want to preserve). To create a new website, also add one `sites[]` object with a unique `id`, `name`, `audience`, and `topic`; point the new ideas' `siteId` at it. Generated files do not contain `productIds`. Older imported portfolios that do are still supported, with an idea's explicit `siteId` taking precedence.

If an export omits a whole site, sync reports `STALE (kept)`. Decide explicitly whether to retain, retire, or tear it down.

## Change the shared frontend

Edit the Next.js source, test one representative site, then roll out:

```bash
python scripts/launch.py --mock --provider static --site freelancer-operations
python scripts/launch.py --frontend-only --site SITE_ID
python scripts/launch.py --frontend-only
```

`--frontend-only` never calls Gemini. It still deploys, completes GSC registration/sitemap submission, and health-checks each site.

## Change domain, signup, hosting, or article count

Edit `sites/SITE_ID/site.json`. These site-local fields survive portfolio imports:

```json
{
  "domain": "tools.example.com",
  "articlesPerProduct": 6,
  "signup": {"endpoint": "https://example.com/subscribe"},
  "deploy": {"provider": "cloudflare-pages", "project": "stable-project"}
}
```

For domain/signup/presentation changes, use `python scripts/launch.py --frontend-only --site SITE_ID`.

For an article-count change, run the normal launch. Products below the new count regenerate; use `--blogs-only` to replace every probe.

## Change one product's posts immediately

```bash
python scripts/launch.py --product PRODUCT_ID
```

The launcher finds its site, force-regenerates only that product, rebuilds the static site, redeploys it, and refreshes GSC/sitemap state.

## Pause and reactivate

Retirement is reversible and does not take the deployment offline:

```bash
python scripts/portfolio.py retire SITE_ID
python scripts/portfolio.py activate SITE_ID
python scripts/launch.py --site SITE_ID
```

Retired sites are excluded from launch, bulk build, and health checks. A destroyed site can also be activated; the next launch recreates hosting and Google resources.

## Take down one site

Preview first:

```bash
python scripts/portfolio.py teardown SITE_ID
```

The preview prints the exact confirmation command. Executing it removes the URL-prefix property from GSC, the matching Google Site Verification ownership record, and the Cloudflare Pages project/domain attachment.

It does not delete the registered domain/DNS zone, shared PostHog project, source, local posts, or site config. The config is marked `destroyed` only after external deletion succeeds.

## Take down every deployed site

Preview the exact set:

```bash
python scripts/portfolio.py teardown --all
```

Review every target, then use the printed `--confirm DESTROY-ALL` command. Teardown reports partial failures; successful sites are marked destroyed while failed sites remain retryable. Commit lifecycle/config changes afterward so the repository remains the audit record.
