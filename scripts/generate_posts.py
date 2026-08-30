#!/usr/bin/env python3
"""Generate restart-safe, product-attributed SEO probes for one portfolio site."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"
STATE = ROOT / ".deploy" / "state"
DEFAULT_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]
GENERATION_VERSION = 2


class GeminiExhausted(Exception):
    pass


def models() -> list[str]:
    raw = os.getenv("GEMINI_MODELS")
    values = [item.strip() for item in raw.split(",")] if raw else DEFAULT_MODELS
    return [item for index, item in enumerate(values) if item and item not in values[:index]]


def load_site(site_id: str) -> tuple[dict[str, Any], Path]:
    directory = SITES / site_id
    path = directory / "site.json"
    if not path.exists():
        raise SystemExit(f"Unknown site '{site_id}'")
    return json.loads(path.read_text(encoding="utf-8")), directory


def site_products(site: dict[str, Any]) -> list[dict[str, Any]]:
    products = site.get("products")
    if isinstance(products, list) and products:
        return products
    return [
        {
            "id": safe_slug(str(site.get("id") or site.get("name") or "product")),
            "name": site.get("name") or site.get("product") or "Product",
            "product": site.get("product", ""),
            "productUrl": site.get("productUrl", ""),
            "audience": site.get("audience", ""),
            "problem": site.get("valueProposition", ""),
            "valueProposition": site.get("valueProposition", ""),
            "topic": site.get("topic", ""),
        }
    ]


def article_target(site: dict[str, Any]) -> int:
    value = site.get("articlesPerProduct", site.get("articleCount", 5))
    return max(1, min(int(value), 12))


def generation_fingerprint(
    site: dict[str, Any], product: dict[str, Any], count: int
) -> str:
    """Fingerprint only inputs that should invalidate this product's probes."""
    payload = {
        "version": GENERATION_VERSION,
        "siteAudience": site.get("audience", ""),
        "count": count,
        "product": {
            key: product.get(key, "")
            for key in (
                "id",
                "name",
                "product",
                "productUrl",
                "audience",
                "problem",
                "valueProposition",
                "topic",
                "seoAngle",
            )
        },
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:20]


def example_format() -> str:
    files = sorted((ROOT / "_posts").glob("*.md"))
    if not files:
        raise SystemExit("No example Markdown files found in _posts/")
    return files[0].read_text(encoding="utf-8")[:3000]


def prompt_for(site: dict[str, Any], product: dict[str, Any], count: int) -> str:
    peers = [
        {"name": item.get("name"), "url": f"/products/{item.get('id')}"}
        for item in site_products(site)
        if item.get("id") != product.get("id")
    ]
    return f"""Create exactly {count} original organic-search probe posts for one narrowly defined product.

Website: {site.get('name')}
Website audience: {site.get('audience')}
Product id: {product.get('id')}
Product name: {product.get('name')}
Product/service: {product.get('product')}
Product URL: {product.get('productUrl')}
Specific audience: {product.get('audience') or site.get('audience')}
Problem: {product.get('problem')}
Value proposition: {product.get('valueProposition')}
Topic: {product.get('topic')}
SEO thesis: {product.get('seoAngle', '')}
Complementary product pages: {json.dumps(peers, ensure_ascii=False)}

The posts are demand probes. Cover distinct high-intent searches across templates, calculators/checklists,
problem diagnosis, comparisons/alternatives, workflow instructions, and purchase-ready software terms. Each
post must be genuinely useful and specific enough to rank independently. Where contextually helpful, include
one natural Markdown link to a complementary product page. Do not force cross-links. Do not invent statistics,
customers, quotes, laws, product capabilities, or keyword-volume numbers. Do not keyword-stuff or write generic
filler. Do not include photos, image Markdown, HTML image tags, or image placeholders. Return ONLY a JSON array
with slug, title, excerpt, and content (Markdown); no YAML frontmatter.

Match this structural example: {example_format()}"""


def mock_articles(product: dict[str, Any], count: int) -> list[dict[str, str]]:
    topic = product.get("topic") or product.get("name") or "this workflow"
    product_name = product.get("name") or "the product"
    intents = (
        "practical guide",
        "checklist",
        "template",
        "common mistakes",
        "software comparison",
        "workflow",
        "calculator",
        "best practices",
        "alternatives",
        "automation guide",
        "examples",
        "buying guide",
    )
    return [
        {
            "slug": f"{safe_slug(topic)}-{safe_slug(intents[index])}",
            "title": f"{topic.title()}: {intents[index].title()}",
            "excerpt": f"A focused {intents[index]} for {topic}.",
            "content": (
                f"## Why {topic} matters\n\nA repeatable process reduces missed handoffs and rework.\n\n"
                f"## A practical approach\n\nDocument the current workflow, identify the failure point, and test "
                f"one measurable improvement. {product_name} is designed around this specific workflow.\n\n"
                "## Next step\n\nTry the smallest useful change and record the result."
            ),
        }
        for index in range(count)
    ]


