from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_editorial_probes():
    path = SCRIPTS / "editorial_probes.py"
    spec = importlib.util.spec_from_file_location("test_editorial_probes_module", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EditorialProbeTests(unittest.TestCase):
    def test_reviewed_portfolio_produces_a_complete_unique_corpus(self) -> None:
        generator = load_editorial_probes()
        document = json.loads((ROOT / "ideas" / "ideas.json").read_text(encoding="utf-8"))
        products_by_site: dict[str, list[dict]] = defaultdict(list)
        for product in document["ideas"]:
            products_by_site[product["siteId"]].append(product)

        titles: set[str] = set()
        bodies: set[str] = set()
        article_count = 0
        for products in products_by_site.values():
            allowed_ids = {product["id"] for product in products}
            for index, product in enumerate(products):
                peers = [candidate for candidate in products if candidate["id"] != product["id"]]
                peer = peers[index % len(peers)] if peers else None
                articles = generator.articles_for(product, product["probeContext"], peer)

                self.assertEqual(len(articles), 10)
                self.assertEqual(len({article["slug"] for article in articles}), 10)
                for article in articles:
                    linked_ids = set(re.findall(r"/products/([a-z0-9-]+)", article["content"]))
                    self.assertIn(product["id"], linked_ids)
                    self.assertLessEqual(linked_ids, allowed_ids)
                    self.assertGreaterEqual(len(re.findall(r"\b[\w’'-]+\b", article["content"])), 400)
                    self.assertNotIn(article["title"], titles)
                    self.assertNotIn(article["content"], bodies)
                    titles.add(article["title"])
                    bodies.add(article["content"])
                    article_count += 1

        self.assertEqual(len(products_by_site), 10)
        self.assertEqual(article_count, 220)

    def test_missing_probe_context_is_rejected(self) -> None:
        generator = load_editorial_probes()
        product = {
            "id": "incomplete-product",
            "name": "Incomplete Product",
            "topic": "incomplete workflows",
            "audience": "test operators",
            "problem": "The context is incomplete.",
        }

        with self.assertRaisesRegex(ValueError, "needs outcome"):
            generator.articles_for(product, {}, None)


if __name__ == "__main__":
    unittest.main()
