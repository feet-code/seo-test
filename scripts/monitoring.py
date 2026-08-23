#!/usr/bin/env python3
"""Provision Cloudflare Pages domains, Google Search Console, and PostHog."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"
STATE = ROOT / ".deploy" / "state"


def http(method: str, url: str, body=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=60) as response:
        raw = response.read()
        return json.loads(raw) if raw else {}


def cloudflare(method: str, path: str, body=None):
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not token or not account:
        raise RuntimeError("CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID are required")
    return http(method, f"https://api.cloudflare.com/client/v4/accounts/{account}{path}", body, {
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"
    })


def provision_pages(config: dict) -> None:
    project = config["deploy"]["project"]
    try:
        cloudflare("GET", f"/pages/projects/{urllib.parse.quote(project, safe='')}")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        cloudflare("POST", "/pages/projects", {"name": project, "production_branch": "main"})

    domain = config.get("domain")
    if domain:
        try:
            cloudflare("GET", f"/pages/projects/{urllib.parse.quote(project, safe='')}/domains/{urllib.parse.quote(domain, safe='')}")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            cloudflare("POST", f"/pages/projects/{urllib.parse.quote(project, safe='')}/domains", {"name": domain})


def posthog(config: dict) -> None:
    key = os.environ.get("POSTHOG_PERSONAL_API_KEY")
    if not key:
        return
    host = os.environ.get("POSTHOG_HOST", "https://us.posthog.com").rstrip("/")
    # PostHog exposes project creation through its authenticated API. Keep the endpoint
    # configurable because self-hosted PostHog installations may use a different base.
    project_name = config.get("name", config["id"])
    try:
        result = http("POST", f"{host}/api/projects/", {"name": project_name}, {
            "Authorization": f"Bearer {key}", "Content-Type": "application/json"
        })
        project = result.get("id") or result.get("project_id")
        public_key = result.get("api_token") or result.get("api_key") or result.get("token")
        if project and public_key:
            config["monitoring"] = {"posthogProjectId": project, "posthogKey": public_key, "posthogHost": host}
    except urllib.error.HTTPError as exc:
        # A 409/400 may mean the project already exists. Existing keys can be supplied in site.json.
        if exc.code not in (400, 409):
            raise


def google_access_token() -> str:
    """Use a Google service-account JSON file with google-auth when available."""
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError as exc:
        raise RuntimeError("Install requirements.txt before using Google automation") from exc
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is required for Search Console automation")
    scopes = [
        "https://www.googleapis.com/auth/siteverification",
        "https://www.googleapis.com/auth/webmasters",
    ]
    creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
    creds.refresh(Request())
    return creds.token


def google_api(method: str, url: str, token: str, body=None):
    return http(method, url, body, {"Authorization": f"Bearer {token}", "Content-Type": "application/json"})


def verify_and_register(config: dict, site_url: str) -> None:
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return
    token = google_access_token()
    # URL-prefix verification is portable and works for pages.dev as well as custom domains.
    property_url = site_url.rstrip("/") + "/"
    token_result = google_api("POST", "https://www.googleapis.com/siteVerification/v1/token", token, {
        "site": {"identifier": property_url, "type": "SITE"},
        "verificationMethod": "META",
    })
    verification_token = token_result["token"]
    config.setdefault("monitoring", {})["googleVerificationToken"] = verification_token
    # The build embeds the token in the HTML. Rebuilding/deploying is handled by launch.py.
    config["monitoring"]["googleProperty"] = property_url
    # Verification itself happens after the new HTML is live.


def finalize_google(config: dict) -> None:
    monitoring = config.get("monitoring", {})
    property_url = monitoring.get("googleProperty")
    if not property_url or not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return
    token = google_access_token()
    encoded = urllib.parse.quote(property_url, safe="")
    try:
        google_api("PUT", f"https://www.googleapis.com/webmasters/v3/sites/{encoded}", token)
    except urllib.error.HTTPError as exc:
        if exc.code not in (200, 204):
            raise
    sitemap = property_url + "sitemap.xml"
    feed = urllib.parse.quote(sitemap, safe="")
    try:
        google_api("PUT", f"https://www.googleapis.com/webmasters/v3/sites/{encoded}/sitemaps/{feed}", token)
    except urllib.error.HTTPError as exc:
        if exc.code not in (200, 204):
            raise


def save(config: dict, path: Path) -> None:
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def provision(config: dict, site_dir: Path) -> None:
    if config.get("deploy", {}).get("provider") == "cloudflare-pages" and os.environ.get("CLOUDFLARE_API_TOKEN"):
        provision_pages(config)
    posthog(config)
    domain = config.get("domain")
    if domain:
        verify_and_register(config, f"https://{domain}")
    save(config, site_dir / "site.json")


def finalize(config: dict) -> None:
    finalize_google(config)


if __name__ == "__main__":
    raise SystemExit("Use scripts/launch.py rather than invoking monitoring.py directly")
