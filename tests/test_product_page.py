from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_PAGE = ROOT / "src" / "app" / "products" / "[id]" / "page.tsx"


class PublicProductPageTests(unittest.TestCase):
    def test_product_page_does_not_expose_internal_research_language(self) -> None:
        source = PRODUCT_PAGE.read_text(encoding="utf-8")
        forbidden = [
            "What the probe must validate",
            "Pricing hypothesis",
            "early validation hypothesis",
            "search probes",
            "product.primaryRisk",
            "product.monetization",
            "product.profitRationale",
            "product.economicDriver",
        ]

        for phrase in forbidden:
            self.assertNotIn(phrase, source)

    def test_product_page_has_customer_facing_sales_sections(self) -> None:
        source = PRODUCT_PAGE.read_text(encoding="utf-8")

        for phrase in [
            "The challenge",
            "The solution",
            "How it works",
            "Built for your operation",
            "Get early access",
        ]:
            self.assertIn(phrase, source)


if __name__ == "__main__":
    unittest.main()
