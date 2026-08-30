#!/usr/bin/env python3
"""Generate, import, validate, and safely sync profitability-first SEO probes."""
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
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]
IDEA_GENERATION_VERSION = 3
DEFAULT_IDEA_COUNT = 100
DEFAULT_BATCH_SIZE = 5
MAX_BATCH_SIZE = 10
PROFIT_SCORE_WEIGHTS = {
    "economicPain": 15,
    "buyerBudget": 10,
    "recurrenceRetention": 10,
    "monetizationExpansion": 15,
    "searchDemand": 10,
    "commercialIntent": 10,
    "contentDepth": 10,
    "serpWinnability": 10,
    "buildSupportFeasibility": 10,
}


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
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.65,
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
                if exc.code == 401:
                    raise GenerationError(
                        f"Gemini authentication failed: HTTP {exc.code}"
                    ) from exc
                if exc.code == 403:
                    # A free-tier key can be valid while one model is unavailable
                    # or quota-blocked. Continue through the configured model chain.
                    break
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


def _generation_plan(count: int, batch_size: int) -> list[dict[str, int | str]]:
    return [
        {
            "id": f"batch-{index + 1:03d}",
            "offset": offset,
            "productCount": min(batch_size, count - offset),
        }
        for index, offset in enumerate(range(0, count, batch_size))
    ]


def _profitability_batch_prompt(
    batch: dict[str, Any],
    used_ideas: list[dict[str, str]],
) -> str:
    count = int(batch["productCount"])
    return f"""Use Google Search and return exactly {count} independent, profit-and-SEO-first micro-SaaS
finalists as a JSON array. You are selecting investment hypotheses, not brainstorming filler. Silently examine
at least {count * 4} candidates across different industries and return only the strongest {count} at the
intersection of expected bootstrapped profit and attainable organic-search acquisition.

Each finalist gets its own website and does NOT need to share an audience, topic, or product family with any
other finalist. Do not group ideas. Optimize the probability of durable bootstrapped profit, subject to a solo
technical founder being able to launch a narrow MVP without employees or large upfront capital.

Prioritize products tied directly to an economic event: winning or recovering revenue, raising margin,
utilizing scarce capacity, preventing an expensive operational risk, enabling a transaction, retaining a
valuable customer, or eliminating a measurable recurring cost. A workflow is not valuable by itself. Reject
thin dashboards, generic trackers, queues, checklists, directories, generic AI wrappers, and products that a
buyer can reproduce in a spreadsheet in under an hour unless there is a defensible data, automation,
optimization, transaction, or compliance advantage.

Prefer specific business buyers with budgets, frequent pain, strong retention mechanics, high-intent organic
searches, weak or disliked substitutes, and room to expand pricing or product depth. SEO must be a credible
primary acquisition channel, not an afterthought: the named buyer must already search for the problem, method,
calculator, comparison, or software category; the idea must support several durable, non-duplicative content
clusters; and a focused new site must have a plausible path around incumbent vendors, marketplaces, publishers,
and government domains. Reject ideas that mainly require outbound sales, depend on a single head keyword, have
only generic informational traffic, or cannot naturally connect useful articles to the product's money outcome.
Do not invent keyword volume or ranking difficulty. Treat broad or incumbent-dominated SERPs skeptically.

Include a deliberate mix
of revenue capture, pricing/margin, forecasting/optimization, capacity/scheduling, risk/evidence,
transactional, integration/data, and customer-retention products. Do not default to monthly subscriptions:
choose the business model that best captures value. Avoid medical diagnosis, legal advice, lending/insurance
underwriting, custody of funds, hardware, two-sided-market cold starts, expensive proprietary data, and ideas
requiring enterprise sales before validation. Do not invent market-size, search-volume, or ROI statistics.

Return ONLY a JSON array. Every object must contain:
- id, name, siteName, audience, buyer, product, problem, valueProposition, topic
- economicDriver, monetization, startupCost, seoAngle, seoThesis, profitRationale, primaryRisk
- marketEvidence: at least 2 short evidence objects with signal and sourceUrl, based on your searches
- searchQueries: at least 6 realistic queries spanning commercial software, problem-aware, calculator/template,
  comparison/alternative, pricing/cost, and specific how-to intent; never include invented volume numbers
- scoreBreakdown: integer 1-10 values for economicPain, buyerBudget, recurrenceRetention,
  monetizationExpansion, searchDemand, commercialIntent, contentDepth, serpWinnability,
  and buildSupportFeasibility

Scoring meanings: 10 is unusually strong, 5 is uncertain/average, and 1 is disqualifying. Be skeptical. Budget
means the named buyer can plausibly approve meaningful spend. MonetizationExpansion covers value-based pricing,
account growth, and adjacent paid depth. Search demand measures how naturally and repeatedly buyers search;
commercial intent measures proximity to a purchase; content depth measures how many genuinely useful clusters
can be published without thin repetition; and SERP winnability must score low when dominant software, publishers,
marketplaces, or government sites control the relevant results. Build/support feasibility includes integrations,
onboarding, data access, reliability, and customer support—not just coding. Use varied scores; do not make every
idea an 8 or 9. The program computes the weighted total, so do not return an overall score.

Already selected ideas to avoid duplicating or lightly renaming:
{json.dumps(used_ideas[-60:], ensure_ascii=False)}"""


