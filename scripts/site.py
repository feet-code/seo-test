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
    print("$", " ".join(command))
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def generate(site_id: str) -> None:
    run([sys.executable, "scripts/generate_posts.py", site_id])


def build(site_id: str) -> None:
    _, site_dir = site_config(site_id)
    env = os.environ.copy()
    env["SEO_POSTS_DIR"] = str((site_dir / "_posts").resolve())
    if OUT.exists():
        shutil.rmtree(OUT)
    run(["npm", "run", "build"], env=env)
    if not OUT.exists():
        raise SystemExit("Next.js build completed but out/ was not produced.")


def deploy(site_id: str, provider: str) -> None:
    config, _ = site_config(site_id)
    project = config.get("deploy", {}).get("project", config.get("id", site_id))
    if not OUT.exists():
        raise SystemExit("out/ does not exist. Run the build command first.")

    if provider == "static":
        print(f"Static artifact ready at {OUT}")
        return

    if provider == "cloudflare-pages":
        run(["npx", "wrangler", "pages", "deploy", str(OUT), "--project-name", project])
        return

    if provider == "cloudflare-workers":
        # Wrangler resolves assets.directory relative to the generated config file.
        deploy_dir = DEPLOY / "cloudflare-workers" / site_id
        deploy_dir.mkdir(parents=True, exist_ok=True)
        config_path = deploy_dir / "wrangler.jsonc"
        config_path.write_text(
            json.dumps(
                {
                    "name": project,
                    "compatibility_date": "2026-08-22",
                    "assets": {"directory": "../../../out"},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        run(["npx", "wrangler", "deploy", "--config", str(config_path)])
        return

    if provider == "vercel":
        run(["npx", "vercel", str(OUT), "--prod"])
        return

    if provider == "netlify":
        run(["npx", "netlify", "deploy", "--dir", str(OUT), "--prod"])
        return

    raise SystemExit(
        f"Unsupported provider '{provider}'. Choose: static, cloudflare-pages, "
        "cloudflare-workers, vercel, netlify."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate, build, and deploy an SEO site")
    parser.add_argument("action", choices=["generate", "build", "deploy", "all"])
    parser.add_argument("site_id")
    parser.add_argument(
        "provider",
        nargs="?",
        choices=["static", "cloudflare-pages", "cloudflare-workers", "vercel", "netlify"],
        default="static",
    )
    args = parser.parse_args()

    if args.action in ("generate", "all"):
        generate(args.site_id)
    if args.action in ("build", "all"):
        build(args.site_id)
    if args.action in ("deploy", "all"):
        deploy(args.site_id, args.provider)


if __name__ == "__main__":
    main()
