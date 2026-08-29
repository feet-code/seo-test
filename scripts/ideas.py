#!/usr/bin/env python3
"""Generate, import, validate, and safely sync an audience-grouped portfolio."""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
IDEAS_DIR = ROOT / "ideas"
IDEAS = IDEAS_DIR / "ideas.json"
SITES = ROOT / "sites"
STATE = ROOT / ".deploy" / "state"
DEFAULT_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]
IDEA_GENERATION_VERSION = 1
DEFAULT_IDEA_COUNT = 100
DEFAULT_PREFERRED_PRODUCTS = 5
DEFAULT_MAX_PRODUCTS = 8


class PortfolioError(ValueError):
    pass


class GenerationError(RuntimeError):
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


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generation_checkpoint() -> Path:
    return STATE / "ideas-generation.json"


def _generation_failure() -> Path:
    return STATE / "ideas-gemini-exhausted.json"


def _models() -> list[str]:
    raw = os.getenv("GEMINI_MODELS")
    values = [item.strip() for item in raw.split(",")] if raw else DEFAULT_MODELS
    return [
        item
        for index, item in enumerate(values)
        if item and item not in values[:index]
    ]


def _clean_json(text: str) -> Any:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    return json.loads(text)


def _call_model(model: str, prompt: str) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise GenerationError("GEMINI_API_KEY is required (or add --mock)")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.85,
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
        payload = json.load(response)
    return payload["candidates"][0]["content"]["parts"][0]["text"]


def _call_gemini_json(
    prompt: str,
    purpose: str,
    validator: Callable[[Any], Any],
) -> Any:
    attempts: list[dict[str, Any]] = []
    last_error: Exception | None = None
    for model in _models():
        for attempt in range(3):
            try:
                print(
                    f"  Gemini {purpose}: {model} attempt {attempt + 1}/3",
                    flush=True,
                )
                result = validator(_clean_json(_call_model(model, prompt)))
                attempts.append(
                    {"model": model, "attempt": attempt + 1, "status": "ok"}
                )
                failure = _generation_failure()
                if failure.exists():
                    failure.unlink()
                return result
            except GenerationError:
                raise
            except urllib.error.HTTPError as exc:
                last_error = exc
                attempts.append(
                    {"model": model, "attempt": attempt + 1, "status": exc.code}
                )
                if exc.code in {401, 403}:
                    raise GenerationError(
                        f"Gemini authentication failed: HTTP {exc.code}"
                    ) from exc
                if exc.code in {400, 404, 422}:
                    break
                if exc.code not in {408, 409, 425, 429, 500, 502, 503, 504}:
                    break
                time.sleep(min(30, 2 ** attempt * 2))
            except urllib.error.URLError as exc:
                last_error = exc
                attempts.append(
                    {"model": model, "attempt": attempt + 1, "status": "network"}
                )
                time.sleep(min(30, 2 ** attempt * 2))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                last_error = exc
                attempts.append(
                    {
                        "model": model,
                        "attempt": attempt + 1,
                        "status": type(exc).__name__,
                    }
                )
                if attempt < 2:
                    time.sleep(min(8, 2 ** attempt))

    _atomic_json(
        _generation_failure(),
        {
            "purpose": purpose,
            "timestamp": _utc_timestamp(),
            "models": _models(),
            "attempts": attempts,
            "error": str(last_error),
        },
    )
    raise GenerationError(f"All configured Gemini models failed for {purpose}: {last_error}")


def _unique_slug(value: Any, used: set[str], *, limit: int) -> str:
    base = slug(value)[:limit].strip("-") or "item"
    candidate = base
    suffix = 2
    while candidate in used:
        ending = f"-{suffix}"
        candidate = f"{base[: limit - len(ending)].rstrip('-')}{ending}"
        suffix += 1
    used.add(candidate)
    return candidate


