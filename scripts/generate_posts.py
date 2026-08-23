#!/usr/bin/env python3
"""Generate SEO Markdown with automatic Gemini free-model failover."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"
DEFAULT_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]


def models() -> list[str]:
    raw = os.getenv("GEMINI_MODELS")
    values = [x.strip() for x in raw.split(",")] if raw else DEFAULT_MODELS
    return [x for i, x in enumerate(values) if x and x not in values[:i]]


def load_site(site_id: str) -> tuple[dict, Path]:
    site_dir = SITES / site_id
    config_path = site_dir / "site.json"
    if not config_path.exists():
        raise SystemExit(f"Unknown site '{site_id}'. Expected {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8")), site_dir


def example_format() -> str:
    examples = sorted((ROOT / "_posts").glob("*.md"))
    if not examples:
        raise SystemExit("No example Markdown files found in _posts/")
    return examples[0].read_text(encoding="utf-8")[:3000]


def prompt_for(site: dict) -> str:
    count = max(1, min(int(site.get("articleCount", 5)), 10))
    author = site.get("author", {})
    images = site.get("images", {})
    return f"""
You are an expert SEO content strategist and technical writer.

Create exactly {count} original blog posts for this website:
- Site: {site.get('name', site.get('id'))}
- Product/service: {site.get('product')}
- Product URL: {site.get('productUrl')}
- Target audience: {site.get('audience')}
- Main topic: {site.get('topic')}
- Value proposition/problem solved: {site.get('valueProposition')}

Goal: attract qualified organic-search visitors who are genuinely likely to need or buy this product/service.
Prioritize useful search intent, topical authority, specificity, and natural conversion opportunities.
Do not write generic filler or keyword-stuffed prose. Make posts meaningfully different and form a coherent topic cluster.
Do not invent statistics, customer claims, certifications, or product capabilities that were not provided.
Do not mention that the articles were AI-generated.

Return ONLY a JSON array. Each item must have:
- "slug": lowercase URL slug
- "title": SEO-friendly title that accurately matches the article
- "excerpt": concise search-friendly summary
- "content": Markdown article body, including ## headings where useful

The existing template uses this frontmatter structure. The automation adds dates, author and image metadata.
Do not include YAML frontmatter in content:

{example_format()}

Use these exact template assets:
- author name: {author.get('name', 'JJ Kasper')}
- author picture: {author.get('picture', '/assets/blog/authors/jj.jpeg')}
- cover image: {images.get('coverImage', '/assets/blog/preview/cover.jpg')}
- OG image: {images.get('ogImage', '/assets/blog/dynamic-routing/cover.jpg')}
""".strip()


def is_rate_limit(exc: Exception) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in (408, 409, 425, 429, 500, 502, 503, 504)
    return isinstance(exc, urllib.error.URLError)


def call_model(model: str, prompt: str) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set. Export it before running the generator.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "responseMimeType": "application/json"},
    }
    request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=180) as response:
        data = json.load(response)
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_gemini(prompt: str) -> str:
    last_error: Exception | None = None
    available = models()
    for model_index, model in enumerate(available):
        for attempt in range(3):
            try:
                print(f"  Gemini model: {model} (attempt {attempt + 1}/3)", flush=True)
                return call_model(model, prompt)
            except Exception as exc:
                last_error = exc
                if not is_rate_limit(exc):
                    # Invalid-request/auth errors are not fixed by switching models.
                    if isinstance(exc, urllib.error.HTTPError) and exc.code in (400, 401, 403):
                        raise SystemExit(f"Gemini request failed for {model}: HTTP {exc.code}") from exc
                    if attempt == 2:
                        break
                if attempt < 2:
                    time.sleep(min(30, 2 ** attempt * 2))
        if model_index < len(available) - 1:
            print(f"  {model} is unavailable/rate-limited; switching to {available[model_index + 1]}", flush=True)
    raise SystemExit(f"All configured Gemini models failed. Last error: {last_error}") from last_error


def clean_json(text: str, expected_count: int) -> list[dict]:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Gemini returned invalid JSON: {exc}") from exc
    if not isinstance(data, list) or len(data) != expected_count:
        raise SystemExit(f"Gemini returned {len(data) if isinstance(data, list) else 'non-list'} articles; expected exactly {expected_count}.")
    return data


def safe_slug(slug: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    if not slug:
        raise ValueError("Generated an empty slug")
    return slug


def write_posts(site: dict, site_dir: Path, articles: list[dict]) -> None:
    posts_dir = site_dir / "_posts"
    posts_dir.mkdir(parents=True, exist_ok=True)
    for old_post in posts_dir.glob("*.md"):
        old_post.unlink()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    seen: set[str] = set()
    for index, article in enumerate(articles):
        title = str(article.get("title", "")).strip()
        excerpt = str(article.get("excerpt", "")).strip()
        content = str(article.get("content", "")).strip()
        slug = safe_slug(str(article.get("slug", title)))
        if not title or not excerpt or not content:
            raise SystemExit(f"Article {index + 1} is missing title, excerpt, or content.")
        if slug in seen:
            raise SystemExit(f"Duplicate generated slug: {slug}")
        seen.add(slug)
        frontmatter = "\n".join([
            "---", f"title: {json.dumps(title, ensure_ascii=False)}", f"excerpt: {json.dumps(excerpt, ensure_ascii=False)}",
            f"coverImage: {json.dumps(site.get('images', {}).get('coverImage', '/assets/blog/preview/cover.jpg'))}",
            f"date: {json.dumps(now.isoformat().replace('+00:00', 'Z'))}", "author:",
            f"  name: {json.dumps(site.get('author', {}).get('name', 'JJ Kasper'))}",
            f"  picture: {json.dumps(site.get('author', {}).get('picture', '/assets/blog/authors/jj.jpeg'))}",
            "ogImage:", f"  url: {json.dumps(site.get('images', {}).get('ogImage', '/assets/blog/dynamic-routing/cover.jpg'))}",
            "---", "", content, "",
        ])
        (posts_dir / f"{slug}.md").write_text(frontmatter, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("site_id")
    args = parser.parse_args()
    site, site_dir = load_site(args.site_id)
    count = max(1, min(int(site.get("articleCount", 5)), 10))
    print(f"Generating {count} posts for {args.site_id} using automatic model failover: {', '.join(models())}")
    articles = clean_json(call_gemini(prompt_for(site)), count)
    write_posts(site, site_dir, articles)
    print(f"Wrote {len(articles)} posts to {site_dir / '_posts'}")


if __name__ == "__main__":
    main()
