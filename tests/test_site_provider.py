from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_site_script():
    path = ROOT / "scripts" / "site.py"
    spec = importlib.util.spec_from_file_location("test_site_provider_module", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class WorkersStaticAssetsTests(unittest.TestCase):
    def test_build_removes_previous_output_and_next_cache(self) -> None:
        site = load_site_script()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            site.ROOT = root
            site.SITES = root / "sites"
            site.OUT = root / "out"
            site.NEXT_BUILD = root / ".next"
            site_dir = site.SITES / "fresh-site"
            site_dir.mkdir(parents=True)
            (site_dir / "site.json").write_text(
                json.dumps({"id": "fresh-site", "name": "Fresh Site"}),
                encoding="utf-8",
            )
            site.OUT.mkdir()
            site.NEXT_BUILD.mkdir()
            (site.OUT / "previous-site.html").write_text("stale", encoding="utf-8")
            (site.NEXT_BUILD / "previous-site.txt").write_text("stale", encoding="utf-8")

            def fake_build(command, *, env=None):
                self.assertEqual(command, ["npm", "run", "build"])
                self.assertFalse(site.OUT.exists())
                self.assertFalse(site.NEXT_BUILD.exists())
                self.assertEqual(env["SITE_NAME"], "Fresh Site")
                site.OUT.mkdir()
                (site.OUT / "index.html").write_text("fresh", encoding="utf-8")

            with patch.object(site, "run", side_effect=fake_build) as run:
                site.build("fresh-site")

            run.assert_called_once()
            self.assertFalse((site.OUT / "previous-site.html").exists())
            self.assertEqual((site.OUT / "index.html").read_text(), "fresh")

    def test_worker_deploy_uses_static_assets_and_workers_dev(self) -> None:
        site = load_site_script()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            site.ROOT = root
            site.SITES = root / "sites"
            site.OUT = root / "out"
            site.DEPLOY = root / ".deploy"
            site_dir = site.SITES / "audience-tools"
            site_dir.mkdir(parents=True)
            site.OUT.mkdir()
            (site.OUT / "index.html").write_text("ok", encoding="utf-8")
            (site_dir / "site.json").write_text(
                json.dumps(
                    {
                        "id": "audience-tools",
                        "deploy": {"project": "audience-tools"},
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(site, "run") as run:
                site.deploy("audience-tools", "cloudflare-workers")

            config_path = (
                site.DEPLOY / "cloudflare-workers" / "audience-tools" / "wrangler.jsonc"
            )
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertTrue(config["workers_dev"])
            self.assertEqual(config["name"], "audience-tools")
            self.assertEqual(config["assets"]["directory"], str(site.OUT.resolve()))
            run.assert_called_once()
            self.assertEqual(run.call_args.args[0][:3], ["npx", "wrangler", "deploy"])


if __name__ == "__main__":
    unittest.main()