def _audience_plan_prompt(count: int, preferred: int, maximum: int) -> str:
    return f"""Design an audience-grouped portfolio for exactly {count} distinct micro-SaaS products.

Return ONLY a JSON array. Each item must contain id, name, audience, topic, and productCount.
The sum of productCount must be exactly {count}; every productCount must be between 1 and {maximum}.

Group only products bought or used by the same specific buyer/audience. A single website should feel like a
coherent toolbox for that audience, not a random software directory. Choose group size from the number of
genuinely complementary opportunities. {preferred} is a soft planning target, not a quota: deliberately use
variable group sizes and never pad a group merely to reach {preferred}. Keep audiences narrow enough for one
SEO content strategy and distinct enough that websites do not compete for the same searches.

Favor painful business workflows, clear buyers, recurring revenue, willingness to pay, low infrastructure/API
costs, solo-founder feasibility, and organic-search acquisition. Avoid generic AI wrappers, broad project
management apps, saturated consumer apps, regulated medical/financial/legal products, expensive proprietary
data, and hardware. Do not include the products yet and do not invent market-size or keyword-volume numbers."""


def _normalize_audience_plan(
    payload: Any,
    count: int,
    preferred: int,
    maximum: int,
) -> list[dict[str, Any]]:
    if not isinstance(payload, list) or not payload:
        raise ValueError("audience plan must be a non-empty JSON array")
    result: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    for index, raw in enumerate(payload):
        if not isinstance(raw, dict):
            raise ValueError(f"audience plan item {index} is not an object")
        audience = str(raw.get("audience", "")).strip()
        topic = str(raw.get("topic", "")).strip()
        name = str(raw.get("name") or audience).strip()
        if not audience or not topic or not name:
            raise ValueError(f"audience plan item {index} is missing name/audience/topic")
        try:
            product_count = int(raw.get("productCount"))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"audience plan item {index} has an invalid productCount"
            ) from exc
        if not 1 <= product_count <= maximum:
            raise ValueError(
                f"audience plan item {index} productCount must be 1..{maximum}"
            )
        site_id = _unique_slug(raw.get("id") or name, used_ids, limit=58)
        result.append(
            {
                "id": site_id,
                "name": name,
                "audience": audience,
                "topic": topic,
                "productCount": product_count,
            }
        )
    actual = sum(site["productCount"] for site in result)
    if actual != count:
        raise ValueError(f"audience plan contains {actual} products; expected {count}")
    sizes = {site["productCount"] for site in result}
    if len(result) >= 3 and sizes == {preferred}:
        raise ValueError(
            f"audience plan padded every site to the soft target of {preferred}"
        )
    return result


_MOCK_AUDIENCES = (
    (
        "freelancer-operations",
        "Freelancer Operations",
        "freelancers and independent service businesses",
        "client operations for independent service businesses",
    ),
    (
        "property-manager-workflows",
        "Property Manager Workflows",
        "independent residential property managers",
        "tenant and vendor operations for small property portfolios",
    ),
    (
        "agency-client-delivery",
        "Agency Client Delivery",
        "small marketing and creative agencies",
        "repeatable client delivery workflows for small agencies",
    ),
    (
        "field-service-office",
        "Field Service Office",
        "owner-operated field service businesses",
        "office workflows for local field service teams",
    ),
    (
        "course-creator-operations",
        "Course Creator Operations",
        "independent cohort and course creators",
        "launch and learner operations for small education businesses",
    ),
    (
        "recruiter-desk-tools",
        "Recruiter Desk Tools",
        "independent recruiters and boutique recruiting firms",
        "candidate and client workflows for boutique recruiters",
    ),
    (
        "wholesale-operations",
        "Wholesale Operations",
        "small specialty wholesalers",
        "order and account workflows for specialty wholesalers",
    ),
    (
        "nonprofit-program-ops",
        "Nonprofit Program Operations",
        "small nonprofit program teams",
        "program delivery and reporting workflows for small nonprofits",
    ),
)


