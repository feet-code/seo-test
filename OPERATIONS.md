# Portfolio operating workflows

Run commands from the repository root. Start with `python scripts/portfolio.py status` whenever you are unsure which sites are active.

## Command map

| Goal | Command | What it changes |
|---|---|---|
| Generate/resume 100 products | `python scripts/ideas.py --generate --count 100` | `ideas/ideas.json`, generation checkpoint, managed site/product fields |
| Intentionally start over | `python scripts/ideas.py --regenerate --count 100` | Replaces the generation checkpoint and, after success, `ideas/ideas.json` |
| Validate/preview manual edits | `python scripts/ideas.py --plan` | Nothing |
| Rebuild reviewed probes from `probeContext` | `python scripts/editorial_probes.py --batch BATCH_ID` | Missing 2–5 planned posts per product in that editorial batch |
| Preview a NicheScout handoff | `python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json --plan` | Nothing |
| Apply a handoff | `python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json` | Portfolio file and managed site/product fields |
| Smoke-test one generated site | `python scripts/launch.py --limit 1` | Complete pipeline for the first active site |
| Deploy every active site | `python scripts/launch.py` | Complete pipeline, skipping unchanged product generation |
| Deploy one site | `python scripts/launch.py --site SITE_ID` | Changed/missing product content, frontend, hosting, GSC |
| Smoke-test a batch | `python scripts/launch.py --batch BATCH_ID --limit 1` | Complete pipeline for the first site in that batch |
| Deploy one batch | `python scripts/launch.py --batch BATCH_ID` | Only websites containing that `contentBatch` |
| Deploy several batches | `python scripts/launch.py --batches BATCH_A,BATCH_B` | Union of affected websites, each deployed once |
| Resume a stopped batch | `python scripts/launch.py --resume` | Continues the saved subset, skipping sites deleted or retired since the checkpoint |
| Export top GSC results | `python scripts/gsc_report.py` | CSV/JSON rankings across every accessible GSC URL-prefix property, including deleted local sites |
| Deploy private GSC dashboard | `python scripts/deploy_gsc_dashboard.py` | Password-protected workers.dev dashboard using encrypted Google OAuth secrets |
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

Review all candidates, scores, query hypotheses, and risks in `ideas/ideas.json`. The default output is exactly one product per website. To change the restart-safe call size for a new run:

```bash
python scripts/ideas.py --regenerate --count 150 --batch-size 5
```

An interrupted idea run is safe to resume with the exact same `--generate` command. `ideas/ideas.json` is replaced atomically only after every independent batch is complete.

The committed `profitability-001` portfolio already includes 100 site configs, one product page per site, and 340 reviewed probes. Per-product counts range from 2–5 according to reviewed SEO content depth. Rebuild them only when you intend to replace or repair the committed corpus:

```bash
python scripts/editorial_probes.py --batch profitability-001
```

Editorial probes and future Gemini output use headings and lists for comparisons. Markdown tables and pipe characters are rejected or normalized before posts are written.

Before deploying, inspect `ideas/ideas.json`. Each idea's `siteId` is its single source of truth for website membership. You can change copy, add ideas, remove ideas, or move an idea to another existing audience website without editing a second membership list. Run `python scripts/ideas.py --plan` after manual edits; the launcher applies the same validated sync automatically.

Deploy one site end to end before starting the batch:

```bash
python scripts/launch.py --limit 1
python scripts/launch.py
```

For a reviewed editorial batch, scope both commands so unrelated websites are not redeployed:

```bash
python scripts/launch.py --batch profitability-001 --limit 1
python scripts/launch.py --batch profitability-001
```

Batch membership comes from each idea's `contentBatch`. A site shared by two selected batches is built and deployed once. `--limit` applies after batch selection. If a run stops, plain `--resume` restores the checkpoint's site list; you may also repeat the original batch flags.

The first real run opens Google OAuth once. It includes post generation, so it is a real production smoke test rather than a frontend-only preview. If that smoke test fails, fix it and run `python scripts/launch.py --limit 1 --resume`. During the full rollout, resume with `python scripts/launch.py --resume`.

If you prefer NicheScout's research pipeline, import its finalized export instead of running `--generate`:

```bash
python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json --plan
python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json
```

## Change an idea or its site

Edit `ideas/ideas.json`, not a generated site's managed product fields.

For a copy/product change:

1. Edit the idea.
2. Run `python scripts/ideas.py --plan`.
3. Run `python scripts/ideas.py`.
4. Run `python scripts/launch.py --site SITE_ID`.

