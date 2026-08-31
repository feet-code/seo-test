#!/usr/bin/env python3
"""Deploy the private GSC dashboard and transfer OAuth values as Worker secrets."""
from __future__ import annotations

import getpass
import json
import os
import secrets
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "dashboard" / "wrangler.jsonc"


def executable(name: str) -> str:
    return f"{name}.cmd" if os.name == "nt" else name


def run(command: list[str], *, secret_input: str | None = None) -> None:
    print("$", " ".join(command))
    subprocess.run(
        command,
        cwd=ROOT,
        input=None if secret_input is None else secret_input + "\n",
        text=True,
        check=True,
    )


def oauth_token_path() -> Path:
    configured = os.environ.get("GOOGLE_OAUTH_TOKEN_FILE", "").strip()
    path = Path(configured) if configured else ROOT / ".deploy" / "state" / "google-oauth-token.json"
    return path if path.is_absolute() else ROOT / path


def main() -> None:
    token_path = oauth_token_path()
    if not token_path.exists():
        raise SystemExit(
            f"Google OAuth token not found at {token_path}. Run one normal launch first or set "
            "GOOGLE_OAUTH_TOKEN_FILE to the cached user OAuth token."
        )
    token = json.loads(token_path.read_text(encoding="utf-8"))
    required = {
        "GOOGLE_CLIENT_ID": token.get("client_id"),
        "GOOGLE_CLIENT_SECRET": token.get("client_secret"),
        "GOOGLE_REFRESH_TOKEN": token.get("refresh_token"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise SystemExit(f"OAuth token file is missing: {', '.join(missing)}")

    password = getpass.getpass("Choose a private dashboard password (12+ characters): ")
    if len(password) < 12:
        raise SystemExit("Dashboard password must be at least 12 characters.")
    if password != getpass.getpass("Confirm dashboard password: "):
        raise SystemExit("Passwords did not match.")
    required["DASHBOARD_PASSWORD"] = password
    required["SESSION_SECRET"] = secrets.token_urlsafe(48)

    npx = executable("npx")
    config = str(CONFIG)
    print("Deploying the Worker shell before attaching encrypted secrets…")
    run([npx, "wrangler", "deploy", "--config", config])
    for name, value in required.items():
        print(f"Uploading encrypted Worker secret: {name}")
        run(
            [npx, "wrangler", "secret", "put", name, "--config", config],
            secret_input=str(value),
        )
    print("\nDashboard deployed. Open the workers.dev URL printed above and sign in.")


if __name__ == "__main__":
    main()
