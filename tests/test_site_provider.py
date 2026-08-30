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
