#!/usr/bin/env python3
"""Provision hosting, shared PostHog analytics, and Google Search Console."""
from __future__ import annotations

import html
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/siteverification",
    "https://www.googleapis.com/auth/webmasters",
]


def _safe_headers(headers: dict | None) -> dict:
    return {
        key: ("<redacted>" if key.lower() == "authorization" else value)
        for key, value in (headers or {}).items()
    }


def http(method: str, url: str, body=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    print("HTTP request:", method, url, "body=", body, "headers=", _safe_headers(headers))
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        detail = raw.decode("utf-8", errors="replace") if raw else "<empty response>"
        print(f"HTTP error: {exc.code} {method} {url}\nResponse: {detail}")
        raise
    result = json.loads(raw) if raw else {}
    print("HTTP response:", result)
    return result


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
    """Use one explicitly configured existing PostHog project for every site."""
    project_id = os.environ.get("POSTHOG_PROJECT_ID")
    project_key = os.environ.get("POSTHOG_PROJECT_API_KEY") or os.environ.get("POSTHOG_API_KEY")
    if not project_id or not project_key:
        return {}

    return {
        "posthogProjectId": project_id,
        "posthogKey": project_key,
        "posthogHost": os.environ.get("POSTHOG_INGEST_HOST", "https://us.i.posthog.com"),
        "posthogProjectName": os.environ.get("POSTHOG_PROJECT_NAME", "Shared PostHog Project"),
    }


def apply_shared_posthog(config: dict, shared: dict) -> None:
    if shared:
        config.setdefault("monitoring", {}).update(shared)


def google_configured() -> bool:
    return bool(
        os.environ.get("GOOGLE_OAUTH_CLIENT_SECRETS")
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )


def _oauth_token_path() -> Path:
    configured = os.environ.get("GOOGLE_OAUTH_TOKEN_FILE")
    path = Path(configured) if configured else ROOT / ".deploy" / "state" / "google-oauth-token.json"
    return path if path.is_absolute() else ROOT / path


def google_credentials():
    try:
        from google.auth.transport.requests import Request
    except ImportError as exc:
        raise RuntimeError("Install requirements.txt before using Google automation") from exc

    oauth_client = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRETS")
    if oauth_client:
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError as exc:
            raise RuntimeError("Run: pip install -r requirements.txt") from exc

        token_path = _oauth_token_path()
        credentials = None
        if token_path.exists():
            credentials = Credentials.from_authorized_user_file(str(token_path), GOOGLE_SCOPES)
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        if not credentials or not credentials.valid:
            print("Opening Google authorization in your browser. Choose the account you use in Search Console.")
            flow = InstalledAppFlow.from_client_secrets_file(oauth_client, GOOGLE_SCOPES)
            credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(credentials.to_json(), encoding="utf-8")
        print(f"Google authentication: user OAuth (cached at {token_path})")
        return credentials

    try:
        from google.oauth2 import service_account
    except ImportError as exc:
        raise RuntimeError("Install requirements.txt before using Google automation") from exc
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise RuntimeError(
            "Set GOOGLE_OAUTH_CLIENT_SECRETS for properties visible in your GSC account, "
            "or GOOGLE_APPLICATION_CREDENTIALS for service-account-only access."
        )
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=GOOGLE_SCOPES
    )
    credentials.refresh(Request())
    print(f"Google authentication: service account {credentials.service_account_email}")
    return credentials


def google_access_token() -> str:
    return google_credentials().token


def google_api(method: str, url: str, token: str, body=None):
    return http(method, url, body, {"Authorization": f"Bearer {token}", "Content-Type": "application/json"})


