#!/usr/bin/env python3
"""Import, validate, plan, and safely sync an editable NicheScout portfolio."""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IDEAS_DIR = ROOT / "ideas"
IDEAS = IDEAS_DIR / "ideas.json"
SITES = ROOT / "sites"


class PortfolioError(ValueError):
    pass


@dataclass
class SyncPlan:
    create: list[str] = field(default_factory=list)
    update: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)

    @property
    def changed(self) -> int:
        return len(self.create) + len(self.update)


def slug(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def mock_document() -> dict[str, Any]:
    products = []
    for index, name in enumerate(("Invoice Nudge", "Scope Guard", "Handoff Pack"), 1):
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
        "articlesPerProduct": 10,
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
    try:
        version = int(document.get("version", 1))
    except (TypeError, ValueError) as exc:
        raise PortfolioError("version must be an integer") from exc
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
        for name in ("name", "product", "audience", "problem", "topic"):
            if not str(idea.get(name, "")).strip():
                raise PortfolioError(f"Idea {idea_id!r} is missing {name}")

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
            raise PortfolioError(
                f"Site id exceeds the portable/deployment limit (58): {site_id}"
            )
        site_ids.add(site_id)
        product_ids = [slug(item) for item in site.get("productIds", [])]
        if not product_ids:
            raise PortfolioError(f"Site {site_id!r} has no productIds")
        if len(product_ids) != len(set(product_ids)):
            raise PortfolioError(f"Site {site_id!r} repeats a product id")
        missing = set(product_ids) - idea_ids
        if missing:
            raise PortfolioError(
                f"Site {site_id!r} references unknown product(s): "
                + ", ".join(sorted(missing))
            )
        overlap = referenced_products & set(product_ids)
        if overlap:
            raise PortfolioError(
                "Products assigned to more than one site: " + ", ".join(sorted(overlap))
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


def normalized_sites(
    document: dict[str, Any],
) -> list[tuple[dict[str, Any], list[dict[str, Any]]]]:
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


def _desired_config(
    document: dict[str, Any],
    site: dict[str, Any],
    ideas: list[dict[str, Any]],
) -> dict[str, Any]:
    site_id = slug(site.get("id") or site.get("name"))
    products = [_product_config(idea) for idea in ideas]
    primary = products[0]
    version = int(document.get("version", 1))
    default_articles = 10 if version >= 2 else 5
    articles = int(
        site.get(
            "articlesPerProduct",
            document.get("articlesPerProduct", default_articles),
        )
    )
    return {
        "id": site_id,
        "name": site.get("name")
        or f"{str(site.get('audience') or primary['audience']).title()} Tools",
        "domain": site.get("domain"),
        "audience": site.get("audience") or primary["audience"],
        "topic": site.get("topic") or primary["topic"],
        "products": products,
        "articlesPerProduct": articles,
        "product": primary["product"],
        "productUrl": primary.get("productUrl", ""),
        "valueProposition": primary["valueProposition"],
        "articleCount": articles,
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
        "status": "active",
        "portfolioManaged": True,
        "portfolioVersion": version,
    }


def _merge_product(
    desired: dict[str, Any],
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    if not existing:
        return desired
    merged = {**existing, **desired}
    if not desired.get("productUrl") and existing.get("productUrl"):
        merged["productUrl"] = existing["productUrl"]
    return merged


def _merge_config(
    desired: dict[str, Any],
    existing: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(existing)
    existing_products = {
        str(product.get("id")): product
        for product in existing.get("products") or []
        if isinstance(product, dict)
    }
    products = [
        _merge_product(product, existing_products.get(str(product["id"])))
        for product in desired["products"]
    ]

    for name in (
        "id",
        "name",
        "audience",
        "topic",
        "portfolioManaged",
        "portfolioVersion",
    ):
        merged[name] = desired[name]
    merged["products"] = products

    primary = products[0]
    merged["product"] = primary["product"]
    merged["productUrl"] = primary.get("productUrl", "")
    merged["valueProposition"] = primary["valueProposition"]

    # Site-local operations stay authoritative across repeated portfolio imports.
    merged["domain"] = existing.get("domain") or desired.get("domain")
    merged["articlesPerProduct"] = int(
        existing.get("articlesPerProduct", desired["articlesPerProduct"])
    )
    merged["articleCount"] = merged["articlesPerProduct"]
    merged["status"] = existing.get("status", "active")
    for name in ("author", "images", "signup", "deploy"):
        if name not in merged:
            merged[name] = desired[name]
    return merged


def sync_document(document: dict[str, Any], *, apply: bool) -> SyncPlan:
    validate_document(document)
    plan = SyncPlan()
    desired_ids: set[str] = set()

    for site, ideas in normalized_sites(document):
        desired = _desired_config(document, site, ideas)
        site_id = desired["id"]
        desired_ids.add(site_id)
        site_dir = SITES / site_id
        config_path = site_dir / "site.json"
        if config_path.exists():
            existing = json.loads(config_path.read_text(encoding="utf-8"))
            merged = _merge_config(desired, existing)
            if merged == existing:
                plan.unchanged.append(site_id)
            else:
                plan.update.append(site_id)
                if apply:
                    _atomic_json(config_path, merged)
        else:
            plan.create.append(site_id)
            if apply:
                site_dir.mkdir(parents=True, exist_ok=True)
                posts = site_dir / "_posts"
                posts.mkdir(exist_ok=True)
                (posts / ".gitkeep").touch(exist_ok=True)
                _atomic_json(config_path, desired)

    if SITES.exists():
        for site_dir in sorted(SITES.iterdir()):
            config_path = site_dir / "site.json"
            if not config_path.exists() or site_dir.name in desired_ids:
                continue
            existing = json.loads(config_path.read_text(encoding="utf-8"))
            if existing.get("portfolioManaged") or "portfolioVersion" in existing:
                plan.stale.append(site_dir.name)
    return plan


def materialize(document: dict[str, Any]) -> int:
    """Backward-compatible helper: create/sync and return only the create count."""
    return len(sync_document(document, apply=True).create)


def import_portfolio(source: Path) -> dict[str, Any]:
    document = load_document(source)
    IDEAS_DIR.mkdir(parents=True, exist_ok=True)
    _atomic_json(IDEAS, document)
    return document


def _atomic_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _print_plan(plan: SyncPlan, *, dry_run: bool) -> None:
    prefix = "PLAN" if dry_run else "SYNC"
    for action, site_ids in (
        ("CREATE", plan.create),
        ("UPDATE", plan.update),
        ("UNCHANGED", plan.unchanged),
        ("STALE (kept)", plan.stale),
    ):
        for site_id in site_ids:
            print(f"{prefix} {action}: {site_id}")
    print(
        f"{prefix} SUMMARY: create={len(plan.create)} update={len(plan.update)} "
        f"unchanged={len(plan.unchanged)} stale={len(plan.stale)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import NicheScout ideas.json and safely sync grouped SEO sites"
    )
    parser.add_argument("--portfolio", type=Path, help="NicheScout ideas.json to import")
    parser.add_argument("--mock", action="store_true", help="Use an isolated three-product fixture")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--plan", action="store_true", help="Show changes without writing files")
    args = parser.parse_args()

    if args.portfolio and args.mock:
        parser.error("choose either --portfolio or --mock")
    if args.validate_only and args.plan:
        parser.error("choose either --validate-only or --plan")

    try:
        if args.mock:
            document = mock_document()
            validate_document(document)
        elif args.portfolio:
            document = load_document(args.portfolio)
        else:
            document = load_document()
    except PortfolioError as exc:
        raise SystemExit(f"Portfolio validation failed: {exc}") from exc

    site_count = len(normalized_sites(document))
    if args.validate_only:
        print(f"Valid portfolio: {len(document['ideas'])} products across {site_count} sites.")
        return

    plan = sync_document(document, apply=not args.plan)
    if args.portfolio and not args.plan:
        IDEAS_DIR.mkdir(parents=True, exist_ok=True)
        _atomic_json(IDEAS, document)
    _print_plan(plan, dry_run=args.plan)
    print(
        f"Portfolio contains {len(document['ideas'])} products across {site_count} "
        "audience-grouped sites."
    )


if __name__ == "__main__":
    main()
