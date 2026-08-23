#!/usr/bin/env python3
"""One-command portfolio launcher.

Typical commands:
  python scripts/launch.py                    # generate/build/deploy all sites
  python scripts/launch.py --frontend-only   # redeploy shared frontend to all sites
  python scripts/launch.py --blogs-only      # regenerate blogs and redeploy all sites
  python scripts/launch.py --site my-site    # process one site
  python scripts/launch.py --skip-generation # publish existing Markdown without regenerating
"""
from __future__ import annotations

import argparse
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
    if config.get("domain"):
        return "https://" + config["domain"].rstrip("/")
    return f"https://{config.get('deploy', {}).get('project', config['id'])}.pages.dev"


def health(url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "seo-site-monitor/1.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            return {"ok": 200 <= response.status < 400, "status": response.status, "url": url}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate, deploy, and monitor the entire SEO site portfolio")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--frontend-only", action="store_true", help="Skip Gemini and redeploy the current frontend/blog files")
    mode.add_argument("--blogs-only", action="store_true", help="Regenerate Markdown, rebuild, and redeploy")
    parser.add_argument("--site", help="Process only this site id")
    parser.add_argument("--limit", type=int, default=0, help="Process only the first N sites; useful for a smoke test")
    parser.add_argument("--skip-generation", action="store_true", help="Do not regenerate Markdown; publish existing files")
    parser.add_argument("--provider", default="cloudflare-pages", choices=["cloudflare-pages", "cloudflare-workers", "vercel", "netlify", "static"])
    args = parser.parse_args()

    run([sys.executable, "scripts/ideas.py"])
    sites = sorted(p for p in SITES.iterdir() if (p / "site.json").exists())
    if args.site:
        sites = [p for p in sites if p.name == args.site]
        if not sites:
            raise SystemExit(f"Unknown site '{args.site}'")
    if args.limit:
        sites = sites[:args.limit]
    print(f"Processing {len(sites)} sites", flush=True)

    STATE.mkdir(parents=True, exist_ok=True)
    shared_posthog = {}
    if not args.frontend_only or os.environ.get("POSTHOG_PERSONAL_API_KEY"):
        from monitoring import provision_shared_posthog
        shared_posthog = provision_shared_posthog()
        if shared_posthog:
            print(f"Using shared PostHog project: {shared_posthog.get('posthogProjectName')}", flush=True)

    results = []
    force_generation = args.blogs_only and not args.skip_generation
    skip_generation = args.frontend_only or args.skip_generation

    for index, site_dir in enumerate(sites, 1):
        site_id = site_dir.name
        started = time.time()
        result = {"site": site_id, "startedAt": time.time()}
        try:
            config = json.loads((site_dir / "site.json").read_text(encoding="utf-8"))
            config.setdefault("deploy", {})["provider"] = args.provider
            target_url = site_url(config)
            from monitoring import provision
            config = provision(config, site_dir, target_url, shared_posthog)

            posts_exist = bool(list((site_dir / "_posts").glob("*.md")))
            if not skip_generation and (force_generation or not posts_exist):
                run([sys.executable, "scripts/generate_posts.py", site_id])

            env = os.environ.copy()
            env["SITE_URL"] = target_url
            monitoring = config.get("monitoring", {})
            if monitoring.get("googleVerificationToken"):
                env["GOOGLE_SITE_VERIFICATION"] = monitoring["googleVerificationToken"]
            if monitoring.get("posthogKey"):
                env["NEXT_PUBLIC_POSTHOG_KEY"] = monitoring["posthogKey"]
                env["NEXT_PUBLIC_POSTHOG_HOST"] = monitoring.get("posthogHost", "https://us.i.posthog.com")
            env["SEO_POSTS_DIR"] = str((site_dir / "_posts").resolve())
            run(["npm", "run", "build"], env=env)
            if args.provider != "static":
                run([sys.executable, "scripts/site.py", "deploy", site_id, args.provider], env=env)

            from monitoring import finalize
            finalize(config)
            result.update({"ok": True, "url": target_url, "health": health(target_url)})
        except Exception as exc:
            result.update({"ok": False, "error": str(exc)})
        result["durationSeconds"] = round(time.time() - started, 2)
        results.append(result)
        (STATE / f"{site_id}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"[{index}/{len(sites)}] {site_id}: {'OK' if result['ok'] else 'FAILED'}", flush=True)

    summary = {
        "timestamp": time.time(), "total": len(results),
        "successful": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"]), "results": results,
    }
    (STATE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("total", "successful", "failed")}, indent=2))
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