_GOOGLE_META_CONTENT = re.compile(r"""content\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def google_verification_content(token: str) -> str:
    """Return only the value for <meta name="google-site-verification" content="...">."""
    token = token.strip()
    match = _GOOGLE_META_CONTENT.search(token)
    return html.unescape(match.group(1)).strip() if match else token


def verify_and_register(config: dict, site_url: str) -> None:
    if not google_configured():
        return
    token = google_access_token()
    property_url = site_url.rstrip("/") + "/"
    print("Getting Google META verification token for", property_url)
    token_result = google_api("POST", "https://www.googleapis.com/siteVerification/v1/token", token, {
        "site": {"identifier": property_url, "type": "SITE"}, "verificationMethod": "META"
    })
    config.setdefault("monitoring", {})["googleVerificationToken"] = google_verification_content(token_result["token"])
    config["monitoring"]["googleProperty"] = property_url


def finalize_google(config: dict) -> None:
    print("Finalizing Google ownership, Search Console property, and sitemap")
    monitoring = config.get("monitoring", {})
    property_url = monitoring.get("googleProperty")
    if not property_url or not google_configured():
        return
    token = google_access_token()
    verification = {"site": {"identifier": property_url, "type": "SITE"}}
    delegated_owner = os.environ.get("GOOGLE_SEARCH_CONSOLE_OWNER_EMAIL")
    if delegated_owner:
        verification["owners"] = [delegated_owner]
    verified = google_api(
        "POST",
        "https://www.googleapis.com/siteVerification/v1/webResource?verificationMethod=META",
        token,
        verification,
    )
    print("Google ownership verified:", verified.get("id", property_url))
    encoded = urllib.parse.quote(property_url, safe="")
    google_api("PUT", f"https://www.googleapis.com/webmasters/v3/sites/{encoded}", token)
    print("Search Console sites.add completed:", property_url)
    sitemap = property_url + "sitemap.xml"
    feed = urllib.parse.quote(sitemap, safe="")
    google_api("PUT", f"https://www.googleapis.com/webmasters/v3/sites/{encoded}/sitemaps/{feed}", token)
    print("Search Console sitemap submitted:", sitemap)


def _ignore_not_found(callable_, *args, **kwargs):
    try:
        return callable_(*args, **kwargs)
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        return {}


def remove_google_property(config: dict) -> None:
    """Remove the URL-prefix property from the authenticated user's GSC account."""
    property_url = config.get("monitoring", {}).get("googleProperty")
    if not property_url:
        return
    if not google_configured():
        raise RuntimeError(
            "Google credentials are required to remove the Search Console property before teardown"
        )
    token = google_access_token()
    normalized = property_url.rstrip("/") + "/"
    encoded = urllib.parse.quote(normalized, safe="")
    _ignore_not_found(
        google_api,
        "DELETE",
        f"https://www.googleapis.com/webmasters/v3/sites/{encoded}",
        token,
    )
    print("Search Console property removed:", normalized)


def remove_google_ownership(config: dict) -> None:
    """Remove ownership after hosting deletion makes the META token unreachable."""
    property_url = config.get("monitoring", {}).get("googleProperty")
    if not property_url:
        return
    if not google_configured():
        raise RuntimeError("Google credentials are required to remove Site Verification ownership")
    token = google_access_token()
    normalized = property_url.rstrip("/") + "/"

    resources = google_api(
        "GET", "https://www.googleapis.com/siteVerification/v1/webResource", token
    )
    for resource in resources.get("items", []):
        identifier = resource.get("site", {}).get("identifier", "")
        if identifier.rstrip("/") + "/" != normalized:
            continue
        resource_id = urllib.parse.quote(str(resource.get("id", "")), safe="")
        if resource_id:
            _ignore_not_found(
                google_api,
                "DELETE",
                f"https://www.googleapis.com/siteVerification/v1/webResource/{resource_id}",
                token,
            )
            print("Google ownership record removed:", normalized)


def remove_pages_project(config: dict) -> None:
    provider = config.get("deploy", {}).get("provider", "cloudflare-pages")
    if provider != "cloudflare-pages":
        raise RuntimeError(
            f"Automated teardown currently supports cloudflare-pages, not {provider!r}"
        )
    project = config.get("deploy", {}).get("project", config.get("id"))
    if not project:
        raise RuntimeError("Site config has no Cloudflare Pages project name")
    encoded = urllib.parse.quote(str(project), safe="")
    _ignore_not_found(cloudflare, "DELETE", f"/pages/projects/{encoded}")
    print("Cloudflare Pages project removed:", project)


def teardown(config: dict) -> None:
    """Remove external discovery/hosting resources; keep the local config as an audit record."""
    provider = config.get("deploy", {}).get("provider", "cloudflare-pages")
    if provider != "cloudflare-pages":
        raise RuntimeError(
            f"Automated teardown currently supports cloudflare-pages, not {provider!r}"
        )
    if config.get("monitoring", {}).get("googleProperty") and not google_configured():
        raise RuntimeError(
            "Google credentials are required to remove GSC and ownership before teardown"
        )
    remove_google_property(config)
    remove_pages_project(config)
    # Google rejects webResource.delete while its META token is still reachable.
    # Deleting the Pages project first removes that token; a retry is safe if propagation lags.
    remove_google_ownership(config)


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
    finalize_google(config)
