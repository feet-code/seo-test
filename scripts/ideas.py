#!/usr/bin/env python3
"""Import, validate, and materialize an editable NicheScout portfolio."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IDEAS_DIR = ROOT / "ideas"
IDEAS = IDEAS_DIR / "ideas.json"
SITES = ROOT / "sites"


class PortfolioError(ValueError):
    pass


def slug(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def mock_document() -> dict[str, Any]:
    products = []
    for index, name in enumerate(
        ("Invoice Nudge", "Scope Guard", "Client Intake Check", "Change Log", "Handoff Pack"),
        1,
    ):
        product_id = slug(name)
        products.append(
            {
                "id": product_id,
                "siteId": "freelancer-operations",
                "name": name,
                "product": f"A focused {name.lower()} tool for independent service businesses.",
                "audience": "freelancers and independent service businesses",
                "problem": f"Teams manually handle the recurring {name.lower()} workflow.",
                "valueProposition": f"Makes {name.lower()} repeatable without a large business suite.",
                "topic": f"{name.lower()} workflows",
                "monetization": "$19/month",
                "startupCost": "Static frontend and inexpensive transactional storage.",
                "seoAngle": f"Templates, checklists, and software searches around {name.lower()}.",
                "score": 75 - index,
                "domain": None,
            }
        )
    return {
        "version": 2,
        "sites": [
            {
                "id": "freelancer-operations",
                "name": "Freelancer Operations Tools",
                "audience": "freelancers and independent service businesses",
                "topic": "client operations for independent service businesses",
                "productIds": [product["id"] for product in products],
                "domain": None,
            }
        ],
        "ideas": products,
    }


def load_document(path: Path = IDEAS) -> dict[str, Any]:
    if not path.exists():
        raise PortfolioError(
            f"Portfolio not found: {path}. Import NicheScout output with --portfolio PATH."
        )
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PortfolioError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise PortfolioError("Portfolio root must be a JSON object")
    validate_document(document)
    return document


def validate_document(document: dict[str, Any]) -> None:
    version = int(document.get("version", 1))
    ideas = document.get("ideas")
    if not isinstance(ideas, list) or not ideas:
        raise PortfolioError("ideas must be a non-empty array")

    idea_ids: set[str] = set()
    for index, idea in enumerate(ideas):
        if not isinstance(idea, dict):
            raise PortfolioError(f"ideas[{index}] must be an object")
        idea_id = slug(idea.get("id") or idea.get("name"))
        if not idea_id:
            raise PortfolioError(f"ideas[{index}] needs a usable id or name")
        if len(idea_id) > 80:
            raise PortfolioError(f"Idea id is too long for portable URLs/files: {idea_id}")
        if idea_id in idea_ids:
            raise PortfolioError(f"Duplicate idea id: {idea_id}")
        idea_ids.add(idea_id)
        for field in ("name", "product", "audience", "problem", "topic"):
            if not str(idea.get(field, "")).strip():
                raise PortfolioError(f"Idea {idea_id!r} is missing {field}")

    if version < 2:
        return
    sites = document.get("sites")
    if not isinstance(sites, list) or not sites:
        raise PortfolioError("Version-2 portfolio requires a non-empty sites array")
    site_ids: set[str] = set()
    referenced_products: set[str] = set()
    idea_by_id = {slug(idea.get("id") or idea.get("name")): idea for idea in ideas}
    for index, site in enumerate(sites):
        if not isinstance(site, dict):
            raise PortfolioError(f"sites[{index}] must be an object")
        site_id = slug(site.get("id") or site.get("name"))
        if not site_id or site_id in site_ids:
            raise PortfolioError(f"Invalid or duplicate site id: {site_id!r}")
        if len(site_id) > 58:
            raise PortfolioError(f"Site id exceeds the portable/deployment limit (58): {site_id}")
        site_ids.add(site_id)
        product_ids = [slug(item) for item in site.get("productIds", [])]
        if not product_ids:
            raise PortfolioError(f"Site {site_id!r} has no productIds")
        if len(product_ids) != len(set(product_ids)):
            raise PortfolioError(f"Site {site_id!r} repeats a product id")
        missing = set(product_ids) - idea_ids
        if missing:
            raise PortfolioError(
                f"Site {site_id!r} references unknown product(s): {', '.join(sorted(missing))}"
            )
        overlap = referenced_products & set(product_ids)
        if overlap:
            raise PortfolioError(
                f"Products assigned to more than one site: {', '.join(sorted(overlap))}"
            )
        for product_id in product_ids:
            declared_site = slug(idea_by_id[product_id].get("siteId", ""))
            if declared_site and declared_site != site_id:
                raise PortfolioError(
                    f"Idea {product_id!r} says siteId={declared_site!r}, expected {site_id!r}"
                )
        referenced_products.update(product_ids)
    orphaned = idea_ids - referenced_products
    if orphaned:
        raise PortfolioError(
            "Every version-2 idea must appear in one site.productIds list; orphaned: "
            + ", ".join(sorted(orphaned))
        )


def normalized_sites(document: dict[str, Any]) -> list[tuple[dict[str, Any], list[dict[str, Any]]]]:
    ideas = document["ideas"]
    if int(document.get("version", 1)) < 2:
        return [
            (
                {
                    "id": slug(idea.get("id") or idea.get("name")),
                    "name": idea.get("name"),
                    "audience": idea.get("audience"),
                    "topic": idea.get("topic"),
                    "domain": idea.get("domain"),
                },
                [idea],
            )
            for idea in ideas
        ]
    idea_by_id = {slug(idea.get("id") or idea.get("name")): idea for idea in ideas}
    return [
        (site, [idea_by_id[slug(product_id)] for product_id in site["productIds"]])
        for site in document["sites"]
    ]


def materialize(document: dict[str, Any]) -> int:
    created = 0
    for site, ideas in normalized_sites(document):
        site_id = slug(site.get("id") or site.get("name"))
        site_dir = SITES / site_id
        config_path = site_dir / "site.json"
        if config_path.exists():
            continue
        products = [_product_config(idea) for idea in ideas]
        primary = products[0]
        config = {
            "id": site_id,
            "name": site.get("name") or f"{str(site.get('audience') or primary['audience']).title()} Tools",
            "domain": site.get("domain"),
            "audience": site.get("audience") or primary["audience"],
            "topic": site.get("topic") or primary["topic"],
            "products": products,
            "articlesPerProduct": 10 if len(products) > 1 else 5,
            # Backward-compatible primary-product fields for older scripts/config readers.
            "product": primary["product"],
            "productUrl": primary.get("productUrl", ""),
            "valueProposition": primary["valueProposition"],
            "articleCount": 10 if len(products) > 1 else 5,
            "author": {"name": "John Smith", "picture": "/assets/blog/authors/jj.jpeg"},
            "images": {
                "coverImage": "/assets/blog/preview/cover.jpg",
                "ogImage": "/assets/blog/dynamic-routing/cover.jpg",
            },
            "signup": {
                "enabled": True,
                "headline": "Interested? Get notified when this is available.",
                "endpoint": "",
                "email": "",
            },
            "deploy": {"provider": "cloudflare-pages", "project": site_id},
            "portfolioVersion": int(document.get("version", 1)),
        }
        site_dir.mkdir(parents=True, exist_ok=True)
        (site_dir / "_posts").mkdir(exist_ok=True)
        (site_dir / "_posts" / ".gitkeep").touch(exist_ok=True)
        _atomic_json(config_path, config)
        created += 1
    return created


def _product_config(idea: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": slug(idea.get("id") or idea.get("name")),
        "name": idea.get("name"),
        "product": idea.get("product"),
        "productUrl": idea.get("productUrl", ""),
        "audience": idea.get("audience"),
        "problem": idea.get("problem"),
        "valueProposition": idea.get("valueProposition") or idea.get("problem"),
        "topic": idea.get("topic"),
        "monetization": idea.get("monetization", ""),
        "startupCost": idea.get("startupCost", ""),
        "seoAngle": idea.get("seoAngle", ""),
        "score": idea.get("score"),
    }


def import_portfolio(source: Path) -> dict[str, Any]:
    document = load_document(source)
    IDEAS_DIR.mkdir(parents=True, exist_ok=True)
    _atomic_json(IDEAS, document)
    return document


def _atomic_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import NicheScout ideas.json and materialize grouped SEO sites"
    )
    parser.add_argument("--portfolio", type=Path, help="NicheScout ideas.json to import")
    parser.add_argument("--mock", action="store_true", help="Use an isolated five-product fixture")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if args.portfolio and args.mock:
        raise SystemExit("Choose either --portfolio or --mock")
    try:
        if args.mock:
            document = mock_document()
            validate_document(document)
        elif args.portfolio:
            document = import_portfolio(args.portfolio)
        else:
            document = load_document()
    except PortfolioError as exc:
        raise SystemExit(f"Portfolio validation failed: {exc}") from exc

    site_count = len(normalized_sites(document))
    if args.validate_only:
        print(f"Valid portfolio: {len(document['ideas'])} products across {site_count} sites.")
        return
    created = materialize(document)
    print(
        f"Portfolio contains {len(document['ideas'])} products across {site_count} sites; "
        f"created {created} new site configurations."
    )


if __name__ == "__main__":
    main()