def mock_audience_plan(
    count: int,
    preferred: int = DEFAULT_PREFERRED_PRODUCTS,
    maximum: int = DEFAULT_MAX_PRODUCTS,
) -> list[dict[str, Any]]:
    pattern = [
        max(1, min(maximum, preferred - 2)),
        max(1, min(maximum, preferred + 2)),
        max(1, min(maximum, preferred - 3)),
        max(1, min(maximum, preferred)),
        max(1, min(maximum, preferred + 3)),
        max(1, min(maximum, preferred - 1)),
    ]
    remaining = count
    index = 0
    result: list[dict[str, Any]] = []
    while remaining:
        base_id, name, audience, topic = _MOCK_AUDIENCES[index % len(_MOCK_AUDIENCES)]
        cycle = index // len(_MOCK_AUDIENCES) + 1
        site_id = base_id if cycle == 1 else f"{base_id}-{cycle}"
        product_count = min(remaining, pattern[index % len(pattern)])
        result.append(
            {
                "id": site_id,
                "name": name if cycle == 1 else f"{name} {cycle}",
                "audience": audience,
                "topic": topic,
                "productCount": product_count,
            }
        )
        remaining -= product_count
        index += 1
    return result


def _products_prompt(
    site: dict[str, Any],
    used_names: list[str],
) -> str:
    count = site["productCount"]
    return f"""Generate exactly {count} distinct micro-SaaS products for one audience website.

Website: {site['name']}
Exact audience: {site['audience']}
Shared SEO territory: {site['topic']}

Return ONLY a JSON array. Every item must contain id, name, product, problem, valueProposition, topic,
monetization, startupCost, seoAngle, and score (integer 1-100). Do not include siteId or domain.

Every product must be bought or used by the exact audience above and must fit the shared SEO territory. Make
the products complementary but independently testable: do not create feature tiers, near-duplicates, or renamed
versions of one tool. Each should solve one narrow, painful workflow for a clear buyer, support a plausible
recurring-revenue offer, be feasible for a solo technical founder, and have a specific organic-search angle.
Avoid regulated workflows, generic AI wrappers, expensive proprietary data, hardware, invented statistics,
and claims about keyword volume. Previously generated names to avoid: {json.dumps(used_names[-40:])}."""


def _normalize_products(
    payload: Any,
    site: dict[str, Any],
    used_ids: set[str],
) -> list[dict[str, Any]]:
    expected = site["productCount"]
    if not isinstance(payload, list) or len(payload) != expected:
        actual = len(payload) if isinstance(payload, list) else "invalid"
        raise ValueError(f"product group contains {actual} products; expected {expected}")
    local_ids = set(used_ids)
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(payload):
        if not isinstance(raw, dict):
            raise ValueError(f"product {index} is not an object")
        name = str(raw.get("name", "")).strip()
        product = str(raw.get("product", "")).strip()
        problem = str(raw.get("problem", "")).strip()
        if not name or not product or not problem:
            raise ValueError(f"product {index} is missing name/product/problem")
        product_id = _unique_slug(raw.get("id") or name, local_ids, limit=80)
        try:
            score = max(1, min(100, int(float(raw.get("score", 70)))))
        except (TypeError, ValueError):
            score = 70
        value = str(raw.get("valueProposition") or problem).strip()
        topic = str(raw.get("topic") or site["topic"]).strip()
        result.append(
            {
                "id": product_id,
                "siteId": site["id"],
                "name": name,
                "product": product,
                "audience": site["audience"],
                "problem": problem,
                "valueProposition": value,
                "topic": topic,
                "monetization": str(
                    raw.get("monetization") or "Low-cost monthly subscription"
                ).strip(),
                "startupCost": str(
                    raw.get("startupCost")
                    or "Static frontend and inexpensive managed services"
                ).strip(),
                "seoAngle": str(
                    raw.get("seoAngle")
                    or f"High-intent searches around {topic}"
                ).strip(),
                "score": score,
                "domain": None,
            }
        )
    return result


