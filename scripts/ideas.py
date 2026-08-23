#!/usr/bin/env python3
"""Generate and materialize the editable portfolio of SEO micro-SaaS sites."""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDEAS_DIR = ROOT / "ideas"
IDEAS = IDEAS_DIR / "ideas.json"
SITES = ROOT / "sites"


def mock_ideas() -> list[dict]:
    return [{
        "id": "example-invoice-followup",
        "name": "Example Invoice Follow-Up",
        "product": "A lightweight tool that reminds small businesses to follow up on overdue invoices.",
        "audience": "freelancers and small service businesses",
        "problem": "Small businesses lose time and cash manually tracking overdue invoices.",
        "valueProposition": "Automates polite payment reminders without requiring a full accounting platform.",
        "topic": "invoice follow-up and overdue invoice collection",
        "monetization": "low-cost monthly subscription",
        "startupCost": "Static frontend plus inexpensive email/API usage; no heavy infrastructure.",
        "seoAngle": "People search for invoice reminder templates, overdue invoice workflows, and payment follow-up tools.",
        "score": 75,
        "domain": None,
    }]


def call_gemini(prompt: str) -> list[dict]:
    if os.environ.get("MOCK_LLM", "").lower() in {"1", "true", "yes"}:
        return mock_ideas()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is required (or use --mock)")
    models = [m.strip() for m in os.environ.get("GEMINI_MODELS", "gemini-2.5-flash-lite,gemini-2.5-flash").split(",") if m.strip()]
    last_error = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        body = {"contents": [{"parts": [{"text": prompt}]}]}, "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"}}
        req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                data = json.load(response)
            raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            raw = re.sub(r"^```json\s*|\s*```$", "", raw)
            ideas = json.loads(raw)
            if not isinstance(ideas, list) or len(ideas) != 99:
                raise ValueError(f"expected 99 ideas, got {len(ideas) if isinstance(ideas, list) else 'invalid'}")
            return ideas
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {408, 429, 500, 502, 503, 504}:
                break
        except Exception as exc:
            last_error = exc
    raise SystemExit(f"All Gemini idea-generation models failed: {last_error}")


def generate_ideas() -> list[dict]:
    prompt = """
Generate exactly 99 distinct micro-SaaS product/service ideas for a solo technical founder.
Favor painful, narrow business problems, clear buyers, recurring revenue, willingness to pay,
low infrastructure/API costs, solo-founder feasibility, and SEO acquisition. Avoid generic AI
wrappers, broad project-management apps, saturated consumer apps, regulated medical/financial/
legal products, and ideas requiring expensive proprietary data or hardware.
Each idea must solve one specific problem for a specific customer.

For each idea return id, name, product, audience, problem, valueProposition, topic, monetization,
startupCost, seoAngle, score (1-100), and domain (null). Rank highest opportunity first.
Do not invent market-size numbers.
"""
    return call_gemini(prompt)


def load_or_generate(mock: bool = False) -> list[dict]:
    IDEAS_DIR.mkdir(parents=True, exist_ok=True)
    if IDEAS.exists():
        data = json.loads(IDEAS.read_text(encoding="utf-8"))
        return data.get("ideas", [])
    ideas = mock_ideas() if mock else generate_ideas()
    IDEAS.write_text(json.dumps({"version": 1, "ideas": ideas}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ideas


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def materialize(ideas: list[dict]) -> int:
    count = 0
    for idea in ideas:
        site_id = slug(str(idea.get("id") or idea.get("name", "")))
        if not site_id:
            continue
        site_dir = SITES / site_id
        config_path = site_dir / "site.json"
        if config_path.exists():
            continue
        config = {
            "id": site_id, "name": idea.get("name", site_id), "domain": idea.get("domain"),
            "product": idea.get("product", ""), "productUrl": "", "audience": idea.get("audience", ""),
            "topic": idea.get("topic", ""), "valueProposition": idea.get("valueProposition", idea.get("problem", "")),
            "articleCount": 5,
            "author": {"name": "John Smith", "picture": "/assets/blog/authors/jj.jpeg"},
            "images": {"coverImage": "/assets/blog/preview/cover.jpg", "ogImage": "/assets/blog/dynamic-routing/cover.jpg"},
            "signup": {"enabled": True, "headline": "Interested? Get notified when this is available.", "endpoint": "", "email": ""},
            "deploy": {"provider": "cloudflare-pages", "project": site_id},
            "ideaScore": idea.get("score"), "monetization": idea.get("monetization", ""),
            "startupCost": idea.get("startupCost", ""), "seoAngle": idea.get("seoAngle", ""),
        }
        site_dir.mkdir(parents=True, exist_ok=True)
        (site_dir / "_posts").mkdir(exist_ok=True)
        (site_dir / "_posts" / ".gitkeep").write_text("", encoding="utf-8")
        config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate", action="store_true", help="Regenerate ideas/ideas.json; manual ideas will be lost")
    parser.add_argument("--mock", action="store_true", help="Create a deterministic example without calling an LLM")
    args = parser.parse_args()
    if args.regenerate:
        ideas = mock_ideas() if args.mock else generate_ideas()
        IDEAS_DIR.mkdir(parents=True, exist_ok=True)
        IDEAS.write_text(json.dumps({"version": 1, "ideas": ideas}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        ideas = load_or_generate(mock=args.mock)
    print(f"Idea portfolio contains {len(ideas)} ideas; created {materialize(ideas)} new site configurations.")


if __name__ == "__main__":
    main()
