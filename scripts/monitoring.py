#!/usr/bin/env python3
"""Provision hosting, shared PostHog analytics, and Google Search Console."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


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
    encoded_project = urllib.parse.quote(project, safe="")
    try:
        cloudflare("GET", f"/pages/projects/{encoded_project}")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        cloudflare("POST", "/pages/projects", {"name": project, "production_branch": "main"})
    domain = config.get("domain")
    if domain:
        encoded_domain = urllib.parse.quote(domain, safe="")
        try:
            cloudflare("GET", f"/pages/projects/{encoded_project}/domains/{encoded_domain}")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            cloudflare("POST", f"/pages/projects/{encoded_project}/domains", {"name": domain})


def provision_shared_posthog() -> dict:
    """Create/reuse exactly one PostHog project for the entire portfolio."""
    key = os.environ.get("POSTHOG_PERSONAL_API_KEY")
    organization = os.environ.get("POSTHOG_ORGANIZATION_ID")
    if not key or not organization:
        return {}

    host = os.environ.get("POSTHOG_HOST", "https://us.posthog.com").rstrip("/")
    state_path = Path(os.environ.get("POSTHOG_STATE_FILE", ".deploy/posthog.json"))
    state_path.parent.mkdir(parents=True, exist_ok=True)
    if state_path.exists():
        try:
            saved = json.loads(state_path.read_text(encoding="utf-8"))
            if saved.get("posthogProjectId") and saved.get("posthogKey"):
                return saved
        except json.JSONDecodeError:
            pass

    base = f"{host}/api/organizations/{urllib.parse.quote(organization, safe='')}/projects/"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    project_name = os.environ.get("POSTHOG_PROJECT_NAME", "SEO Site Portfolio")
    listing = http("GET", base + "?search=" + urllib.parse.quote(project_name), headers=headers)
    matches = listing.get("results", [])
    project = next((p for p in matches if p.get("name") == project_name), None)
    if project is None:
        project = http("POST", base, {"name": project_name}, headers)

    result = {
        "posthogProjectId": project.get("id"),
        "posthogKey": project.get("api_token"),
        "posthogHost": os.environ.get("POSTHOG_INGEST_HOST", "https://us.i.posthog.com"),
        "posthogProjectName": project_name,
    }
    if not result["posthogProjectId"] or not result["posthogKey"]:
        raise RuntimeError("PostHog project was found/created but no public API key was returned")
    state_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def apply_shared_posthog(config: dict, shared: dict) -> None:
    if shared:
        config.setdefault("monitoring", {}).update(shared)


def google_access_token() -> str:
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError as exc:
        raise RuntimeError("Install requirements.txt before using Google automation") from exc
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is required for Search Console automation")
    scopes = ["https://www.googleapis.com/auth/siteverification", "https://www.googleapis.com/auth/webmasters"]
    creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
    creds.refresh(Request())
    return creds.token


def google_api(method: str, url: str, token: str, body=None):
    return http(method, url, body, {"Authorization": f"Bearer {token}", "Content-Type": "application/json"})


def verify_and_register(config: dict, site_url: str) -> None:
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return
    token = google_access_token()
    property_url = site_url.rstrip("/") + "/"
    token_result = google_api("POST", "https://www.googleapis.com/siteVerification/v1/token", token, {
        "site": {"identifier": property_url, "type": "SITE"}, "verificationMethod": "META"
    })
    config.setdefault("monitoring", {})["googleVerificationToken"] = token_result["token"]
    config["monitoring"]["googleProperty"] = property_url


def finalize_google(config: dict) -> None:
    monitoring = config.get("monitoring", {})
    property_url = monitoring.get("googleProperty")
    if not property_url or not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return
    token = google_access_token()
    google_api("POST", "https://www.googleapis.com/siteVerification/v1/webResource?verificationMethod=META", token, {
        "site": {"identifier": property_url, "type": "SITE"}
    })
    encoded = urllib.parse.quote(property_url, safe="")
    google_api("PUT", f"https://www.googleapis.com/webmasters/v3/sites/{encoded}", token)
    sitemap = property_url + "sitemap.xml"
    feed = urllib.parse.quote(sitemap, safe="")
    google_api("PUT", f"https://www.googleapis.com/webmasters/v3/sites/{encoded}/sitemaps/{feed}", token)


def save(config: dict, path: Path) -> None:
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def provision(config: dict, site_dir: Path, site_url: str, shared_posthog: dict | None = None) -> dict:
    if config.get("deploy", {}).get("provider") == "cloudflare-pages" and os.environ.get("CLOUDFLARE_API_TOKEN"):
        provision_pages(config)
    apply_shared_posthog(config, shared_posthog or {})
    verify_and_register(config, site_url)
    save(config, site_dir / "site.json")
    return config


def finalize(config: dict) -> None:
    try:
        finalize_google(config)
    except urllib.error.HTTPError as exc:
        print(f"Search Console verification/submission pending: HTTP {exc.code}")
