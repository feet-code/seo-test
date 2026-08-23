#!/usr/bin/env python3
"""One-command portfolio launcher.

First run:
  python scripts/launch.py

The command creates the editable 99-idea portfolio (if ideas.json is absent),
materializes site.json files, provisions monitoring/hosting, generates posts,
builds each site, deploys it, and writes a machine-readable status report.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"
STATE = ROOT / ".deploy" / "state"


def run(args: list[str], env=None) -> None:
    print("$", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, env=env or os.environ.copy(), check=True)


def site_url(config: dict) -> str:
    domain = config.get("domain")
    if domain:
        return "https://" + domain.rstrip("/")
    project = config.get("deploy", {}).get("project", config["id"])
    return f"https://{project}.pages.dev"


def health(url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "seo-site-monitor/1.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            return {"ok": 200 <= response.status < 400, "status": response.status, "url": url}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate, deploy, and monitor the entire SEO site portfolio")
    parser.add_argument("--limit", type=int, default=0, help="Only process the first N sites; useful for a smoke test")
    parser.add_argument("--skip-generation", action="store_true", help="Do not regenerate Markdown already present")
    parser.add_argument("--provider", default="cloudflare-pages", choices=["cloudflare-pages", "cloudflare-workers", "vercel", "netlify", "static"])
    args = parser.parse_args()

    run([sys.executable, "scripts/ideas.py"])
    sites = sorted(p for p in SITES.iterdir() if (p / "site.json").exists())
    if args.limit:
        sites = sites[:args.limit]
    print(f"Processing {len(sites)} sites", flush=True)
    STATE.mkdir(parents=True, exist_ok=True)
    results = []

    for index, site_dir in enumerate(sites, 1):
        site_id = site_dir.name
        started = time.time()
        result = {"site": site_id, "startedAt": time.time()}
        try:
            config = json.loads((site_dir / "site.json").read_text(encoding="utf-8"))
            config.setdefault("deploy", {})["provider"] = args.provider
            # Provisioning can create the host project and monitoring credentials/tokens.
            from monitoring import provision
            provision(config, site_dir)
            config = json.loads((site_dir / "site.json").read_text(encoding="utf-8"))

            if not args.skip_generation and not list((site_dir / "_posts").glob("*.md")):
                run([sys.executable, "scripts/generate_posts.py", site_id])

            env = os.environ.copy()
            env["SITE_URL"] = site_url(config)
            monitoring = config.get("monitoring", {})
            if monitoring.get("googleVerificationToken"):
                env["GOOGLE_SITE_VERIFICATION"] = monitoring["googleVerificationToken"]
            if monitoring.get("posthogKey"):
                env["NEXT_PUBLIC_POSTHOG_KEY"] = monitoring["posthogKey"]
                env["NEXT_PUBLIC_POSTHOG_HOST"] = monitoring.get("posthogHost", "https://us.i.posthog.com")
            env["SEO_POSTS_DIR"] = str((site_dir / "_posts").resolve())
            run(["npm", "run", "build"], env=env)
            if args.provider != "static":
                # site.py also knows how to create/reuse provider resources. Cloudflare Pages
                # creation is additionally handled by the API provisioning step above.
                run([sys.executable, "scripts/site.py", "deploy", site_id, args.provider], env=env)

            from monitoring import finalize
            finalize(config)
            result.update({"ok": True, "url": site_url(config), "health": health(site_url(config))})
        except Exception as exc:
            result.update({"ok": False, "error": str(exc)})
        result["durationSeconds"] = round(time.time() - started, 2)
        results.append(result)
        (STATE / f"{site_id}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"[{index}/{len(sites)}] {site_id}: {'OK' if result['ok'] else 'FAILED'}", flush=True)

    summary = {
        "timestamp": time.time(),
        "total": len(results),
        "successful": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"]),
        "results": results,
    }
    (STATE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("total", "successful", "failed")}, indent=2))
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
