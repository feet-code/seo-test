from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_report():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    path = ROOT / "scripts" / "gsc_report.py"
    spec = importlib.util.spec_from_file_location("test_gsc_report_module", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GscReportTests(unittest.TestCase):
    def test_property_selection_comes_from_gsc_and_excludes_domain_duplicates(self) -> None:
        report = load_report()
        properties = [
            {"siteUrl": "https://old-site.pages.dev/", "permissionLevel": "siteOwner"},
            {"siteUrl": "https://live-site.workers.dev/", "permissionLevel": "siteOwner"},
            {"siteUrl": "sc-domain:example.com", "permissionLevel": "siteOwner"},
            {"siteUrl": "https://unverified.test/", "permissionLevel": "siteUnverifiedUser"},
        ]

        selected = report.select_properties(
            properties,
            property_kind="url-prefix",
            requested=set(),
        )

        self.assertEqual(
            [item["siteUrl"] for item in selected],
            ["https://live-site.workers.dev/", "https://old-site.pages.dev/"],
        )

    def test_search_analytics_paginates_up_to_requested_limit(self) -> None:
        report = load_report()
        first_page = [
            {"keys": [f"query-{index}"], "clicks": 1, "impressions": 2, "position": 3}
            for index in range(report.MAX_API_PAGE_SIZE)
        ]
        with patch.object(
            report,
            "gsc_api",
            side_effect=[{"rows": first_page}, {"rows": [{"keys": ["last"]}]}],
        ) as api:
            rows = report.search_analytics(
                "token",
                "https://old-site.pages.dev/",
                date(2026, 8, 1),
                date(2026, 8, 28),
                dimension="query",
                search_type="web",
                data_state="final",
                max_rows=25_001,
            )

        self.assertEqual(len(rows), 25_001)
        self.assertEqual(api.call_args_list[0].args[3]["startRow"], 0)
        self.assertEqual(api.call_args_list[1].args[3]["startRow"], 25_000)
        self.assertEqual(api.call_args_list[1].args[3]["rowLimit"], 1)

    def test_query_aggregation_uses_impression_weighted_position(self) -> None:
        report = load_report()
        rows = [
            {
                "property": "https://one.test/",
                "query": "margin calculator",
                "clicks": 3.0,
                "impressions": 10.0,
                "position": 2.0,
            },
            {
                "property": "https://two.test/",
                "query": "margin calculator",
                "clicks": 1.0,
                "impressions": 30.0,
                "position": 10.0,
            },
        ]

        result = report.aggregate_queries(rows)

        self.assertEqual(result[0]["clicks"], 4.0)
        self.assertEqual(result[0]["impressions"], 40.0)
        self.assertAlmostEqual(result[0]["ctr"], 0.1)
        self.assertAlmostEqual(result[0]["position"], 8.0)
        self.assertEqual(result[0]["propertyCount"], 2)

    def test_rankings_can_sort_by_impressions_for_early_seo_signals(self) -> None:
        report = load_report()
        document = {
            "sites": [
                {"property": "clicks.test", "clicks": 5.0, "impressions": 10.0},
                {"property": "impressions.test", "clicks": 0.0, "impressions": 100.0},
            ],
            "queries": [],
            "siteQueries": [],
            "pages": [],
        }

        report.sort_rankings(document, "impressions")

        self.assertEqual(document["sites"][0]["property"], "impressions.test")


if __name__ == "__main__":
    unittest.main()
