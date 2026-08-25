#!/usr/bin/env python3
"""Single CLI for generate -> build -> deploy across multiple hosting providers."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"
OUT = ROOT / "out"
DEPLOY = ROOT / ".deploy"


def site_config(site_id: str) -> tuple[dict, Path]:
    site_dir = SITES / site_id
    path = site_dir / "site.json"
    if not path.exists():
        raise SystemExit(f"Unknown site '{site_id}'. Expected {path}")
    return json.loads(path.read_text(encoding="utf-8")), site_dir


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    # Windows npm installs expose npx as npx.cmd, which subprocess cannot
    # resolve when invoked directly as "npx".
    if os.name == "nt" and command and command[0] == "npx":
        command = ["npx.cmd", *command[1:]]
    print("$", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True, encoding="utf-8", errors="replace")


def generate(site_id: str) -> None:
    run([sys.executable, "scripts/generate_posts.py", site_id])


def build(site_id: str, env_overrides: dict[str, str] | None = None) -> None:
    config, site_dir = site_config(site_id)
    env = os.environ.copy()
    products = config.get("products") or [{
        "id": config.get("id", site_id),
        "name": config.get("name", site_id),
        "product": config.get("product", ""),
        "audience": config.get("audience", ""),
        "problem": config.get("valueProposition", ""),
        "valueProposition": config.get("valueProposition", ""),
        "topic": config.get("topic", ""),
    }]
    monitoring = config.get("monitoring", {})
    signup = config.get("signup", {})
    env.update({
        "SEO_POSTS_DIR": str((site_dir / "_posts").resolve()),
        "SITE_NAME": config.get("name", site_id),
        "SITE_PRODUCT_NAME": config.get("name", site_id),
        "SITE_AUDIENCE": config.get("audience", ""),
        "SITE_TOPIC": config.get("topic", ""),
        "SITE_DESCRIPTION": config.get("valueProposition", config.get("topic", "")),
        "SITE_PRODUCTS_JSON": json.dumps(products, ensure_ascii=False),
        "SIGNUP_ENDPOINT": signup.get("endpoint", ""),
        "SIGNUP_EMAIL": signup.get("email", ""),
        "SIGNUP_HEADLINE": signup.get("headline", "Interested? Get notified when this is available."),
        "GOOGLE_SITE_VERIFICATION": monitoring.get("googleVerificationToken", ""),
        "NEXT_PUBLIC_POSTHOG_KEY": monitoring.get("posthogKey", ""),
        "NEXT_PUBLIC_POSTHOG_HOST": monitoring.get("posthogHost", "https://us.i.posthog.com"),
    })
    if env_overrides:
        env.update(env_overrides)
    if OUT.exists():
        shutil.rmtree(OUT)
    run(["npm", "run", "build"], env=env)
    if not OUT.exists():
        raise SystemExit("Build completed but out/ was not produced.")


def deploy(site_id: str, provider: str) -> None:
    config, _ = site_config(site_id)
    project = config.get("deploy", {}).get("project", config.get("id", site_id))
    if not OUT.exists():
        raise SystemExit("out/ does not exist. Run the build command first.")
    env = os.environ.copy()

    if provider == "static":
        print(f"Static artifact ready at {OUT}")
        return
    if provider == "cloudflare-pages":
        run(["npx", "wrangler", "pages", "deploy", str(OUT), "--project-name", project, "--branch=main"], env=env)
        return
    if provider == "cloudflare-workers":
        deploy_dir = DEPLOY / "cloudflare-workers" / site_id
        deploy_dir.mkdir(parents=True, exist_ok=True)
        config_path = deploy_dir / "wrangler.jsonc"
        config_path.write_text(json.dumps({
            "name": project,
            "compatibility_date": "2026-08-22",
            "assets": {"directory": str(OUT.resolve())},
        }, indent=2) + "\n", encoding="utf-8")
        run(["npx", "wrangler", "deploy", "--config", str(config_path), "--yes"], env=env)
        return
    if provider == "vercel":
        run(["npx", "vercel", str(OUT), "--prod", "--yes"], env=env)
        return
    if provider == "netlify":
        run(["npx", "netlify", "deploy", "--dir", str(OUT), "--prod"], env=env)
        return
    raise SystemExit(f"Unsupported provider '{provider}'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate, build, and deploy an SEO site")
    parser.add_argument("action", choices=["generate", "build", "deploy", "all"])
    parser.add_argument("site_id")
    parser.add_argument("provider", nargs="?", choices=["static", "cloudflare-pages", "cloudflare-workers", "vercel", "netlify"], default="static")
    args = parser.parse_args()
    if args.action in ("generate", "all"):
        generate(args.site_id)
    if args.action in ("build", "all"):
        build(args.site_id)
    if args.action in ("deploy", "all"):
        deploy(args.site_id, args.provider)


if __name__ == "__main__":
    main()
