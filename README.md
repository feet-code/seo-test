# SEO portfolio automation

This repository is the downstream deployment and forever-feedback loop for a NicheScout seed portfolio. NicheScout does the finite pre-deployment research; this repo turns its editable `ideas.json` into sites, blog probes, product-interest events, deployments, GSC, and PostHog data.

The version-2 portfolio shape is **100 websites × five complementary products = 500 product probes**. Products on one site share an audience, so visitors can cross-discover adjacent tools without mixing unrelated search intent.

## Import NicheScout output

From this repository:

```bash
python scripts/ideas.py --portfolio ../NicheScout/exports/ideas.json
python scripts/ideas.py --validate-only
```

The importer validates unique IDs, `siteId`/`productIds` consistency, orphaned products, and required deployment fields before atomically replacing `ideas/ideas.json`. It then creates one `sites/<site-id>/site.json` per group with a `products` array.

Existing site configs are never overwritten. That protects manual domain, signup, monitoring, and deployment edits. Version-1 one-product portfolios/configs remain supported.

`ideas/ideas.json` remains human editable. You can add your own products or regroup finalists after observing NicheScout’s report; keep every idea in exactly one `site.productIds` list.

## Safe local smoke test

```bash
pip install -r requirements.txt
npm ci
python -m unittest discover -s tests -v
python scripts/launch.py --mock --provider static --limit 1
```

`--mock` makes no Gemini, monitoring, or deployment API calls.

## Launch

After credentials are configured:

```bash
python scripts/launch.py
```

Useful subsets and modes:

```bash
python scripts/launch.py --site my-site
python scripts/launch.py --sites site-a,site-b,site-c
python scripts/launch.py --limit 5
python scripts/launch.py --frontend-only
python scripts/launch.py --blogs-only
python scripts/launch.py --skip-generation
```

All sites share the same Next.js frontend. `--frontend-only` rebuilds without calling Gemini. `--blogs-only` intentionally regenerates every selected product’s posts. `--skip-generation` publishes existing/manual Markdown.

## Product-attributed SEO probes

Grouped sites default to ten articles per product (50 per five-product site). Generation runs one product at a time and persists `.deploy/state/generate-<site>.json`. Completed products are skipped on rerun; a partial product is regenerated only after a complete replacement response has been validated.

Every generated post has:

```yaml
productId: invoice-nudge
productName: Invoice Nudge
```

The static frontend uses that attribution to:

- create an indexable `/products/<product-id>` landing page;
- show only that product’s guides on its landing page;
- attach a product-specific interest form to every product page and post;
- include all product pages and posts in `sitemap.xml`;
- cross-link the five complementary products on the same site;
- capture PostHog event `product_probe_viewed` on attributed landing/post views and `product_interest_submitted` on form submission, with product/source properties;
- POST the same product identity to an optional signup endpoint.

This means GSC queries/clicks, PostHog behavior, and signups can be rolled up by the original NicheScout idea even though five probes share one domain.

## Gemini failover and resume

Blog generation cycles through `GEMINI_MODELS`. Defaults are free-tier text models, with 2.5 Flash models as the broad compatibility fallback:

```text
GEMINI_MODELS=gemini-3.5-flash-lite,gemini-3.1-flash-lite,gemini-2.5-flash-lite,gemini-2.5-flash
```

Unsupported model IDs advance immediately; transient/rate-limit failures retry and advance through the chain. Authentication failures stop immediately. If every model fails, the generator writes `.deploy/state/gemini_exhausted.json` with the exact site, product, models, attempts, and error. The site launcher saves its own checkpoint and terminates instead of silently skipping work.

Resume with the same selected subset:

```bash
python scripts/launch.py --resume
```

The site checkpoint resumes the site, and the product checkpoint skips every product already completed inside that site.

## Product-interest signup

Each site config can contain:

```json
{
  "signup": {
    "enabled": true,
    "headline": "Interested? Get notified when this is available.",
    "endpoint": "https://your-form-endpoint.example/subscribe",
    "email": "hello@example.com"
  }
}
```

If `endpoint` is configured, the frontend sends:

```json
{
  "email": "person@example.com",
  "productId": "invoice-nudge",
  "product": "Invoice Nudge",
  "site": "Freelancer Operations Tools",
  "sourcePath": "/posts/invoice-nudge-overdue-invoice-template"
}
```

Without an endpoint, a configured email opens a prefilled message. Even without either backend, a configured PostHog project still records the product-interest event.

## Monitoring

All sites use one shared PostHog project, suitable for a free-tier portfolio. Google Search Console verification and sitemap submission are automated when Google credentials are configured. An hourly GitHub Actions workflow health-checks configured sites.

The grouping affects presentation only: downstream learning remains product-specific via post frontmatter, landing-page route, signup payload, and PostHog properties.

## Deployment providers

The build produces a portable static `out/` artifact:

```bash
python scripts/launch.py --provider cloudflare-pages
python scripts/launch.py --provider cloudflare-workers
python scripts/launch.py --provider vercel
python scripts/launch.py --provider netlify
python scripts/launch.py --provider static
```

Cloudflare Pages projects are created/reused automatically when credentials are supplied. Custom domains must already be owned and controlled by you.

## Credentials

Never commit credentials:

```text
GEMINI_API_KEY=...
GEMINI_MODELS=gemini-3.5-flash-lite,gemini-3.1-flash-lite,gemini-2.5-flash-lite,gemini-2.5-flash
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
POSTHOG_PERSONAL_API_KEY=...
POSTHOG_ORGANIZATION_ID=...
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## Architecture boundary

```text
NicheScout (finite public-evidence tournament)
                    |
                    v
       ideas/ideas.json v2 (editable)
                    |
                    v
       100 site configs × 5 products
                    |
        +-----------+-----------+
        |                       |
        v                       v
product-attributed posts   product landing pages
        |                       |
        +-----------+-----------+
                    v
       static build and deployment
                    |
        +-----------+-----------+
        |           |           |
        v           v           v
       GSC       PostHog      signups
        |           |           |
        +-----------+-----------+
                    v
        forever deployment feedback loop
```