def _profitability_score(raw: Any, index: int) -> tuple[dict[str, int], int]:
    if not isinstance(raw, dict):
        raise ValueError(f"product {index} scoreBreakdown must be an object")
    scores: dict[str, int] = {}
    for name, weight in PROFIT_SCORE_WEIGHTS.items():
        try:
            value = int(raw.get(name))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"product {index} has invalid {name} score") from exc
        if not 1 <= value <= 10:
            raise ValueError(f"product {index} {name} score must be 1..10")
        scores[name] = value
    total = round(
        sum(scores[name] * weight for name, weight in PROFIT_SCORE_WEIGHTS.items())
        / 10
    )
    return scores, total


def _evidence_items(raw: Any, index: int) -> list[dict[str, str]]:
    if not isinstance(raw, list) or len(raw) < 2:
        raise ValueError(f"product {index} needs at least two marketEvidence items")
    evidence: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError(f"product {index} marketEvidence item is not an object")
        signal = str(item.get("signal", "")).strip()
        source = str(item.get("sourceUrl", "")).strip()
        if not signal or not source.startswith(("https://", "http://")):
            raise ValueError(
                f"product {index} marketEvidence needs signal and sourceUrl"
            )
        evidence.append({"signal": signal, "sourceUrl": source})
    return evidence


def _profit_probe_context(values: dict[str, str]) -> dict[str, Any]:
    topic = values["topic"]
    buyer = values["buyer"]
    driver = values["economicDriver"]
    return {
        "outcome": values["valueProposition"],
        "workflow": [
            f"Collect the minimum source records needed to evaluate {topic}.",
            "Normalize revenue, cost, volume, timing, and exception inputs before calculation.",
            f"Calculate the {driver} result and expose the assumptions behind it.",
            f"Let the {buyer} approve an action and compare the eventual result with the forecast.",
        ],
        "fields": [
            "source record and reporting period",
            "customer, job, asset, location, or contract identifier",
            "revenue or avoided-loss amount",
            "variable cost and allocated capacity cost",
            "volume, timing, utilization, or risk inputs",
            "recommended action, owner, confidence, and review date",
        ],
        "mistakes": [
            "Treating revenue as profit while omitting variable and capacity costs.",
            "Automating a recommendation before source data and assumptions are reviewable.",
            "Using one threshold for unlike customers, jobs, assets, or seasons.",
            "Measuring recommendations without recording the action and eventual outcome.",
        ],
        "metrics": [
            {
                "name": "incremental gross profit or avoided loss",
                "formula": "realized revenue plus avoided loss minus variable and capacity cost",
                "decision": "keep only actions that create a positive realized contribution",
            },
            {
                "name": "financial realization rate",
                "formula": "realized financial result divided by the approved expected result",
                "decision": "find recommendations whose promised value does not survive execution",
            },
            {
                "name": "forecast error",
                "formula": "absolute expected-versus-realized difference divided by the realized result",
                "decision": "recalibrate assumptions or separate unlike cases",
            },
            {
                "name": "decision cycle time",
                "formula": "approved-action timestamp minus qualifying-trigger timestamp",
                "decision": "remove delays that cause an otherwise valuable opportunity to expire",
            },
        ],
        "alternatives": [
            {
                "name": "Owner-maintained spreadsheet",
                "best": "volume is low, one person owns the decision, and assumptions change often",
                "limit": "manual joins and inconsistent follow-through become hard to audit",
            },
            {
                "name": "Existing industry-system reports",
                "best": "the source system already contains costs, outcomes, and decision rules",
                "limit": "reports often stop at activity or revenue instead of the full money outcome",
            },
            {
                "name": "General BI tool or analyst",
                "best": "the buyer has data skills and needs several adjacent analyses",
                "limit": "analysis alone may not put an approved action back into the operating cycle",
            },
        ],
        "triggers": [
            "a new quote, order, job, customer, asset, or contract",
            "a material change in cost, price, utilization, or timing",
            "a renewal, repricing, planning, or exception-review cycle",
        ],
        "examples": [
            "a high-revenue case that becomes unattractive after variable costs",
            "an underused capacity slot where a targeted action creates incremental margin",
            "an exception whose missing evidence would otherwise hide revenue or increase risk",
        ],
        "rules": [
            "Never recommend an action when required source inputs are missing or stale.",
            "Show the financial formula and assumptions beside every recommendation.",
            "Require human approval for customer-facing price, contract, or schedule changes.",
            "Recalculate after the realized outcome so future recommendations can improve.",
        ],
    }


