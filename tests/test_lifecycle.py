from __future__ import annotations

import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"test_{name}_module", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LifecycleTests(unittest.TestCase):
    def make_site(self, lifecycle, root: Path) -> Path:
        lifecycle.SITES = root / "sites"
        site_dir = lifecycle.SITES / "audience-tools"
        site_dir.mkdir(parents=True)
        path = site_dir / "site.json"
        path.write_text(
            json.dumps(
                {
                    "id": "audience-tools",
                    "status": "active",
                    "products": [{"id": "one"}, {"id": "two"}],
                    "deploy": {
                        "provider": "cloudflare-pages",
                        "project": "audience-tools",
                    },
                    "monitoring": {
                        "googleProperty": "https://audience-tools.pages.dev/"
                    },
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_retire_is_reversible(self) -> None:
        lifecycle = load_script("portfolio")
        with TemporaryDirectory() as directory:
            path = self.make_site(lifecycle, Path(directory))

            lifecycle.set_status("audience-tools", "retired")
            retired = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(retired["status"], "retired")

            lifecycle.set_status("audience-tools", "active")
            active = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(active["status"], "active")

    def test_teardown_is_preview_only_without_exact_confirmation(self) -> None:
        lifecycle = load_script("portfolio")
        with TemporaryDirectory() as directory:
            path = self.make_site(lifecycle, Path(directory))
            called = []
            fake_monitoring = types.SimpleNamespace(teardown=lambda config: called.append(config))
            with patch.dict(sys.modules, {"monitoring": fake_monitoring}):
                lifecycle.teardown("audience-tools", False, None)

            self.assertEqual(called, [])
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8"))["status"],
                "active",
            )

    def test_confirmed_teardown_marks_destroyed_after_external_success(self) -> None:
        lifecycle = load_script("portfolio")
        with TemporaryDirectory() as directory:
            path = self.make_site(lifecycle, Path(directory))
            called = []
            fake_monitoring = types.SimpleNamespace(teardown=lambda config: called.append(config["id"]))
            with patch.dict(sys.modules, {"monitoring": fake_monitoring}):
                lifecycle.teardown(
                    "audience-tools",
                    False,
                    "audience-tools",
                )

            self.assertEqual(called, ["audience-tools"])
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8"))["status"],
                "destroyed",
            )


if __name__ == "__main__":
    unittest.main()