def mock_products(
    site: dict[str, Any],
    used_ids: set[str],
) -> list[dict[str, Any]]:
    payload = []
    for index in range(1, site["productCount"] + 1):
        label = f"{site['name']} Workflow {index}"
        payload.append(
            {
                "id": slug(label),
                "name": label,
                "product": f"A focused workflow tool for {site['audience']}.",
                "problem": f"The audience manually repeats workflow {index} with inconsistent results.",
                "valueProposition": f"Makes workflow {index} repeatable without a broad business suite.",
                "topic": f"{site['topic']} workflow {index}",
                "monetization": "$19/month",
                "startupCost": "Static frontend and inexpensive managed storage.",
                "seoAngle": f"Templates and software searches for workflow {index}.",
                "score": 80 - (index % 10),
            }
        )
    return _normalize_products(payload, site, used_ids)


def _generation_settings(count: int, preferred: int, maximum: int, mock: bool) -> dict[str, Any]:
    return {
        "count": count,
        "preferredProductsPerSite": preferred,
        "maxProductsPerSite": maximum,
        "mock": mock,
        "generationVersion": IDEA_GENERATION_VERSION,
    }


def _load_generation_state(settings: dict[str, Any]) -> dict[str, Any] | None:
    path = _generation_checkpoint()
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GenerationError(
            f"Invalid idea-generation checkpoint {path}; use --regenerate to replace it"
        ) from exc
    if state.get("settings") != settings:
        return None
    if not isinstance(state.get("plan"), list) or not isinstance(
        state.get("completedProducts"), dict
    ):
        raise GenerationError(
            f"Incomplete idea-generation checkpoint {path}; use --regenerate to replace it"
        )
    return state