def _normalize_products(
    payload: Any,
    batch: dict[str, Any],
    used_ids: set[str],
) -> list[dict[str, Any]]:
    expected = int(batch["productCount"])
    if not isinstance(payload, list) or len(payload) != expected:
        actual = len(payload) if isinstance(payload, list) else "invalid"
        raise ValueError(f"idea batch contains {actual} products; expected {expected}")
    local_ids = set(used_ids)
    result: list[dict[str, Any]] = []
    required = (
        "name",
        "siteName",
        "audience",
        "buyer",
        "product",
        "problem",
        "valueProposition",
        "topic",
        "economicDriver",
        "monetization",
        "startupCost",
        "seoAngle",
        "seoThesis",
        "profitRationale",
        "primaryRisk",
    )
    for index, raw in enumerate(payload):
        if not isinstance(raw, dict):
            raise ValueError(f"product {index} is not an object")
        values = {name: str(raw.get(name, "")).strip() for name in required}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise ValueError(f"product {index} is missing {', '.join(missing)}")
        product_id = _unique_slug(raw.get("id") or values["name"], local_ids, limit=58)
        search_queries = [
            str(value).strip()
            for value in (raw.get("searchQueries") or [])
            if str(value).strip()
        ]
        if len(search_queries) < 6:
            raise ValueError(f"product {index} needs at least six searchQueries")
        scores, score = _profitability_score(raw.get("scoreBreakdown"), index)
        result.append(
            {
                "id": product_id,
                "siteId": product_id,
                "siteName": values["siteName"],
                "name": values["name"],
                "product": values["product"],
                "audience": values["audience"],
                "buyer": values["buyer"],
                "problem": values["problem"],
                "valueProposition": values["valueProposition"],
                "topic": values["topic"],
                "economicDriver": values["economicDriver"],
                "monetization": values["monetization"],
                "startupCost": values["startupCost"],
                "seoAngle": values["seoAngle"],
                "seoThesis": values["seoThesis"],
                "profitRationale": values["profitRationale"],
                "primaryRisk": values["primaryRisk"],
                "marketEvidence": _evidence_items(raw.get("marketEvidence"), index),
                "searchQueries": search_queries,
                "scoreBreakdown": scores,
                "score": score,
                "contentBatch": "profitability-generated",
                "probeContext": _profit_probe_context(values),
                "domain": None,
            }
        )
    return result


_MOCK_PROFIT_IDEAS = (
    (
        "Pool Route Margin",
        "owners of residential pool service companies",
        "route-level account profitability and repricing",
        "margin",
    ),
    (
        "Shop Bay Yield",
        "independent auto repair shop owners",
        "repair bay utilization and schedule profitability",
        "capacity",
    ),
    (
        "Distributor Margin Leak",
        "specialty wholesale distributors",
        "order-line margin leakage detection",
        "margin",
    ),
    (
        "Agency Fee Burn",
        "small professional-service agencies",
        "project fee burn and profitability forecasting",
        "risk",
    ),
    (
        "Venue Date Yield",
        "independent wedding and event venues",
        "event-date pricing and displacement analysis",
        "revenue",
    ),
)