The fingerprint checkpoint regenerates only products whose generation inputs changed.

Generated portfolios use one product per site, so change the matching idea and site records together if you rename an ID. Legacy imported portfolios can still be regrouped by changing an idea's `siteId`; preview and apply the sync, then deploy both affected sites.

To add an idea to an existing website, copy an idea object and edit its unique `id`, `name`, `product`, `audience`, `problem`, `valueProposition`, `topic`, and `siteId` (plus the research fields you want to preserve). To create a new website, also add one `sites[]` object with a unique `id`, `name`, `audience`, and `topic`; point the new ideas' `siteId` at it. Generated files do not contain `productIds`. Older imported portfolios that do are still supported, with an idea's explicit `siteId` taking precedence.

If an export omits a whole site, sync reports `STALE (kept)`. Decide explicitly whether to retain, retire, or tear it down.

## Change the shared frontend

Edit the Next.js source, test one representative site, then roll out:

```bash
python scripts/launch.py --mock --provider static --site freelancer-operations
python scripts/launch.py --frontend-only --site SITE_ID
python scripts/launch.py --frontend-only
```

To roll a shared change to only one editorial cohort, add `--batch BATCH_ID` to the last two commands.

`--frontend-only` never calls Gemini. It still deploys, completes GSC registration/sitemap submission, and health-checks each site.

After each deploy, the launcher waits for the exact Google META token at the public production URL and retries Google's token-not-found response within a five-minute deadline. This absorbs normal Pages/Google propagation delays without stopping the batch. For unusually slow custom-domain propagation, increase the deadline before launching:

```bash
# PowerShell
$env:GOOGLE_VERIFICATION_TIMEOUT_SECONDS="600"
python scripts/launch.py --resume

# bash/zsh
GOOGLE_VERIFICATION_TIMEOUT_SECONDS=600 python scripts/launch.py --resume
```

## Change domain, signup, hosting, or article count

Edit `sites/SITE_ID/site.json`. These site-local fields survive portfolio imports:

```json
{
  "domain": "tools.example.com",
  "articlesPerProduct": 4,
  "products": [{"probeArticleCount": 4}],
  "signup": {"endpoint": "https://example.com/subscribe"},
  "deploy": {"provider": "cloudflare-auto", "project": "stable-project"}
}
```

`cloudflare-auto` is the default for new sites. It preserves an already resolved host; otherwise it reuses an existing Pages project, creates Pages while the account is below its configured or observed project cap, and assigns overflow to Workers Static Assets on `*.workers.dev`. Cloudflare error `8000027` triggers the Workers fallback immediately, records the observed cap, and routes later new sites directly to Workers. If the live Pages count falls below that observed cap, the marker is cleared. The resulting `resolvedProvider` and `url` are saved in the config.

You can select `cloudflare-pages` or `cloudflare-workers`, or override a run with `--provider`; a Pages capacity rejection still falls back safely to Workers. A Workers-capable API token needs `Account > Workers Scripts > Edit` for the selected account. Provider selection does not require listing all Worker scripts. If account-subdomain discovery is unavailable, set `CLOUDFLARE_WORKERS_SUBDOMAIN` to the part before `.workers.dev` and resume; the override does not replace the deploy permission.

## Keep blogs image-free

Both content generators omit image frontmatter and remove model-produced Markdown or HTML image tags. The Next.js frontend has no cover-image, avatar-image, or Open Graph image dependency.

After importing older Markdown or site configs, run:

```bash
python scripts/remove_blog_images.py
```

The command is idempotent and strips image fields from all root and site-local posts/configs.

For domain/signup/presentation changes, use `python scripts/launch.py --frontend-only --site SITE_ID`.

For an article-count change, update both the site's `articlesPerProduct` and its product's `probeArticleCount`, then run the normal launch. Products below the new count regenerate; use `--blogs-only` to replace every probe.

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

The preview prints the exact confirmation command. Executing it removes the URL-prefix property from GSC, the matching Google Site Verification ownership record, and the resolved Cloudflare Pages project or Worker script.

It does not delete the registered domain/DNS zone, shared PostHog project, source, local posts, or site config. The config is marked `destroyed` only after external deletion succeeds.

## Take down every deployed site

Preview the exact set:

```bash
python scripts/portfolio.py teardown --all
```

Review every target, then use the printed `--confirm DESTROY-ALL` command. Teardown reports partial failures; successful sites are marked destroyed while failed sites remain retryable. Commit lifecycle/config changes afterward so the repository remains the audit record.
