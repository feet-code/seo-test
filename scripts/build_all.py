#!/usr/bin/env python3
"""Build every configured site serially so generated output never collides."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"


def main() -> None:
    sites = []
    for path in sorted(SITES.iterdir()):
        config_path = path / "site.json"
        if not config_path.exists():
            continue
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if str(config.get("status", "active")).lower() not in {"retired", "destroyed"}:
            sites.append(path.name)
    if not sites:
        raise SystemExit("No configured sites found in sites/")
    for site_id in sites:
        subprocess.run([sys.executable, "scripts/site.py", "build", site_id], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