def mock_products(
    batch: dict[str, Any],
    used_ids: set[str],
) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    offset = int(batch.get("offset", 0))
    for local_index in range(int(batch["productCount"])):
        absolute = offset + local_index
        name, audience, topic, driver = _MOCK_PROFIT_IDEAS[
            absolute % len(_MOCK_PROFIT_IDEAS)
        ]
        cycle = absolute // len(_MOCK_PROFIT_IDEAS) + 1
        label = name if cycle == 1 else f"{name} {cycle}"
        payload.append(
            {
                "id": slug(label),
                "name": label,
                "siteName": label,
                "audience": audience,
                "buyer": "owner or general manager",
                "product": f"A focused decision tool for {topic}.",
                "problem": f"The buyer cannot reliably quantify {topic} before money is lost.",
                "valueProposition": f"Turns operating data into an explainable {driver} decision.",
                "topic": topic,
                "economicDriver": driver,
                "monetization": "$99-$299/month based on locations or transaction volume",
                "startupCost": "Solo-buildable web MVP with managed storage and CSV imports.",
                "seoAngle": f"Commercial software and calculator searches for {topic}.",
                "seoThesis": (
                    "A narrow industry site can connect decision guides, calculators, "
                    "comparisons, and software pages to the same measurable money outcome."
                ),
                "profitRationale": "The product is attached to a measurable financial decision.",
                "primaryRisk": "Source data may require customer onboarding and cleanup.",
                "marketEvidence": [
                    {"signal": "Buyers already track the decision in operating software.", "sourceUrl": "https://example.com/source-one"},
                    {"signal": "The decision recurs as volume or schedules change.", "sourceUrl": "https://example.com/source-two"},
                ],
                "searchQueries": [
                    f"{topic} software",
                    f"{topic} calculator",
                    f"best tool for {topic}",
                    f"how to improve {topic}",
                    f"{topic} software pricing",
                    f"{topic} spreadsheet alternative",
                ],
                "scoreBreakdown": {
                    "economicPain": 8,
                    "buyerBudget": 7,
                    "recurrenceRetention": 8,
                    "monetizationExpansion": 7,
                    "searchDemand": 7,
                    "commercialIntent": 8,
                    "contentDepth": 8,
                    "serpWinnability": 6,
                    "buildSupportFeasibility": 8,
                },
            }
        )
    return _normalize_products(payload, batch, used_ids)


