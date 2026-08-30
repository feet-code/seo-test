from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"test_{name}_images", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ImageFreeBlogTests(unittest.TestCase):
    def test_every_committed_blog_is_image_free(self) -> None:
        root_paths = sorted((ROOT / "_posts").glob("*.md"))
        site_paths = sorted((ROOT / "sites").glob("*/_posts/*.md"))
        self.assertGreater(len(root_paths), 0)
        self.assertEqual(site_paths, [])
        paths = root_paths
        forbidden = re.compile(
            r"^(?:coverImage|ogImage):|^\s+picture:|!\[[^\]]*\]\(|<img\b",
            re.MULTILINE | re.IGNORECASE,
        )
        offenders = [str(path.relative_to(ROOT)) for path in paths if forbidden.search(path.read_text(encoding="utf-8"))]
        self.assertEqual(offenders, [])

    def test_generator_strips_model_image_markup(self) -> None:
        generator = load_script("generate_posts")
        content = "Before ![useful diagram](https://example.test/a.jpg) after <img src='x'>."

        cleaned = generator.strip_images(content)

        self.assertEqual(cleaned, "Before useful diagram after .")
        self.assertNotIn("![", cleaned)
        self.assertNotIn("<img", cleaned)

    def test_site_configs_have_no_blog_image_defaults(self) -> None:
        offenders = []
        for path in sorted((ROOT / "sites").glob("*/site.json")):
            text = path.read_text(encoding="utf-8")
            if '"images"' in text or '"picture"' in text:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
