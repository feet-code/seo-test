from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard"


class GscDashboardTests(unittest.TestCase):
    def test_worker_protects_api_and_keeps_credentials_in_secrets(self) -> None:
        worker = (DASHBOARD / "worker.ts").read_text(encoding="utf-8")
        config = json.loads((DASHBOARD / "wrangler.jsonc").read_text(encoding="utf-8"))

        self.assertTrue(config["assets"]["run_worker_first"])
        self.assertTrue(config["workers_dev"])
        self.assertIn("isAuthenticated(request, env)", worker)
        self.assertIn("HttpOnly; SameSite=Strict", worker)
        self.assertIn('protocol === "https:" ? "; Secure"', worker)
        self.assertIn("https://oauth2.googleapis.com/token", worker)
        self.assertNotIn("GOOGLE_REFRESH_TOKEN\"", json.dumps(config))
        self.assertNotIn("DASHBOARD_PASSWORD\"", json.dumps(config))

    def test_dashboard_loads_properties_from_gsc_not_local_sites(self) -> None:
        worker = (DASHBOARD / "worker.ts").read_text(encoding="utf-8")
        browser = (DASHBOARD / "public" / "app.js").read_text(encoding="utf-8")

        self.assertIn("https://www.googleapis.com/webmasters/v3/sites", worker)
        self.assertIn('/api/properties', browser)
        self.assertIn('/api/property-stats', browser)
        self.assertIn("sc-domain:", worker)
        self.assertNotIn('!item.siteUrl.startsWith("sc-domain:")', worker)
        self.assertIn("safePageUrl", browser)
        self.assertIn("id.replace(/-([a-z])/g", browser)
        self.assertNotIn("ideas.json", worker)


if __name__ == "__main__":
    unittest.main()
