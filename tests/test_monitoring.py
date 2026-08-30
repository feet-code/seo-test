from __future__ import annotations

import importlib.util
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_monitoring():
    path = ROOT / "scripts" / "monitoring.py"
    spec = importlib.util.spec_from_file_location("test_monitoring_module", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MonitoringVerificationTests(unittest.TestCase):
    def test_meta_parser_handles_attribute_order_and_html_entities(self) -> None:
        monitoring = load_monitoring()

        self.assertEqual(
            monitoring.google_verification_meta_contents(
                '<html><head><meta content="token&amp;value" data-x="1" '
                'name="google-site-verification"></head></html>'
            ),
            ["token&value"],
        )

    def test_public_meta_wait_retries_until_the_exact_token_is_visible(self) -> None:
        monitoring = load_monitoring()
        stale = '<meta name="google-site-verification" content="old-token">'
        current = '<meta content="new-token" name="google-site-verification">'

        with (
            patch.object(
                monitoring,
                "_fetch_public_html",
                side_effect=[stale, current],
            ) as fetch,
            patch.object(monitoring.time, "sleep") as sleep,
        ):
            monitoring.wait_for_verification_meta(
                "https://audience-tools.pages.dev/",
                "new-token",
                timeout_seconds=10,
                poll_seconds=0.01,
            )

        self.assertEqual(fetch.call_count, 2)
        sleep.assert_called_once()

    def test_existing_token_is_reused_on_resume(self) -> None:
        monitoring = load_monitoring()
        config = {
            "monitoring": {
                "googleProperty": "https://audience-tools.pages.dev/",
                "googleVerificationToken": "existing-token",
            }
        }

        with (
            patch.object(monitoring, "google_configured", return_value=True),
            patch.object(monitoring, "google_access_token") as access_token,
            patch.object(monitoring, "google_api") as google_api,
        ):
            monitoring.verify_and_register(
                config,
                "https://audience-tools.pages.dev",
            )

        access_token.assert_not_called()
        google_api.assert_not_called()
        self.assertEqual(
            config["monitoring"]["googleVerificationToken"],
            "existing-token",
        )

    def test_google_token_not_found_is_retried_before_gsc_registration(self) -> None:
        monitoring = load_monitoring()
        calls = []
        verification_attempts = 0

        def fake_api(method, url, token, body=None):
            nonlocal verification_attempts
            calls.append((method, url, token, body))
            if method == "POST" and "webResource?verificationMethod=META" in url:
                verification_attempts += 1
                if verification_attempts == 1:
                    error = urllib.error.HTTPError(
                        url,
                        400,
                        "Bad Request",
                        {},
                        None,
                    )
                    error.response_detail = (
                        '{"error":{"message":"The necessary verification token '
                        'could not be found on your site."}}'
                    )
                    raise error
                return {"id": "verified-resource"}
            return {}

        config = {
            "monitoring": {
                "googleProperty": "https://audience-tools.pages.dev/",
                "googleVerificationToken": "expected-token",
            }
        }
        with (
            patch.object(monitoring, "google_configured", return_value=True),
            patch.object(monitoring, "google_access_token", return_value="oauth-token"),
            patch.object(monitoring, "google_api", side_effect=fake_api),
            patch.object(monitoring, "wait_for_verification_meta") as wait_for_meta,
            patch.object(monitoring, "_verification_timing", return_value=(30.0, 0.01)),
            patch.object(monitoring.time, "sleep") as sleep,
        ):
            monitoring.finalize_google(config)

        wait_for_meta.assert_called_once()
        sleep.assert_called_once()
        self.assertEqual(
            [method for method, _url, _token, _body in calls],
            ["POST", "POST", "PUT", "PUT"],
        )

    def test_unrelated_google_bad_request_is_not_retried(self) -> None:
        monitoring = load_monitoring()
        error = urllib.error.HTTPError(
            "https://www.googleapis.com/siteVerification/v1/webResource",
            400,
            "Bad Request",
            {},
            None,
        )
        error.response_detail = '{"error":{"message":"Invalid site identifier"}}'
        config = {
            "monitoring": {
                "googleProperty": "https://audience-tools.pages.dev/",
                "googleVerificationToken": "expected-token",
            }
        }

        with (
            patch.object(monitoring, "google_configured", return_value=True),
            patch.object(monitoring, "google_access_token", return_value="oauth-token"),
            patch.object(monitoring, "google_api", side_effect=error) as google_api,
            patch.object(monitoring, "wait_for_verification_meta"),
            patch.object(monitoring, "_verification_timing", return_value=(30.0, 0.01)),
            patch.object(monitoring.time, "sleep") as sleep,
        ):
            with self.assertRaises(urllib.error.HTTPError):
                monitoring.finalize_google(config)

        google_api.assert_called_once()
        sleep.assert_not_called()


class MonitoringTeardownTests(unittest.TestCase):
    def test_remove_google_property_deletes_gsc_property(self) -> None:
        monitoring = load_monitoring()
        calls = []

        def fake_api(method, url, token, body=None):
            calls.append((method, url, token, body))
            return {}

        with (
            patch.object(monitoring, "google_configured", return_value=True),
            patch.object(monitoring, "google_access_token", return_value="token"),
            patch.object(monitoring, "google_api", side_effect=fake_api),
        ):
            monitoring.remove_google_property(
                {
                    "monitoring": {
                        "googleProperty": "https://audience-tools.pages.dev/"
                    }
                }
            )

        self.assertEqual([call[0] for call in calls], ["DELETE"])
        self.assertIn(
            "https%3A%2F%2Faudience-tools.pages.dev%2F",
            calls[0][1],
        )

    def test_remove_google_ownership_deletes_matching_verification_record(self) -> None:
        monitoring = load_monitoring()
        calls = []

        def fake_api(method, url, token, body=None):
            calls.append((method, url, token, body))
            if method == "GET":
                return {
                    "items": [
                        {
                            "id": "https://audience-tools.pages.dev/",
                            "site": {"identifier": "https://audience-tools.pages.dev/"},
                        },
                        {
                            "id": "other",
                            "site": {"identifier": "https://other.pages.dev/"},
                        },
                    ]
                }
            return {}

        with (
            patch.object(monitoring, "google_configured", return_value=True),
            patch.object(monitoring, "google_access_token", return_value="token"),
            patch.object(monitoring, "google_api", side_effect=fake_api),
        ):
            monitoring.remove_google_ownership(
                {"monitoring": {"googleProperty": "https://audience-tools.pages.dev/"}}
            )

        self.assertEqual([call[0] for call in calls], ["GET", "DELETE"])
        self.assertIn("/siteVerification/v1/webResource/", calls[1][1])

    def test_remove_pages_project_uses_configured_project(self) -> None:
        monitoring = load_monitoring()
        with patch.object(monitoring, "cloudflare", return_value={}) as cloudflare:
            monitoring.remove_pages_project(
                {
                    "id": "site-id",
                    "deploy": {
                        "provider": "cloudflare-pages",
                        "project": "stable-project",
                    },
                }
            )

        cloudflare.assert_called_once_with(
            "DELETE",
            "/pages/projects/stable-project",
        )

    def test_teardown_removes_host_before_site_verification_ownership(self) -> None:
        monitoring = load_monitoring()
        order = []
        config = {
            "id": "site-id",
            "deploy": {"provider": "cloudflare-pages", "project": "site-id"},
            "monitoring": {"googleProperty": "https://site-id.pages.dev/"},
        }
        with (
            patch.object(monitoring, "google_configured", return_value=True),
            patch.object(
                monitoring,
                "remove_google_property",
                side_effect=lambda value: order.append("gsc"),
            ),
            patch.object(
                monitoring,
                "remove_pages_project",
                side_effect=lambda value: order.append("hosting"),
            ),
            patch.object(
                monitoring,
                "remove_google_ownership",
                side_effect=lambda value: order.append("ownership"),
            ),
        ):
            monitoring.teardown(config)

        self.assertEqual(order, ["gsc", "hosting", "ownership"])

    def test_worker_teardown_deletes_the_worker_script(self) -> None:
        monitoring = load_monitoring()
        order = []
        config = {
            "id": "worker-site",
            "deploy": {
                "provider": "cloudflare-auto",
                "resolvedProvider": "cloudflare-workers",
                "project": "worker-site",
            },
        }
        with (
            patch.object(
                monitoring,
                "remove_google_property",
                side_effect=lambda value: order.append("gsc"),
            ),
            patch.object(
                monitoring,
                "remove_worker_script",
                side_effect=lambda value: order.append("hosting"),
            ),
            patch.object(
                monitoring,
                "remove_google_ownership",
                side_effect=lambda value: order.append("ownership"),
            ),
        ):
            monitoring.teardown(config)

        self.assertEqual(order, ["gsc", "hosting", "ownership"])


class CloudflareHostingTests(unittest.TestCase):
    def config(self) -> dict:
        return {
            "id": "audience-tools",
            "domain": None,
            "deploy": {
                "provider": "cloudflare-auto",
                "project": "audience-tools",
            },
        }

    def test_auto_uses_workers_at_the_real_pages_project_limit(self) -> None:
        monitoring = load_monitoring()
        with (
            patch.object(monitoring, "_page_project_exists", return_value=False),
            patch.object(monitoring, "pages_project_count", return_value=100),
            patch.object(monitoring, "_pages_limit", return_value=100),
            patch.object(monitoring, "cloudflare") as cloudflare,
        ):
            provider = monitoring.resolve_cloudflare_auto(self.config())

        self.assertEqual(provider, "cloudflare-workers")
        cloudflare.assert_not_called()

    def test_workers_subdomain_403_explains_required_token_permission(self) -> None:
        monitoring = load_monitoring()
        error = urllib.error.HTTPError(
            "https://api.cloudflare.com/client/v4/accounts/test/workers/subdomain",
            403,
            "Forbidden",
            {},
            None,
        )
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(monitoring, "cloudflare", side_effect=error),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Account > Workers Scripts > Edit",
            ):
                monitoring.workers_subdomain()

    def test_pages_project_count_uses_supported_default_page_size(self) -> None:
        monitoring = load_monitoring()
        response = {
            "result": [{"name": "first"}],
            "result_info": {"page": 1, "per_page": 20, "total_count": 73},
        }

        with patch.object(monitoring, "cloudflare", return_value=response) as cloudflare:
            count = monitoring.pages_project_count()

        self.assertEqual(count, 73)
        cloudflare.assert_called_once_with("GET", "/pages/projects")

    def test_pages_project_count_paginates_without_per_page_override(self) -> None:
        monitoring = load_monitoring()
        responses = [
            {
                "result": [{"name": "first"}, {"name": "second"}],
                "result_info": {"page": 1, "per_page": 2, "total_pages": 2},
            },
            {
                "result": [{"name": "third"}],
                "result_info": {"page": 2, "per_page": 2, "total_pages": 2},
            },
        ]

        with patch.object(monitoring, "cloudflare", side_effect=responses) as cloudflare:
            count = monitoring.pages_project_count()

        self.assertEqual(count, 3)
        self.assertEqual(
            [call.args for call in cloudflare.call_args_list],
            [("GET", "/pages/projects"), ("GET", "/pages/projects?page=2")],
        )

    def test_auto_reuses_existing_pages_project_even_at_capacity(self) -> None:
        monitoring = load_monitoring()
        with (
            patch.object(monitoring, "_page_project_exists", return_value=True),
            patch.object(monitoring, "pages_project_count") as project_count,
        ):
            provider = monitoring.resolve_cloudflare_auto(self.config())

        self.assertEqual(provider, "cloudflare-pages")
        project_count.assert_not_called()

    def test_pages_capacity_response_falls_back_and_persists_worker_url(self) -> None:
        monitoring = load_monitoring()
        error = urllib.error.HTTPError(
            "https://api.cloudflare.com/client/v4/accounts/test/pages/projects",
            400,
            "Bad Request",
            {},
            None,
        )
        error.response_detail = '{"errors":[{"message":"Pages project limit exceeded"}]}'
        with TemporaryDirectory() as directory:
            site_dir = Path(directory)
            with (
                patch.object(
                    monitoring,
                    "resolve_cloudflare_auto",
                    return_value="cloudflare-pages",
                ),
                patch.object(monitoring, "provision_pages", side_effect=error),
                patch.object(monitoring, "pages_project_count", return_value=100),
                patch.object(
                    monitoring,
                    "worker_url",
                    return_value="https://audience-tools.account.workers.dev",
                ),
            ):
                config = monitoring.prepare_hosting(self.config(), site_dir)

            self.assertEqual(
                config["deploy"]["resolvedProvider"],
                "cloudflare-workers",
            )
            self.assertEqual(
                config["deploy"]["url"],
                "https://audience-tools.account.workers.dev",
            )
            self.assertEqual(config["deploy"]["provider"], "cloudflare-auto")
            self.assertTrue((site_dir / "site.json").exists())

    def test_error_8000027_falls_back_even_for_legacy_explicit_pages_config(self) -> None:
        monitoring = load_monitoring()
        error = urllib.error.HTTPError(
            "https://api.cloudflare.com/client/v4/accounts/test/pages/projects",
            400,
            "Bad Request",
            {},
            None,
        )
        error.response_detail = (
            '{"errors":[{"code":8000027,"message":"You have reached the limit '
            'of projects you can have on your account."}]}'
        )
        config = self.config()
        config["deploy"]["provider"] = "cloudflare-pages"

        with TemporaryDirectory() as directory:
            site_dir = Path(directory)
            with (
                patch.object(monitoring, "provision_pages", side_effect=error),
                patch.object(monitoring, "pages_project_count", return_value=37),
                patch.object(
                    monitoring,
                    "worker_url",
                    return_value="https://audience-tools.account.workers.dev",
                ),
            ):
                result = monitoring.prepare_hosting(config, site_dir)

        self.assertEqual(result["deploy"]["resolvedProvider"], "cloudflare-workers")
        self.assertEqual(result["deploy"]["provider"], "cloudflare-auto")
        self.assertEqual(monitoring._known_pages_capacity(), 37)

    def test_observed_pages_limit_routes_following_projects_to_workers(self) -> None:
        monitoring = load_monitoring()
        monitoring._record_pages_capacity(37)

        with (
            patch.object(monitoring, "_page_project_exists", return_value=False),
            patch.object(monitoring, "pages_project_count", return_value=37),
        ):
            provider = monitoring.resolve_cloudflare_auto(self.config())

        self.assertEqual(provider, "cloudflare-workers")


if __name__ == "__main__":
    unittest.main()
