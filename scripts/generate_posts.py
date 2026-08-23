#!/usr/bin/env python3
"""Generate SEO-focused Markdown posts for a configured site using Gemini.

Uses only Python's standard library so the generator does not add a Node dependency.
Set GEMINI_API_KEY in the environment; never commit the key to the repository.
"""
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
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


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
    # The prompt only needs the frontmatter/structure, not the full existing articles.
    text = examples[0].read_text(encoding="utf-8")
    return text[:3000]


def prompt_for(site: dict) -> str:
    count = int(site.get("articleCount", 5))
    count = max(1, min(count, 10))
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

Goal: attract qualified organic-search visitors who are genuinely likely to need or buy
this product/service. Prioritize useful search intent, topical authority, specificity,
and natural conversion opportunities. Do not write generic filler or keyword-stuffed prose.
Make the posts meaningfully different from one another and cover a coherent topic cluster.
Include informational, problem-solving, comparison, workflow, or buyer-intent angles where appropriate.
Do not invent statistics, customer claims, certifications, or product capabilities that were not provided.
Do not mention that the articles were AI-generated.

Return ONLY a JSON array. Each item must have:
- "slug": lowercase URL slug
- "title": SEO-friendly title that accurately matches the article
- "excerpt": concise search-friendly summary
- "content": Markdown article body, including ## headings where useful

The existing template uses this frontmatter structure. The automation will add dates,
author and image metadata, so do not include YAML frontmatter in content:

{example_format()}

Use these exact template assets when the generated Markdown is written:
- author name: {author.get('name', 'JJ Kasper')}
- author picture: {author.get('picture', '/assets/blog/authors/jj.jpeg')}
- cover image: {images.get('coverImage', '/assets/blog/preview/cover.jpg')}
- OG image: {images.get('ogImage', '/assets/blog/dynamic-routing/cover.jpg')}
""".strip()


def call_gemini(prompt: str) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set. Export it before running the generator.")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
        f"?key={key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "responseMimeType": "application/json"},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.load(response)
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, IndexError) as exc:
            if attempt == 3:
                raise SystemExit(f"Gemini request failed: {exc}") from exc
            time.sleep(2 ** attempt)

    raise AssertionError("unreachable")


def clean_json(text: str, expected_count: int) -> list[dict]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Gemini returned invalid JSON: {exc}") from exc
    if not isinstance(data, list) or len(data) != expected_count:
        raise SystemExit(
            f"Gemini returned {len(data) if isinstance(data, list) else 'non-list'} articles; "
            f"expected exactly {expected_count}."
        )
    return data


def safe_slug(slug: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    if not slug:
        raise ValueError("Generated an empty slug")
    return slug


def write_posts(site: dict, site_dir: Path, articles: list[dict]) -> None:
    posts_dir = site_dir / "_posts"
    posts_dir.mkdir(parents=True, exist_ok=True)
    # Generated site posts are fully managed by this generator. Remove old generated
    # Markdown first so reducing articleCount cannot leave stale articles published.
    for old_post in posts_dir.glob("*.md"):
        old_post.unlink()

    now = datetime.now(timezone.utc)
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

        date = now.replace(microsecond=0)
        frontmatter = "\n".join([
            "---",
            f"title: {json.dumps(title, ensure_ascii=False)}",
            f"excerpt: {json.dumps(excerpt, ensure_ascii=False)}",
            f"coverImage: {json.dumps(site.get('images', {}).get('coverImage', '/assets/blog/preview/cover.jpg'))}",
            f"date: {json.dumps(date.isoformat().replace('+00:00', 'Z'))}",
            "author:",
            f"  name: {json.dumps(site.get('author', {}).get('name', 'JJ Kasper'))}",
            f"  picture: {json.dumps(site.get('author', {}).get('picture', '/assets/blog/authors/jj.jpeg'))}",
            "ogImage:",
            f"  url: {json.dumps(site.get('images', {}).get('ogImage', '/assets/blog/dynamic-routing/cover.jpg'))}",
            "---",
            "",
            content,
            "",
        ])
        (posts_dir / f"{slug}.md").write_text(frontmatter, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("site_id")
    args = parser.parse_args()
    site, site_dir = load_site(args.site_id)
    count = max(1, min(int(site.get("articleCount", 5)), 10))
    print(f"Generating {count} posts for {args.site_id} using {MODEL}...")
    articles = clean_json(call_gemini(prompt_for(site)), count)
    write_posts(site, site_dir, articles)
    print(f"Wrote {len(articles)} posts to {site_dir / '_posts'}")


if __name__ == "__main__":
    main()
