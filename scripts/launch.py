#!/usr/bin/env python3
"""Generate, deploy, register, and monitor an SEO product portfolio."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"
STATE = ROOT / ".deploy" / "state"
LOGS = ROOT / ".deploy" / "logs"
CHECKPOINT = STATE / "checkpoint.json"
INACTIVE_STATUSES = {"retired", "destroyed"}


def run(
    args: list[str | Path],
    env: dict[str, str] | None = None,
    *,
    site_id: str | None = None,
    step: str | None = None,
) -> subprocess.CompletedProcess:
    command_args = [str(value) for value in args]
    if os.name == "nt" and command_args and command_args[0].lower() == "npm":
        command_args[0] = "npm.cmd"

    label = f"{site_id}/{step}" if site_id and step else (step or "command")
    log_path = LOGS / (site_id or "global") / (f"{step}.log" if step else "command.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    child_env = (env or os.environ.copy()).copy()
    path = child_env.get("PATH", "")
    resolved = shutil.which(command_args[0], path=path)
    command = " ".join(command_args)

    print("\n" + "=" * 72, flush=True)
    print(f"STEP: {label}", flush=True)
    print(f"COMMAND: {command}", flush=True)
    print(f"CWD: {ROOT}", flush=True)
    print(f"EXECUTABLE: {resolved or '<not found>'}", flush=True)
    print(f"PYTHON: {sys.executable}", flush=True)
    print(f"LOG: {log_path.relative_to(ROOT)}", flush=True)
    print("=" * 72, flush=True)

    started = time.time()
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        log.write(
            f"COMMAND: {command}\nCWD: {ROOT}\nEXECUTABLE: {resolved or '<not found>'}\n"
            f"PYTHON: {sys.executable}\nSTARTED: {time.ctime()}\n\n"
        )
        try:
            process = subprocess.Popen(
                command_args,
                cwd=ROOT,
                env=child_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except (FileNotFoundError, OSError) as exc:
            detail = (
                f"Could not start process. executable={command_args[0]!r}; resolved={resolved!r}; "
                f"cwd={str(ROOT)!r}; error={exc!r}"
            )
            log.write(detail + "\n")
            print(f"\n✗ PROCESS START FAILED\n{detail}", file=sys.stderr, flush=True)
            print(f"  Check log: {log_path.relative_to(ROOT)}", file=sys.stderr, flush=True)
            raise RuntimeError(detail) from exc

        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
            log.flush()
        code = process.wait()
        duration = round(time.time() - started, 2)
        log.write(f"\nEXIT CODE: {code}\nDURATION: {duration}s\n")

    print(f"\nEXIT CODE: {code} | DURATION: {duration}s", flush=True)
    if code:
        print(f"\n✗ {label.upper()} FAILED", file=sys.stderr, flush=True)
        print(f"  Full log: {log_path.relative_to(ROOT)}", file=sys.stderr, flush=True)
        raise subprocess.CalledProcessError(code, command_args)
    print(f"✓ {label.upper()} COMPLETED", flush=True)
    return subprocess.CompletedProcess(command_args, code)


def load_config(site_dir: Path) -> dict[str, Any]:
    return json.loads((site_dir / "site.json").read_text(encoding="utf-8"))


def site_url(config: dict[str, Any]) -> str:
    if config.get("domain"):
        return "https://" + str(config["domain"]).rstrip("/")
    deploy = config.get("deploy", {})
    if deploy.get("url"):
        return str(deploy["url"]).rstrip("/")
    project = deploy.get("project", config["id"])
    provider = deploy.get("resolvedProvider") or deploy.get("provider", "cloudflare-pages")
    if provider == "cloudflare-workers":
        raise RuntimeError(
            f"Worker URL for {project!r} is not resolved. Run with Cloudflare credentials "
            "or set deploy.url in the site config."
        )
    return f"https://{project}.pages.dev"


def concrete_provider(config: dict[str, Any]) -> str:
    deploy = config.get("deploy", {})
    provider = str(deploy.get("resolvedProvider") or deploy.get("provider", "cloudflare-pages"))
    return "cloudflare-pages" if provider in {"auto", "cloudflare-auto"} else provider


def health(url: str) -> dict[str, Any]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "seo-site-monitor/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            return {"ok": 200 <= response.status < 400, "status": response.status, "url": url}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def save_checkpoint(
    site_ids: list[str],
    next_index: int,
    reason: str | None = None,
    step: str | None = None,
) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    document: dict[str, Any] = {
        "siteIds": site_ids,
        "nextIndex": next_index,
        "nextSite": site_ids[next_index] if next_index < len(site_ids) else None,
        "updatedAt": time.time(),
    }
    if reason:
        document["reason"] = reason
    if step:
        document["step"] = step
    CHECKPOINT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def _configured_sites() -> dict[str, tuple[Path, dict[str, Any]]]:
    configured: dict[str, tuple[Path, dict[str, Any]]] = {}
    for site_dir in sorted(SITES.iterdir()):
        if (site_dir / "site.json").exists():
            configured[site_dir.name] = (site_dir, load_config(site_dir))
    return configured


def _requested_site_ids(args: argparse.Namespace) -> set[str]:
    requested = set(args.site or [])
    if args.sites:
        requested.update(value.strip() for value in args.sites.split(",") if value.strip())
    return requested


def _requested_batches(args: argparse.Namespace) -> set[str]:
    requested = set(args.batch or [])
    if args.batches:
        requested.update(value.strip() for value in args.batches.split(",") if value.strip())
    return requested


def _has_explicit_selection(args: argparse.Namespace) -> bool:
    return bool(
        args.site
        or args.sites
        or args.product
        or args.batch
        or args.batches
        or args.limit
    )


def _resume_start_index(checkpoint: dict[str, Any], site_ids: list[str]) -> int:
    """Translate checkpoint progress after removed sites have been pruned."""
    checkpoint_ids = [str(value) for value in checkpoint.get("siteIds", [])]
    old_next_index = min(
        max(int(checkpoint.get("nextIndex", 0)), 0),
        len(checkpoint_ids),
    )
    completed = set(checkpoint_ids[:old_next_index])
    return sum(1 for site_id in site_ids if site_id in completed)


def selected_sites(args: argparse.Namespace) -> list[Path]:
    configured = _configured_sites()
    requested = _requested_site_ids(args)
    resume_order: list[str] | None = None
    if args.resume and CHECKPOINT.exists() and not _has_explicit_selection(args):
        checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        checkpoint_ids = [str(value) for value in checkpoint.get("siteIds", [])]
        missing_checkpoint_ids = [
            site_id for site_id in checkpoint_ids if site_id not in configured
        ]
        if missing_checkpoint_ids:
            print(
                "Skipping checkpoint site(s) no longer configured: "
                + ", ".join(missing_checkpoint_ids),
                flush=True,
            )
        resume_order = [site_id for site_id in checkpoint_ids if site_id in configured]
        requested.update(resume_order)
        if requested:
            print(
                f"Restored {len(requested)} deployable sites from the saved launch checkpoint.",
                flush=True,
            )
    missing = requested - configured.keys()
    if missing:
        raise SystemExit(f"Unknown site(s): {', '.join(sorted(missing))}")

    product_sites: dict[str, str] = {}
    for product_id in args.product or []:
        matches = []
        for site_id, (_, config) in configured.items():
            if any(
                str(product.get("id")) == product_id
                for product in (config.get("products") or [])
            ):
                matches.append(site_id)
        if not matches:
            raise SystemExit(f"Unknown product: {product_id}")
        if len(matches) > 1:
            raise SystemExit(
                f"Product {product_id!r} appears in multiple sites: {', '.join(sorted(matches))}"
            )
        product_sites[product_id] = matches[0]

    if product_sites:
        resolved = set(product_sites.values())
        if requested and not resolved.issubset(requested):
            outside = resolved - requested
            raise SystemExit(
                "Requested product(s) are outside the selected site(s): "
                + ", ".join(sorted(outside))
            )
        requested = requested or resolved

    requested_batches = _requested_batches(args)
    available_batches = {
        str(product.get("contentBatch"))
        for _, config in configured.values()
        for product in (config.get("products") or [])
        if str(product.get("contentBatch", "")).strip()
    }
    unknown_batches = requested_batches - available_batches
    if unknown_batches:
        available = ", ".join(sorted(available_batches)) or "none"
        raise SystemExit(
            f"Unknown content batch(es): {', '.join(sorted(unknown_batches))}. "
            f"Available batches: {available}"
        )
    if requested_batches:
        batch_sites = {
            site_id
            for site_id, (_, config) in configured.items()
            if any(
                str(product.get("contentBatch")) in requested_batches
                for product in (config.get("products") or [])
            )
        }
        if requested:
            outside = requested - batch_sites
            if outside:
                raise SystemExit(
                    "Selected site/product filters do not belong to the requested batch(es): "
                    + ", ".join(sorted(outside))
                )
            requested &= batch_sites
        else:
            requested = batch_sites

    active = {
        site_id: value
        for site_id, value in configured.items()
        if str(value[1].get("status", "active")).lower() not in INACTIVE_STATUSES
    }
    inactive_requested = requested - active.keys()
    if inactive_requested and resume_order is not None:
        print(
            "Skipping inactive checkpoint site(s): "
            + ", ".join(sorted(inactive_requested)),
            flush=True,
        )
        requested -= inactive_requested
        resume_order = [site_id for site_id in resume_order if site_id in active]
    elif inactive_requested:
        raise SystemExit(
            "Inactive site(s) cannot deploy: "
            + ", ".join(sorted(inactive_requested))
            + ". Run scripts/portfolio.py activate SITE_ID first."
        )

    selected = (
        [active[site_id][0] for site_id in resume_order]
        if resume_order is not None
        else [
            value[0]
            for site_id, value in active.items()
            if not requested or site_id in requested
        ]
    )
    return selected[: args.limit] if args.limit else selected


def product_args_for_site(args: argparse.Namespace, config: dict[str, Any]) -> list[str]:
    requested = set(args.product or [])
    site_products = {str(product.get("id")) for product in config.get("products") or []}
    return [product_id for product_id in args.product or [] if product_id in requested & site_products]


def build_environment(
    base: dict[str, str],
    config: dict[str, Any],
    site_dir: Path,
    target: str,
    *,
    mock: bool,
) -> dict[str, str]:
    environment = base.copy()
    monitoring = config.get("monitoring", {})
    signup = config.get("signup", {})
    products = config.get("products") or [
        {
            "id": config.get("id", site_dir.name),
            "name": config.get("name", site_dir.name),
            "product": config.get("product", ""),
            "audience": config.get("audience", ""),
            "problem": config.get("valueProposition", ""),
            "valueProposition": config.get("valueProposition", ""),
            "topic": config.get("topic", ""),
        }
    ]
    environment.update(
        {
            "SITE_URL": target,
            "SEO_POSTS_DIR": str((site_dir / "_posts").resolve()),
            "GOOGLE_SITE_VERIFICATION": ""
            if mock
            else str(monitoring.get("googleVerificationToken", "")),
            "NEXT_PUBLIC_POSTHOG_KEY": ""
            if mock
            else str(monitoring.get("posthogKey", "")),
            "NEXT_PUBLIC_POSTHOG_HOST": str(
                monitoring.get("posthogHost", "https://us.i.posthog.com")
            ),
            "SIGNUP_ENDPOINT": str(signup.get("endpoint", "")),
            "SIGNUP_EMAIL": str(signup.get("email", "")),
            "SIGNUP_HEADLINE": str(
                signup.get("headline", "Interested? Get notified when this is available.")
            ),
            "SITE_PRODUCT_NAME": str(config.get("name", site_dir.name)),
            "SITE_NAME": str(config.get("name", site_dir.name)),
            "SITE_AUDIENCE": str(config.get("audience", "")),
            "SITE_DESCRIPTION": str(
                config.get("valueProposition", config.get("topic", ""))
            ),
            "SITE_TOPIC": str(config.get("topic", "")),
            "SITE_PRODUCTS_JSON": json.dumps(products, ensure_ascii=False),
        }
    )
    return environment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate, deploy, register, and monitor the SEO site portfolio"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--frontend-only", action="store_true", help="Build/deploy existing content")
    mode.add_argument("--blogs-only", action="store_true", help="Regenerate selected blog probes")
    parser.add_argument("--site", action="append", help="Site ID; repeat for multiple sites")
    parser.add_argument("--sites", help="Comma-separated site IDs")
    parser.add_argument(
        "--batch",
        action="append",
        help="Deploy sites containing this ideas.json contentBatch; repeat as needed",
    )
    parser.add_argument("--batches", help="Comma-separated contentBatch values")
    parser.add_argument(
        "--product",
        action="append",
        help="Regenerate/deploy the site containing this product ID; repeat as needed",
    )
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--skip-generation", action="store_true")
    parser.add_argument(
        "--provider",
        choices=[
            "auto",
            "cloudflare-auto",
            "cloudflare-pages",
            "cloudflare-workers",
            "vercel",
            "netlify",
            "static",
        ],
        help="Override each site's configured provider; auto fills Pages first, then Workers",
    )
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be zero or positive")
    if args.product and args.limit:
        parser.error("--product resolves exact sites and cannot be combined with --limit")
    if args.product and (args.frontend_only or args.skip_generation):
        parser.error("--product requests content generation; remove --frontend-only/--skip-generation")
    return args


def main() -> None:
    args = parse_args()
    environment = os.environ.copy()
    if args.mock:
        environment["MOCK_LLM"] = "1"

    STATE.mkdir(parents=True, exist_ok=True)
    marker = STATE / "gemini_exhausted.json"
    if marker.exists() and not args.resume:
        marker.unlink()

    ideas_command = [sys.executable, "scripts/ideas.py"]
    if args.mock:
        ideas_command.append("--mock")
    run(ideas_command, env=environment, step="ideas")
    sites = selected_sites(args)
    site_ids = [path.name for path in sites]
    start = 0
    if args.resume and CHECKPOINT.exists():
        checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        if not _has_explicit_selection(args):
            start = _resume_start_index(checkpoint, site_ids)
            next_site = site_ids[start] if start < len(site_ids) else "complete"
            print(f"Resuming at {start + 1}/{len(site_ids)}: {next_site}")
        elif checkpoint.get("siteIds") == site_ids:
            start = min(int(checkpoint.get("nextIndex", 0)), len(site_ids))
            next_site = site_ids[start] if start < len(site_ids) else "complete"
            print(f"Resuming at {start + 1}/{len(site_ids)}: {next_site}")
        else:
            print("Checkpoint site set differs from the current subset; starting at the beginning.")
    if not site_ids:
        raise SystemExit(
            "No active sites selected. Add/sync sites, adjust the selection, or activate a retired site."
        )

    print(
        f"Processing {len(site_ids) - start} sites "
        f"(selected {len(site_ids)}, starting index {start + 1})",
        flush=True,
    )
    shared_posthog: dict[str, Any] = {}
    if not args.mock:
        try:
            from monitoring import provision_shared_posthog

            shared_posthog = provision_shared_posthog()
        except Exception as exc:
            print(f"PostHog provisioning skipped: {exc}")

    results = []
    force_generation = args.blogs_only or bool(args.product)
    skip_generation = args.frontend_only or args.skip_generation
    for index in range(start, len(sites)):
        site_dir = sites[index]
        site_id = site_dir.name
        save_checkpoint(site_ids, index, step="start")
        started = time.time()
        result: dict[str, Any] = {"site": site_id, "startedAt": started}
        print(
            f"\n{'#' * 72}\nSITE {index + 1}/{len(site_ids)}: {site_id}\n{'#' * 72}",
            flush=True,
        )
        try:
            config = load_config(site_dir)
            save_checkpoint(site_ids, index, step="hosting")
            if args.mock:
                requested_provider = args.provider or str(
                    config.get("deploy", {}).get("provider", "cloudflare-pages")
                )
                config.setdefault("deploy", {})["resolvedProvider"] = (
                    "cloudflare-pages"
                    if requested_provider in {"auto", "cloudflare-auto"}
                    else requested_provider
                )
            else:
                from monitoring import prepare_hosting

                config = prepare_hosting(config, site_dir, args.provider)
            provider = concrete_provider(config)
            target = site_url(config)
            if not args.mock:
                from monitoring import provision

                config = provision(config, site_dir, target, shared_posthog)

            if not skip_generation:
                save_checkpoint(site_ids, index, step="generate")
                command = [sys.executable, "scripts/generate_posts.py", site_id]
                if args.mock:
                    command.append("--mock")
                if force_generation:
                    command.append("--force")
                for product_id in product_args_for_site(args, config):
                    command.extend(["--product", product_id])
                run(command, env=environment, site_id=site_id, step="generate")
            else:
                print(
                    f"{site_id}: content generation skipped by --frontend-only/--skip-generation.",
                    flush=True,
                )

            build_env = build_environment(environment, config, site_dir, target, mock=args.mock)
            save_checkpoint(site_ids, index, step="build")
            run(["npm", "run", "build"], env=build_env, site_id=site_id, step="build")
            if provider != "static":
                save_checkpoint(site_ids, index, step="deploy")
                run(
                    [sys.executable, "scripts/site.py", "deploy", site_id, provider],
                    env=build_env,
                    site_id=site_id,
                    step="deploy",
                )
            if not args.mock:
                save_checkpoint(site_ids, index, step="gsc")
                from monitoring import finalize

                finalize(config)
            result.update({"ok": True, "url": target, "health": health(target)})
        except subprocess.CalledProcessError as exc:
            exhausted = marker.exists()
            result.update({"ok": False, "error": f"Command failed with exit code {exc.returncode}"})
            step = (
                json.loads(CHECKPOINT.read_text(encoding="utf-8")).get("step")
                if CHECKPOINT.exists()
                else "unknown"
            )
            reason = (
                "Gemini fallback chain exhausted; resume when credits/rate limits recover."
                if exhausted
                else "Command failed; fix the error and resume."
            )
            save_checkpoint(site_ids, index, reason, step)
            (STATE / f"{site_id}.json").write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            print(
                f"\n✗ STOPPED at site {index + 1}/{len(site_ids)}: {site_id}\n"
                f"  Failed step: {step}\n  Checkpoint: .deploy/state/checkpoint.json\n"
                "  Fix the failure and run: python scripts/launch.py --resume",
                file=sys.stderr,
                flush=True,
            )
            raise SystemExit(2 if exhausted else 1)
        except Exception as exc:
            step = (
                json.loads(CHECKPOINT.read_text(encoding="utf-8")).get("step")
                if CHECKPOINT.exists()
                else "python"
            )
            result.update({"ok": False, "error": repr(exc)})
            save_checkpoint(site_ids, index, "Unexpected error; fix the error and resume.", step)
            (STATE / f"{site_id}.json").write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            print(
                f"\n✗ UNEXPECTED FAILURE at site {index + 1}/{len(site_ids)}: {site_id}\n"
                f"  Failed step: {step}\n  {exc!r}\n"
                "  Checkpoint saved. Run: python scripts/launch.py --resume",
                file=sys.stderr,
                flush=True,
            )
            raise SystemExit(1)

        result["durationSeconds"] = round(time.time() - started, 2)
        (STATE / f"{site_id}.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        save_checkpoint(site_ids, index + 1, step="complete")
        print(f"[{index + 1}/{len(site_ids)}] {site_id}: OK ({result['durationSeconds']}s)")
        results.append(result)

    summary = {
        "timestamp": time.time(),
        "total": len(results),
        "successful": sum(result["ok"] for result in results),
        "failed": sum(not result["ok"] for result in results),
        "results": results,
    }
    (STATE / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "\nFINAL SUMMARY\n"
        + json.dumps(
            {key: summary[key] for key in ("total", "successful", "failed")},
            indent=2,
        )
    )
    if summary["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