def call_model(model: str, prompt: str) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise GeminiExhausted("GEMINI_API_KEY is not set")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.75,
            "responseMimeType": "application/json",
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        data = json.load(response)
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_gemini(
    prompt: str, site_id: str, product_id: str, article_count: int
) -> list[dict[str, Any]]:
    last: Exception | None = None
    attempts: list[dict[str, Any]] = []
    for model in models():
        for attempt in range(3):
            try:
                print(f"  Gemini: {model} attempt {attempt + 1}/3", flush=True)
                result = clean_json(call_model(model, prompt), article_count)
                attempts.append({"model": model, "attempt": attempt + 1, "status": "ok"})
                return result
            except urllib.error.HTTPError as exc:
                last = exc
                attempts.append(
                    {"model": model, "attempt": attempt + 1, "status": exc.code}
                )
                if exc.code in {401, 403}:
                    raise SystemExit(f"Gemini authentication failed: HTTP {exc.code}") from exc
                if exc.code in {400, 404, 422}:
                    break  # Unsupported model/schema: advance to the next model.
                if exc.code not in {408, 409, 425, 429, 500, 502, 503, 504}:
                    break
                time.sleep(min(30, 2 ** attempt * 2))
            except urllib.error.URLError as exc:
                last = exc
                attempts.append(
                    {"model": model, "attempt": attempt + 1, "status": "network"}
                )
                time.sleep(min(30, 2 ** attempt * 2))
            except Exception as exc:
                last = exc
                attempts.append(
                    {"model": model, "attempt": attempt + 1, "status": type(exc).__name__}
                )
                if attempt == 2:
                    break
                time.sleep(min(30, 2 ** attempt * 2))
    STATE.mkdir(parents=True, exist_ok=True)
    _atomic_json(
        STATE / "gemini_exhausted.json",
        {
            "site": site_id,
            "product": product_id,
            "timestamp": time.time(),
            "models": models(),
            "attempts": attempts,
            "error": str(last),
        },
    )
    raise GeminiExhausted(f"All configured Gemini models failed: {last}")


def clean_json(text: str, count: int) -> list[dict[str, Any]]:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    data = json.loads(text)
    if not isinstance(data, list) or len(data) != count:
        actual = len(data) if isinstance(data, list) else "invalid"
        raise ValueError(f"Gemini returned {actual} articles; expected {count}")
    return data


def safe_slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not result:
        raise ValueError("Generated an empty slug")
    return result


_MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\([^\n)]*\)")
_HTML_IMAGE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)


def strip_images(content: str) -> str:
    """Remove model-produced image markup while preserving useful alt text."""
    content = _MARKDOWN_IMAGE.sub(lambda match: match.group(1).strip(), content)
    return _HTML_IMAGE.sub("", content).strip()


def existing_product_posts(directory: Path, product_id: str) -> list[Path]:
    result = []
    marker = f"productId: {json.dumps(product_id, ensure_ascii=False)}"
    for path in (directory / "_posts").glob("*.md"):
        try:
            header = path.read_text(encoding="utf-8")[:1800]
        except OSError:
            continue
        if marker in header:
            result.append(path)
    return result


def attributed_product_ids(directory: Path) -> set[str]:
    result: set[str] = set()
    pattern = re.compile(r'^productId:\s*["\']?([^"\'\n]+)', re.MULTILINE)
    for path in (directory / "_posts").glob("*.md"):
        try:
            match = pattern.search(path.read_text(encoding="utf-8")[:1800])
        except OSError:
            continue
        if match:
            result.add(match.group(1).strip())
    return result


def write_product_posts(
    site: dict[str, Any],
    directory: Path,
    product: dict[str, Any],
    articles: list[dict[str, Any]],
    fingerprint: str,
) -> list[Path]:
    posts = directory / "_posts"
    posts.mkdir(parents=True, exist_ok=True)
    product_id = safe_slug(str(product.get("id") or product.get("name")))
    for old in existing_product_posts(directory, product_id):
        old.unlink()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    seen: set[str] = set()
    author = site.get("author", {})
    written: list[Path] = []
    for index, article in enumerate(articles):
        title = str(article.get("title", "")).strip()
        excerpt = str(article.get("excerpt", "")).strip()
        content = strip_images(str(article.get("content", "")).strip())
        article_slug = safe_slug(str(article.get("slug", title)))
        product_prefix = product_id[:48].rstrip("-")
        article_limit = max(24, 116 - len(product_prefix))
        slug = f"{product_prefix}-{article_slug[:article_limit].rstrip('-')}"
        if not title or not excerpt or not content:
            raise ValueError(f"Article {index + 1} missing title, excerpt, or content")
        if slug in seen:
            raise ValueError(f"Duplicate generated slug: {slug}")
        seen.add(slug)
        frontmatter = "\n".join(
            [
                "---",
                f"title: {json.dumps(title, ensure_ascii=False)}",
                f"excerpt: {json.dumps(excerpt, ensure_ascii=False)}",
                f"productId: {json.dumps(product_id, ensure_ascii=False)}",
                f"productName: {json.dumps(product.get('name') or product_id, ensure_ascii=False)}",
                f"generationFingerprint: {json.dumps(fingerprint)}",
                f"date: {json.dumps(now.isoformat().replace('+00:00', 'Z'))}",
                "author:",
                f"  name: {json.dumps(author.get('name', 'John Smith'))}",
                "---",
                "",
                content,
                "",
            ]
        )
        output = posts / f"{slug}.md"
        output.write_text(frontmatter, encoding="utf-8")
        written.append(output)
    return written


