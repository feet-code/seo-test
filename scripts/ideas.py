#!/usr/bin/env python3
"""Generate and materialize the editable portfolio of SEO micro-SaaS sites."""
from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDEAS = ROOT / "ideas.json"
SITES = ROOT / "sites"


def call_gemini(prompt: str) -> list[dict]:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is required")
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"},
    }
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as response:
        data = json.load(response)
    raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    raw = re.sub(r"^```json\s*|\s*```$", "", raw)
    ideas = json.loads(raw)
    if not isinstance(ideas, list) or len(ideas) != 99:
        raise SystemExit(f"Gemini returned {len(ideas) if isinstance(ideas, list) else 'invalid'} ideas; expected exactly 99")
    return ideas


def generate_ideas() -> list[dict]:
    prompt = """
Generate exactly 99 distinct micro-SaaS product/service ideas for a solo technical founder.
The objective is to identify opportunities that have a credible path to profitability, not
ideas that merely sound interesting. Favor painful, narrow business problems, clear buyers,
recurring revenue, strong willingness to pay, low infrastructure/API costs, and products
that can be built and operated by one person. Favor niches where SEO can acquire customers.
Avoid generic AI wrappers, broad project-management apps, saturated consumer apps, regulated
medical/financial/legal products, and ideas requiring expensive proprietary data or hardware.
Each idea must solve one specific problem for a specific customer.

For each idea return:
- id: kebab-case identifier
- name
- product: one sentence describing what it does
- audience: specific buyer/user
- problem: painful problem being solved
- valueProposition: why the buyer pays
- topic: SEO topic the companion blog should own
- monetization: plausible pricing model
- startupCost: why infrastructure can remain cheap
- seoAngle: why the niche can attract qualified search traffic
- score: integer 1-100 representing overall attractiveness
- domain: leave as null (the founder may add domains manually later)

Rank the array from highest to lowest opportunity score. Do not invent market-size numbers.
"""
    return call_gemini(prompt)


def load_or_generate() -> list[dict]:
    if IDEAS.exists():
        data = json.loads(IDEAS.read_text(encoding="utf-8"))
        return data.get("ideas", [])
    ideas = generate_ideas()
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
        # Never overwrite a manually edited site.json.
        if config_path.exists():
            continue
        config = {
            "id": site_id,
            "name": idea.get("name", site_id),
            "domain": idea.get("domain"),
            "product": idea.get("product", ""),
            "productUrl": "",
            "audience": idea.get("audience", ""),
            "topic": idea.get("topic", ""),
            "valueProposition": idea.get("valueProposition", idea.get("problem", "")),
            "articleCount": 5,
            "author": {"name": "JJ Kasper", "picture": "/assets/blog/authors/jj.jpeg"},
            "images": {
                "coverImage": "/assets/blog/preview/cover.jpg",
                "ogImage": "/assets/blog/dynamic-routing/cover.jpg",
            },
            "deploy": {"provider": "cloudflare-pages", "project": site_id},
            "ideaScore": idea.get("score"),
            "monetization": idea.get("monetization", ""),
            "startupCost": idea.get("startupCost", ""),
            "seoAngle": idea.get("seoAngle", ""),
        }
        site_dir.mkdir(parents=True, exist_ok=True)
        (site_dir / "_posts").mkdir(exist_ok=True)
        (site_dir / "_posts" / ".gitkeep").write_text("", encoding="utf-8")
        config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        count += 1
    return count


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate", action="store_true", help="Regenerate ideas.json; manual ideas will be lost")
    args = parser.parse_args()
    if args.regenerate:
        ideas = generate_ideas()
        IDEAS.write_text(json.dumps({"version": 1, "ideas": ideas}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        ideas = load_or_generate()
    print(f"Idea portfolio contains {len(ideas)} ideas; created {materialize(ideas)} new site configurations.")


if __name__ == "__main__":
    main()
