#!/usr/bin/env python3
"""Inspect, pause, reactivate, or safely tear down portfolio sites."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def configured_sites() -> dict[str, tuple[Path, dict[str, Any]]]:
    result: dict[str, tuple[Path, dict[str, Any]]] = {}
    for site_dir in sorted(SITES.iterdir()):
        path = site_dir / "site.json"
        if path.exists():
            result[site_dir.name] = (
                path,
                json.loads(path.read_text(encoding="utf-8")),
            )
    return result


def save(path: Path, config: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def target_url(config: dict[str, Any]) -> str:
    if config.get("domain"):
        return "https://" + str(config["domain"]).rstrip("/")
    project = config.get("deploy", {}).get("project", config.get("id"))
    return f"https://{project}.pages.dev"


def status_rows() -> list[dict[str, Any]]:
    rows = []
    for site_id, (path, config) in configured_sites().items():
        rows.append(
            {
                "site": site_id,
                "status": config.get("status", "active"),
                "products": len(config.get("products") or [config.get("product")]),
                "provider": config.get("deploy", {}).get("provider", "cloudflare-pages"),
                "url": target_url(config),
                "posts": len(list((path.parent / "_posts").glob("*.md"))),
            }
        )
    return rows


def show_status(as_json: bool) -> None:
    rows = status_rows()
    if as_json:
        print(json.dumps(rows, indent=2))
        return
    print("STATUS\tPRODUCTS\tPOSTS\tSITE\tURL")
    for row in rows:
        print(
            f"{row['status']}\t{row['products']}\t{row['posts']}\t"
            f"{row['site']}\t{row['url']}"
        )


def set_status(site_id: str, status: str) -> None:
    sites = configured_sites()
    if site_id not in sites:
        raise SystemExit(f"Unknown site: {site_id}")
    path, config = sites[site_id]
    previous = str(config.get("status", "active"))
    config["status"] = status
    lifecycle = config.setdefault("lifecycle", {})
    lifecycle["updatedAt"] = now()
    if status == "retired":
        lifecycle["retiredAt"] = lifecycle["updatedAt"]
    elif status == "active":
        lifecycle["activatedAt"] = lifecycle["updatedAt"]
    save(path, config)
    print(f"{site_id}: {previous} -> {status}")
    if status == "retired":
        print("The deployed site is still live; retire only excludes it from deploys and health checks.")
    elif previous == "destroyed":
        print("Run launch.py for this site to recreate hosting and Google resources.")


def teardown_targets(site_id: str | None, all_sites: bool) -> list[tuple[str, Path, dict[str, Any]]]:
    sites = configured_sites()
    if all_sites:
        selected = [
            (name, path, config)
            for name, (path, config) in sites.items()
            if str(config.get("status", "active")).lower() != "destroyed"
        ]
    else:
        if not site_id:
            raise SystemExit("Pass SITE_ID or --all")
        if site_id not in sites:
            raise SystemExit(f"Unknown site: {site_id}")
        path, config = sites[site_id]
        selected = [(site_id, path, config)]
    if not selected:
        raise SystemExit("No non-destroyed sites selected.")
    return selected


def teardown(site_id: str | None, all_sites: bool, confirmation: str | None) -> None:
    selected = teardown_targets(site_id, all_sites)
    required = "DESTROY-ALL" if all_sites else selected[0][0]

    print("TEARDOWN PLAN (local configs and source content are preserved)")
    for name, _, config in selected:
        project = config.get("deploy", {}).get("project", name)
        google = config.get("monitoring", {}).get("googleProperty", "<not configured>")
        print(
            f"- {name}: delete Cloudflare Pages project {project!r}; "
            f"remove GSC/Site Verification property {google!r}"
        )

    if confirmation != required:
        target = "--all" if all_sites else selected[0][0]
        print(
            "\nPreview only. To execute exactly this teardown, run:\n"
            f"python scripts/portfolio.py teardown {target} --confirm {required}"
        )
        return

    from monitoring import teardown as remove_external_resources

    failures = []
    for name, path, config in selected:
        try:
            remove_external_resources(config)
            config["status"] = "destroyed"
            lifecycle = config.setdefault("lifecycle", {})
            lifecycle["destroyedAt"] = now()
            lifecycle["updatedAt"] = lifecycle["destroyedAt"]
            save(path, config)
            print(f"{name}: destroyed externally; local config/content preserved")
        except Exception as exc:
            failures.append((name, repr(exc)))
            print(f"{name}: teardown failed: {exc!r}")
    if failures:
        raise SystemExit(
            "Teardown incomplete: "
            + "; ".join(f"{name}={error}" for name, error in failures)
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    status = commands.add_parser("status", help="List sites and lifecycle state")
    status.add_argument("--json", action="store_true")

    for command in ("retire", "activate"):
        subparser = commands.add_parser(command)
        subparser.add_argument("site_id")

    destroy = commands.add_parser(
        "teardown",
        help="Preview or delete hosting plus Google property/ownership resources",
    )
    destroy.add_argument("site_id", nargs="?")
    destroy.add_argument("--all", action="store_true")
    destroy.add_argument("--confirm")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "status":
        show_status(args.json)
    elif args.command == "retire":
        set_status(args.site_id, "retired")
    elif args.command == "activate":
        set_status(args.site_id, "active")
    elif args.command == "teardown":
        if args.site_id and args.all:
            raise SystemExit("Choose SITE_ID or --all, not both")
        teardown(args.site_id, args.all, args.confirm)


if __name__ == "__main__":
    main()