def generate_portfolio(
    count: int = DEFAULT_IDEA_COUNT,
    preferred: int = DEFAULT_PREFERRED_PRODUCTS,
    maximum: int = DEFAULT_MAX_PRODUCTS,
    *,
    mock: bool = False,
    regenerate: bool = False,
) -> dict[str, Any]:
    """Generate or resume a grouped portfolio, writing ideas.json only when complete."""
    if count < 1:
        raise GenerationError("count must be at least 1")
    if preferred < 1 or maximum < 1 or preferred > maximum:
        raise GenerationError("group sizes require 1 <= preferred <= maximum")
    mock = mock or os.getenv("MOCK_LLM", "").lower() in {"1", "true", "yes"}
    settings = _generation_settings(count, preferred, maximum, mock)
    state = None if regenerate else _load_generation_state(settings)

    if state and state.get("complete") and IDEAS.exists():
        document = load_document(IDEAS)
        generation = document.get("generation", {})
        if generation.get("runId") == state.get("runId"):
            print(f"Reusing completed idea-generation run {state['runId']}.")
            return document

    if state is None:
        print(f"Planning audience groups for {count} products...", flush=True)
        if mock:
            plan = mock_audience_plan(count, preferred, maximum)
        else:
            plan = _call_gemini_json(
                _audience_plan_prompt(count, preferred, maximum),
                "audience plan",
                lambda payload: _normalize_audience_plan(
                    payload, count, preferred, maximum
                ),
            )
        now = _utc_timestamp()
        state = {
            "version": IDEA_GENERATION_VERSION,
            "runId": f"{int(time.time() * 1000)}-{os.getpid()}",
            "createdAt": now,
            "updatedAt": now,
            "settings": settings,
            "plan": plan,
            "completedProducts": {},
            "complete": False,
        }
        _atomic_json(_generation_checkpoint(), state)
    else:
        plan = state["plan"]
        print(
            f"Resuming idea generation: {len(state['completedProducts'])}/{len(plan)} "
            "audience groups complete.",
            flush=True,
        )

    completed = state["completedProducts"]
    plan_ids = {site["id"] for site in plan}
    unexpected = set(completed) - plan_ids
    if unexpected:
        raise GenerationError(
            "Idea-generation checkpoint contains unknown audience groups; "
            "use --regenerate to start a fresh run"
        )
    used_ids: set[str] = set()
    used_names: list[str] = []
    for site in plan:
        products = completed.get(site["id"])
        if products is None:
            continue
        if not isinstance(products, list) or len(products) != site["productCount"]:
            raise GenerationError(
                f"Checkpoint group {site['id']} is incomplete; use --regenerate"
            )
        for product in products:
            product_id = str(product.get("id", ""))
            if not product_id or product_id in used_ids:
                raise GenerationError(
                    "Checkpoint has missing or duplicate product IDs; use --regenerate"
                )
            used_ids.add(product_id)
            used_names.append(str(product.get("name", "")))

    for index, site in enumerate(plan, 1):
        if site["id"] in completed:
            print(
                f"[{index}/{len(plan)}] {site['id']}: checkpoint complete "
                f"({site['productCount']} products)",
                flush=True,
            )
            continue
        print(
            f"[{index}/{len(plan)}] Generating {site['productCount']} products for "
            f"{site['audience']}...",
            flush=True,
        )
        if mock:
            products = mock_products(site, used_ids)
        else:
            products = _call_gemini_json(
                _products_prompt(site, used_names),
                f"products for {site['id']}",
                lambda payload, current=site: _normalize_products(
                    payload, current, used_ids
                ),
            )
        completed[site["id"]] = products
        used_ids.update(product["id"] for product in products)
        used_names.extend(str(product["name"]) for product in products)
        state["updatedAt"] = _utc_timestamp()
        _atomic_json(_generation_checkpoint(), state)

    ideas = [product for site in plan for product in completed[site["id"]]]
    document = {
        "version": 2,
        "articlesPerProduct": 10,
        "generatedAt": _utc_timestamp(),
        "generation": {
            "source": "seo-test",
            "mode": "mock" if mock else "gemini",
            "runId": state["runId"],
            "requestedProducts": count,
            "preferredProductsPerSite": preferred,
            "maxProductsPerSite": maximum,
            "grouping": "semantic audience plan with a soft preferred size",
        },
        "sites": [
            {
                "id": site["id"],
                "name": site["name"],
                "audience": site["audience"],
                "topic": site["topic"],
                "domain": None,
            }
            for site in plan
        ],
        "ideas": ideas,
    }
    validate_document(document)
    _atomic_json(IDEAS, document)
    state["complete"] = True
    state["completedAt"] = _utc_timestamp()
    state["updatedAt"] = state["completedAt"]
    _atomic_json(_generation_checkpoint(), state)
    return document


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
                "domain": None,
            }
        ],
        "ideas": products,
    }


