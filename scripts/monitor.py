#!/usr/bin/env python3
"""Health-check every deployed site and fail CI when any site is unreachable."""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"
STATE = ROOT / ".deploy" / "monitor"


def url(config: dict) -> str:
    if config.get("domain"):
        return "https://" + config["domain"].rstrip("/")
    deploy = config.get("deploy", {})
    if deploy.get("url"):
        return str(deploy["url"]).rstrip("/")
    return f"https://{deploy.get('project', config['id'])}.pages.dev"


def check(target: str) -> dict:
    try:
        req = urllib.request.Request(target, headers={"User-Agent": "seo-site-monitor/1.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            return {"ok": 200 <= response.status < 400, "status": response.status}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main() -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    results = []
    for site_dir in sorted(SITES.iterdir()):
        path = site_dir / "site.json"
        if not path.exists():
            continue
        config = json.loads(path.read_text(encoding="utf-8"))
        if str(config.get("status", "active")).lower() in {"retired", "destroyed"}:
            continue
        target = url(config)
        result = {"site": site_dir.name, "url": target, **check(target)}
        results.append(result)
    report = {"timestamp": time.time(), "total": len(results), "failed": sum(not r["ok"] for r in results), "results": results}
    (STATE / "latest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
