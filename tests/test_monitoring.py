from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