def generate_site(
    site_id: str,
    *,
    mock: bool,
    force: bool,
    product_ids: list[str] | None = None,
) -> int:
    site, directory = load_site(site_id)
    all_products = site_products(site)
    requested = set(product_ids or [])
    known = {
        safe_slug(str(product.get("id") or product.get("name"))): product
        for product in all_products
    }
    missing = requested - known.keys()
    if missing:
        raise SystemExit(
            f"Unknown product(s) for {site_id}: {', '.join(sorted(missing))}"
        )
    products = [product for product_id, product in known.items() if not requested or product_id in requested]
    count = article_target(site)
    checkpoint = STATE / f"generate-{site_id}.json"
    generated = 0
    STATE.mkdir(parents=True, exist_ok=True)

    fingerprints: dict[str, str] = {}
    if checkpoint.exists():
        try:
            fingerprints = dict(
                json.loads(checkpoint.read_text(encoding="utf-8")).get("fingerprints", {})
            )
        except (OSError, ValueError, TypeError):
            fingerprints = {}

    if not requested:
        current_ids = set(known)
        for stale_id in sorted(attributed_product_ids(directory) - current_ids):
            stale_posts = existing_product_posts(directory, stale_id)
            for path in stale_posts:
                path.unlink()
            fingerprints.pop(stale_id, None)
            print(f"Removed {len(stale_posts)} posts for removed product {stale_id}", flush=True)

    for index, product in enumerate(products):
        product_id = safe_slug(str(product.get("id") or product.get("name")))
        fingerprint = generation_fingerprint(site, product, count)
        existing = existing_product_posts(directory, product_id)
        stored_fingerprint = fingerprints.get(product_id)
        if not force and len(existing) >= count and (
            stored_fingerprint == fingerprint or stored_fingerprint is None
        ):
            # Adopt legacy count-only checkpoints once, without an expensive surprise regeneration.
            fingerprints[product_id] = fingerprint
            print(
                f"[{index + 1}/{len(products)}] {product_id}: already has {len(existing)} posts; skipped",
                flush=True,
            )
            _generation_checkpoint(
                checkpoint, site_id, products, index + 1, product_id, fingerprints
            )
            continue
        if existing and stored_fingerprint and stored_fingerprint != fingerprint:
            print(f"[{index + 1}/{len(products)}] {product_id}: inputs changed; regenerating", flush=True)
        print(
            f"[{index + 1}/{len(products)}] Generating {count} posts for {product_id} "
            f"({'mock' if mock else 'Gemini failover'})",
            flush=True,
        )
        _generation_checkpoint(checkpoint, site_id, products, index, product_id, fingerprints)
        articles = (
            mock_articles(product, count)
            if mock
            else call_gemini(
                prompt_for(site, product, count), site_id, product_id, count
            )
        )
        written = write_product_posts(
            site, directory, product, articles, fingerprint
        )
        generated += len(written)
        fingerprints[product_id] = fingerprint
        _generation_checkpoint(
            checkpoint, site_id, products, index + 1, product_id, fingerprints
        )
    _generation_checkpoint(
        checkpoint,
        site_id,
        products,
        len(products),
        None,
        fingerprints,
        complete=True,
    )
    exhausted_marker = STATE / "gemini_exhausted.json"
    if exhausted_marker.exists():
        exhausted_marker.unlink()
    return generated


def _generation_checkpoint(
    path: Path,
    site_id: str,
    products: list[dict[str, Any]],
    next_index: int,
    product_id: str | None,
    fingerprints: dict[str, str],
    *,
    complete: bool = False,
) -> None:
    _atomic_json(
        path,
        {
            "site": site_id,
            "productIds": [item.get("id") for item in products],
            "nextIndex": next_index,
            "currentProduct": product_id,
            "fingerprints": fingerprints,
            "complete": complete,
            "updatedAt": time.time(),
        },
    )


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("site_id")
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--product", action="append", help="Generate only this product ID")
    args = parser.parse_args()
    mock = args.mock or os.getenv("MOCK_LLM", "").lower() in {"1", "true", "yes"}
    generated = generate_site(
        args.site_id,
        mock=mock,
        force=args.force,
        product_ids=args.product,
    )
    print(f"Wrote {generated} new posts to {SITES / args.site_id / '_posts'}")


if __name__ == "__main__":
    main()
