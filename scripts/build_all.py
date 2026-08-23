#!/usr/bin/env python3
"""Build every configured site serially so generated output never collides."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"


def main() -> None:
    sites = sorted(p.name for p in SITES.iterdir() if (p / "site.json").exists())
    if not sites:
        raise SystemExit("No configured sites found in sites/")
    for site_id in sites:
        subprocess.run([sys.executable, "scripts/site.py", "build", site_id], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