def load_document(path: Path = IDEAS) -> dict[str, Any]:
    if not path.exists():
        raise PortfolioError(
            f"Portfolio not found: {path}. Generate it with --generate or import one "
            "with --portfolio PATH."
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

    _version_two_assignments(document)


def _version_two_assignments(
    document: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """Resolve idea membership with idea.siteId as the editable source of truth."""
    sites = document.get("sites")
    ideas = document.get("ideas")
    if not isinstance(sites, list) or not sites:
        raise PortfolioError("Version-2 portfolio requires a non-empty sites array")
    if not isinstance(ideas, list):
        raise PortfolioError("ideas must be an array")

    idea_by_id = {
        slug(idea.get("id") or idea.get("name")): idea
        for idea in ideas
        if isinstance(idea, dict)
    }
    site_ids: set[str] = set()
    site_by_id: dict[str, dict[str, Any]] = {}
    legacy_references: dict[str, list[str]] = {}
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
        site_by_id[site_id] = site

        raw_product_ids = site.get("productIds", [])
        if not isinstance(raw_product_ids, list):
            raise PortfolioError(f"Site {site_id!r} productIds must be an array")
        product_ids = [slug(item) for item in raw_product_ids]
        if len(product_ids) != len(set(product_ids)):
            raise PortfolioError(f"Site {site_id!r} repeats a product id")
        missing = set(product_ids) - set(idea_by_id)
        if missing:
            raise PortfolioError(
                f"Site {site_id!r} references unknown product(s): "
                + ", ".join(sorted(missing))
            )
        for product_id in product_ids:
            legacy_references.setdefault(product_id, []).append(site_id)

    assignments = {site_id: [] for site_id in site_ids}
    for idea_id, idea in idea_by_id.items():
        declared_site = slug(idea.get("siteId", ""))
        if declared_site:
            if declared_site not in site_by_id:
                raise PortfolioError(
                    f"Idea {idea_id!r} references unknown siteId={declared_site!r}"
                )
            assigned_site = declared_site
        else:
            legacy_sites = legacy_references.get(idea_id, [])
            if not legacy_sites:
                raise PortfolioError(
                    f"Idea {idea_id!r} needs siteId (or a legacy sites[].productIds assignment)"
                )
            if len(legacy_sites) > 1:
                raise PortfolioError(
                    f"Legacy product {idea_id!r} appears in multiple sites: "
                    + ", ".join(sorted(legacy_sites))
                )
            assigned_site = legacy_sites[0]
        assignments[assigned_site].append(idea)
    return assignments


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

    assignments = _version_two_assignments(document)
    return [
        (site, assignments[slug(site.get("id") or site.get("name"))])
        for site in document["sites"]
        if assignments[slug(site.get("id") or site.get("name"))]
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
        description="Generate/import ideas.json and safely sync audience-grouped SEO sites"
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--portfolio", type=Path, help="Existing ideas.json to import")
    source.add_argument(
        "--generate",
        action="store_true",
        help="Generate ideas.json, automatically resuming an interrupted run",
    )
    source.add_argument(
        "--regenerate",
        action="store_true",
        help="Discard the generation checkpoint and create a brand-new ideas.json",
    )
    parser.add_argument("--mock", action="store_true", help="Use an isolated three-product fixture")
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_IDEA_COUNT,
        help=f"Products to generate (default: {DEFAULT_IDEA_COUNT})",
    )
    parser.add_argument(
        "--preferred-products-per-site",
        type=int,
        default=DEFAULT_PREFERRED_PRODUCTS,
        help="Soft grouping target, never an exact quota",
    )
    parser.add_argument(
        "--max-products-per-site",
        type=int,
        default=DEFAULT_MAX_PRODUCTS,
        help="Hard audience-site size guardrail",
    )
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--plan", action="store_true", help="Show changes without writing files")
    args = parser.parse_args()

    if args.portfolio and args.mock:
        parser.error("--mock cannot be combined with --portfolio")
    if args.validate_only and args.plan:
        parser.error("choose either --validate-only or --plan")
    generating = args.generate or args.regenerate
    if generating and args.plan:
        parser.error("--plan cannot generate a new file; generate first, then run --plan")
    if args.count < 1:
        parser.error("--count must be at least 1")
    if not 1 <= args.preferred_products_per_site <= args.max_products_per_site:
        parser.error(
            "group sizes require 1 <= --preferred-products-per-site "
            "<= --max-products-per-site"
        )

    # Preserve the old first-run behavior without making dry-run commands mutate files.
    auto_generate = (
        not IDEAS.exists()
        and not args.portfolio
        and not args.mock
        and not args.plan
        and not args.validate_only
    )
    generating = generating or auto_generate

    try:
        if generating:
            document = generate_portfolio(
                args.count,
                args.preferred_products_per_site,
                args.max_products_per_site,
                mock=args.mock,
                regenerate=args.regenerate,
            )
        elif args.mock:
            document = mock_document()
            validate_document(document)
        elif args.portfolio:
            document = load_document(args.portfolio)
        else:
            document = load_document()
    except (GenerationError, PortfolioError) as exc:
        raise SystemExit(f"Portfolio preparation failed: {exc}") from exc

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
    if generating:
        print(f"Generated {IDEAS.relative_to(ROOT)} successfully.")
        print("Next: test one site with `python scripts/launch.py --limit 1`.")
        print("Then deploy all active sites with `python scripts/launch.py`.")


if __name__ == "__main__":
    main()
