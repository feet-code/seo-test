from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"test_{name}_module", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PortfolioTests(unittest.TestCase):
    def test_version_two_materializes_a_variable_size_site(self) -> None:
        ideas = load_script("ideas")
        document = ideas.mock_document()
        ideas.validate_document(document)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            ideas.SITES = root / "sites"
            created = ideas.materialize(document)
            self.assertEqual(created, 1)
            config = json.loads(
                (ideas.SITES / "freelancer-operations" / "site.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(len(config["products"]), 3)
            self.assertEqual(config["articlesPerProduct"], 10)
            self.assertEqual(ideas.materialize(document), 0)

    def test_uneven_group_sizes_are_valid(self) -> None:
        ideas = load_script("ideas")
        document = ideas.mock_document()
        first, rest = document["ideas"][0], document["ideas"][1:]
        document["sites"] = [
            {
                "id": "solo-audience",
                "name": "Solo Audience",
                "audience": "solo audience",
                "topic": "solo topic",
                "productIds": [first["id"]],
            },
            {
                "id": "paired-audience",
                "name": "Paired Audience",
                "audience": "paired audience",
                "topic": "paired topic",
                "productIds": [product["id"] for product in rest],
            },
        ]
        first["siteId"] = "solo-audience"
        for product in rest:
            product["siteId"] = "paired-audience"

        ideas.validate_document(document)

    def test_mock_generation_writes_a_flexible_grouped_portfolio(self) -> None:
        ideas = load_script("ideas")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            ideas.IDEAS_DIR = root / "ideas"
            ideas.IDEAS = ideas.IDEAS_DIR / "ideas.json"
            ideas.SITES = root / "sites"
            ideas.STATE = root / "state"

            document = ideas.generate_portfolio(
                17, preferred=5, maximum=7, mock=True
            )
            sizes = [
                sum(idea["siteId"] == site["id"] for idea in document["ideas"])
                for site in document["sites"]
            ]

            self.assertEqual(len(document["ideas"]), 17)
            self.assertEqual(sum(sizes), 17)
            self.assertGreater(len(set(sizes)), 1)
            self.assertTrue(all(1 <= size <= 7 for size in sizes))
            self.assertTrue(
                all("productIds" not in site for site in document["sites"])
            )
            self.assertTrue(ideas.IDEAS.exists())
            ideas.validate_document(document)

            plan = ideas.sync_document(document, apply=True)
            self.assertEqual(len(plan.create), len(document["sites"]))
            checkpoint = json.loads(
                ideas._generation_checkpoint().read_text(encoding="utf-8")
            )
            self.assertTrue(checkpoint["complete"])

            repeated = ideas.generate_portfolio(
                17, preferred=5, maximum=7, mock=True
            )
            self.assertEqual(repeated["generation"]["runId"], document["generation"]["runId"])

    def test_generation_resumes_completed_audience_groups(self) -> None:
        ideas = load_script("ideas")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            ideas.IDEAS_DIR = root / "ideas"
            ideas.IDEAS = ideas.IDEAS_DIR / "ideas.json"
            ideas.STATE = root / "state"
            plan = ideas.mock_audience_plan(12, preferred=5, maximum=7)
            first_products = ideas.mock_products(plan[0], set())
            settings = ideas._generation_settings(12, 5, 7, True)
            checkpoint = {
                "version": ideas.IDEA_GENERATION_VERSION,
                "runId": "resume-test",
                "createdAt": "2026-01-01T00:00:00+00:00",
                "updatedAt": "2026-01-01T00:00:00+00:00",
                "settings": settings,
                "plan": plan,
                "completedProducts": {plan[0]["id"]: first_products},
                "complete": False,
            }
            ideas._atomic_json(ideas._generation_checkpoint(), checkpoint)

            document = ideas.generate_portfolio(
                12, preferred=5, maximum=7, mock=True
            )

            self.assertEqual(document["generation"]["runId"], "resume-test")
            self.assertEqual(
                [
                    product["id"]
                    for product in document["ideas"]
                    if product["siteId"] == plan[0]["id"]
                ],
                [product["id"] for product in first_products],
            )
            self.assertEqual(len(document["ideas"]), 12)
            self.assertTrue(
                json.loads(ideas._generation_checkpoint().read_text())["complete"]
            )

    def test_failed_generation_preserves_the_previous_ideas_file(self) -> None:
        ideas = load_script("ideas")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            ideas.IDEAS_DIR = root / "ideas"
            ideas.IDEAS = ideas.IDEAS_DIR / "ideas.json"
            ideas.STATE = root / "state"
            original = ideas.mock_document()
            ideas._atomic_json(ideas.IDEAS, original)
            before = ideas.IDEAS.read_text(encoding="utf-8")

            def fail(*_args, **_kwargs):
                raise ideas.GenerationError("simulated Gemini failure")

            ideas._call_gemini_json = fail
            with self.assertRaisesRegex(ideas.GenerationError, "simulated"):
                ideas.generate_portfolio(9, preferred=4, maximum=6)

            self.assertEqual(ideas.IDEAS.read_text(encoding="utf-8"), before)

    def test_sync_updates_portfolio_content_but_preserves_operations(self) -> None:
        ideas = load_script("ideas")
        document = ideas.mock_document()
        with TemporaryDirectory() as directory:
            ideas.SITES = Path(directory) / "sites"
            ideas.materialize(document)
            path = ideas.SITES / "freelancer-operations" / "site.json"
            config = json.loads(path.read_text(encoding="utf-8"))
            config.update(
                {
                    "domain": "tools.example.com",
                    "status": "retired",
                    "articlesPerProduct": 3,
                    "monitoring": {"googleProperty": "https://tools.example.com/"},
                }
            )
            config["deploy"]["project"] = "stable-project"
            path.write_text(json.dumps(config), encoding="utf-8")
            document["ideas"][0]["name"] = "Invoice Nudge Pro"

            plan = ideas.sync_document(document, apply=True)
            updated = json.loads(path.read_text(encoding="utf-8"))

            self.assertEqual(plan.update, ["freelancer-operations"])
            self.assertEqual(updated["products"][0]["name"], "Invoice Nudge Pro")
            self.assertEqual(updated["domain"], "tools.example.com")
            self.assertEqual(updated["status"], "retired")
            self.assertEqual(updated["articlesPerProduct"], 3)
            self.assertEqual(updated["deploy"]["project"], "stable-project")
            self.assertEqual(
                updated["monitoring"]["googleProperty"], "https://tools.example.com/"
            )

    def test_unknown_idea_site_id_is_rejected(self) -> None:
        ideas = load_script("ideas")
        document = ideas.mock_document()
        document["ideas"][0]["siteId"] = "wrong-site"
        with self.assertRaisesRegex(ideas.PortfolioError, "unknown siteId"):
            ideas.validate_document(document)

    def test_manual_idea_only_needs_an_existing_site_id(self) -> None:
        ideas = load_script("ideas")
        document = ideas.mock_document()
        added = dict(document["ideas"][0])
        added.update(
            {
                "id": "proposal-reminder",
                "name": "Proposal Reminder",
                "product": "A focused proposal follow-up reminder.",
                "problem": "Freelancers forget to follow up on open proposals.",
                "topic": "proposal follow-up workflows",
            }
        )
        document["ideas"].append(added)

        ideas.validate_document(document)
        grouped = ideas.normalized_sites(document)

        self.assertEqual(len(grouped), 1)
        self.assertEqual(len(grouped[0][1]), 4)

    def test_legacy_product_ids_remain_importable(self) -> None:
        ideas = load_script("ideas")
        document = ideas.mock_document()
        product_ids = [product.pop("siteId") for product in document["ideas"]]
        self.assertEqual(set(product_ids), {"freelancer-operations"})
        document["sites"][0]["productIds"] = [
            product["id"] for product in document["ideas"]
        ]

        ideas.validate_document(document)

        self.assertEqual(len(ideas.normalized_sites(document)[0][1]), 3)

    def test_generation_is_product_attributed_and_resumable(self) -> None:
        ideas = load_script("ideas")
        generator = load_script("generate_posts")
        document = ideas.mock_document()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            ideas.SITES = root / "sites"
            ideas.materialize(document)
            generator.SITES = ideas.SITES
            generator.STATE = root / "state"
            site_path = generator.SITES / "freelancer-operations" / "site.json"
            site = json.loads(site_path.read_text(encoding="utf-8"))
            site["articlesPerProduct"] = 2
            site_path.write_text(json.dumps(site), encoding="utf-8")

            first = generator.generate_site("freelancer-operations", mock=True, force=False)
            second = generator.generate_site("freelancer-operations", mock=True, force=False)
            posts = sorted((site_path.parent / "_posts").glob("*.md"))
            self.assertEqual(first, 6)
            self.assertEqual(second, 0)
            self.assertEqual(len(posts), 6)
            for product in site["products"]:
                attributed = generator.existing_product_posts(site_path.parent, product["id"])
                self.assertEqual(len(attributed), 2)
                self.assertIn(
                    f"productName: {json.dumps(product['name'])}",
                    attributed[0].read_text(encoding="utf-8")[:1500],
                )
            checkpoint = json.loads(
                (generator.STATE / "generate-freelancer-operations.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(checkpoint["complete"])

            site["products"][0]["topic"] = "updated invoice follow-up workflows"
            site_path.write_text(json.dumps(site), encoding="utf-8")
            changed = generator.generate_site(
                "freelancer-operations", mock=True, force=False
            )
            self.assertEqual(changed, 2)


if __name__ == "__main__":
    unittest.main()