def _generation_settings(count: int, batch_size: int, mock: bool) -> dict[str, Any]:
    return {
        "count": count,
        "batchSize": batch_size,
        "mock": mock,
        "generationVersion": IDEA_GENERATION_VERSION,
        "objective": "maximum-profit-and-attainable-seo-independent-products",
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
    batch_size: int = DEFAULT_BATCH_SIZE,
    *,
    mock: bool = False,
    regenerate: bool = False,
) -> dict[str, Any]:
    """Generate or resume independent finalists, replacing ideas.json only when complete."""
    if count < 1:
        raise GenerationError("count must be at least 1")
    if not 1 <= batch_size <= MAX_BATCH_SIZE:
        raise GenerationError(f"batch size must be 1..{MAX_BATCH_SIZE}")
    mock = mock or os.getenv("MOCK_LLM", "").lower() in {"1", "true", "yes"}
    settings = _generation_settings(count, batch_size, mock)
    state = None if regenerate else _load_generation_state(settings)

    if state and state.get("complete") and IDEAS.exists():
        document = load_document(IDEAS)
        generation = document.get("generation", {})
        if generation.get("runId") == state.get("runId"):
            print(f"Reusing completed idea-generation run {state['runId']}.")
            return document

    if state is None:
        plan = _generation_plan(count, batch_size)
        print(
            f"Generating {count} independent profitability finalists in "
            f"{len(plan)} restart-safe batches...",
            flush=True,
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
            "profitability batches complete.",
            flush=True,
        )

    completed = state["completedProducts"]
    plan_ids = {batch["id"] for batch in plan}
    unexpected = set(completed) - plan_ids
    if unexpected:
        raise GenerationError(
            "Idea-generation checkpoint contains unknown batches; "
            "use --regenerate to start a fresh run"
        )
    used_ids: set[str] = set()
    used_ideas: list[dict[str, str]] = []
    for batch in plan:
        products = completed.get(batch["id"])
        if products is None:
            continue
        if not isinstance(products, list) or len(products) != batch["productCount"]:
            raise GenerationError(
                f"Checkpoint batch {batch['id']} is incomplete; use --regenerate"
            )
        for product in products:
            product_id = str(product.get("id", ""))
            if not product_id or product_id in used_ids:
                raise GenerationError(
                    "Checkpoint has missing or duplicate product IDs; use --regenerate"
                )
            used_ids.add(product_id)
            used_ideas.append(
                {
                    "name": str(product.get("name", "")),
                    "audience": str(product.get("audience", "")),
                    "topic": str(product.get("topic", "")),
                }
            )

    for index, batch in enumerate(plan, 1):
        if batch["id"] in completed:
            print(
                f"[{index}/{len(plan)}] {batch['id']}: checkpoint complete "
                f"({batch['productCount']} finalists)",
                flush=True,
            )
            continue
        print(
            f"[{index}/{len(plan)}] Researching and selecting "
            f"{batch['productCount']} independent finalists...",
            flush=True,
        )
        if mock:
            products = mock_products(batch, used_ids)
        else:
            products = _call_gemini_json(
                _profitability_batch_prompt(batch, used_ideas),
                f"profitability finalists {batch['id']}",
                lambda payload, current=batch: _normalize_products(
                    payload, current, used_ids
                ),
            )
        completed[batch["id"]] = products
        used_ids.update(product["id"] for product in products)
        used_ideas.extend(
            {
                "name": str(product["name"]),
                "audience": str(product["audience"]),
                "topic": str(product["topic"]),
            }
            for product in products
        )
        state["updatedAt"] = _utc_timestamp()
        _atomic_json(_generation_checkpoint(), state)

    ideas = [product for batch in plan for product in completed[batch["id"]]]
    document = {
        "version": 2,
        "articlesPerProduct": 10,
        "generatedAt": _utc_timestamp(),
        "generation": {
            "source": "seo-test",
            "mode": "mock" if mock else "gemini",
            "runId": state["runId"],
            "requestedProducts": count,
            "requestedSites": count,
            "batchSize": batch_size,
            "objective": "maximum expected bootstrapped profitability and attainable SEO",
            "grouping": "none; every product is an independent one-product site",
            "grounding": "Google Search enabled for every Gemini model",
            "scoreWeights": PROFIT_SCORE_WEIGHTS,
        },
        "sites": [
            {
                "id": product["siteId"],
                "name": product["siteName"],
                "audience": product["audience"],
                "topic": product["topic"],
                "domain": None,
            }
            for product in ideas
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
        "seoThesis": idea.get("seoThesis", ""),
        "searchQueries": idea.get("searchQueries", []),
        "buyer": idea.get("buyer", ""),
        "economicDriver": idea.get("economicDriver", ""),
        "profitRationale": idea.get("profitRationale", ""),
        "primaryRisk": idea.get("primaryRisk", ""),
        "scoreBreakdown": idea.get("scoreBreakdown", {}),
        "score": idea.get("score"),
        "contentBatch": idea.get("contentBatch", ""),
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
        "author": {"name": "John Smith"},
        "signup": {
            "enabled": True,
            "headline": "Interested? Get notified when this is available.",
            "endpoint": "",
            "email": "",
        },
        "deploy": {"provider": "cloudflare-auto", "project": site_id},
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
    author = dict(existing.get("author") or desired["author"])
    author.pop("picture", None)
    merged["author"] = author
    merged.pop("images", None)
    for name in ("signup", "deploy"):
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
        description="Generate/import independent profitability-first SEO probes"
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
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=(
            "Independent finalists per grounded Gemini call "
            f"(default: {DEFAULT_BATCH_SIZE}, max: {MAX_BATCH_SIZE})"
        ),
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
    if not 1 <= args.batch_size <= MAX_BATCH_SIZE:
        parser.error(f"--batch-size must be between 1 and {MAX_BATCH_SIZE}")

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
                args.batch_size,
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
        "sites."
    )
    if generating:
        print(f"Generated {IDEAS.relative_to(ROOT)} successfully.")
        print("Next: test one site with `python scripts/launch.py --limit 1`.")
        print("Then deploy all active sites with `python scripts/launch.py`.")


if __name__ == "__main__":
    main()
