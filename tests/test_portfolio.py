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
    def test_version_two_materializes_one_site_with_five_products(self) -> None:
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
            self.assertEqual(len(config["products"]), 5)
            self.assertEqual(config["articlesPerProduct"], 10)
            self.assertEqual(ideas.materialize(document), 0)

    def test_cross_site_product_mismatch_is_rejected(self) -> None:
        ideas = load_script("ideas")
        document = ideas.mock_document()
        document["ideas"][0]["siteId"] = "wrong-site"
        with self.assertRaisesRegex(ideas.PortfolioError, "expected"):
            ideas.validate_document(document)

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
            self.assertEqual(first, 10)
            self.assertEqual(second, 0)
            self.assertEqual(len(posts), 10)
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


if __name__ == "__main__":
    unittest.main()
