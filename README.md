# SEO site automation

This repository contains one reusable Next.js static blog template plus a data-driven pipeline for generating and deploying many independent SEO sites.

## Architecture

Each site lives under `sites/<site-id>/` and contains a `site.json` plus generated Markdown in `_posts/`. The Next.js app reads the selected post directory from `SEO_POSTS_DIR` during the build, so the template itself is shared by every site.

The build artifact is always `out/`. Deployment is a separate step, keeping the system portable across hosting providers.

Supported deployment adapters:

- `static` — leave the `out/` artifact ready for any static host
- `cloudflare-pages` — Wrangler Pages deployment
- `cloudflare-workers` — Wrangler Workers static-assets deployment
- `vercel` — Vercel CLI deployment
- `netlify` — Netlify CLI deployment

## Setup

1. Install Node.js/npm and Python 3.10+.
2. Run `npm install`.
3. Set `GEMINI_API_KEY` in your shell. Never commit API keys.
4. Copy `sites/example/site.json` to a new directory and customize the product, audience, topic, images, author, and article count.

## Commands

Generate posts:

```bash
python scripts/site.py generate example
```

Build one site:

```bash
python scripts/site.py build example
```

Generate + build + produce a static artifact:

```bash
python scripts/site.py all example static
```

Deploy to Cloudflare Pages:

```bash
python scripts/site.py all example cloudflare-pages
```

Deploy the static assets as a Cloudflare Worker:

```bash
python scripts/site.py all example cloudflare-workers
```

Deploy to Vercel:

```bash
python scripts/site.py all example vercel
```

Deploy to Netlify:

```bash
python scripts/site.py all example netlify
```

The Vercel and Netlify CLIs are invoked through `npx`, so they are not dependencies of the blog application itself. Authenticate each provider using its normal CLI/environment configuration.

## Scaling to hundreds of sites

Add one directory and one `site.json` per website. Generated articles are isolated under that site's `_posts/` directory. Builds are performed serially because Next.js writes to the shared `out/` directory.

For production-scale generation, run Gemini generation in controlled batches to respect API quotas and review/validate generated content before publishing.

## Security

The old hard-coded Gemini key must not be used. Rotate any key that was previously committed and use `GEMINI_API_KEY` instead.
