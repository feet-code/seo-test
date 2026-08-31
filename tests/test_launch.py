from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def load_launch():
    path = ROOT / "scripts" / "launch.py"
    spec = importlib.util.spec_from_file_location("test_launch_module", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def arguments(**overrides):
    values = {
        "site": None,
        "sites": None,
        "product": None,
        "batch": None,
        "batches": None,
        "limit": 0,
        "resume": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class LaunchSelectionTests(unittest.TestCase):
    def make_site(self, root: Path, site_id: str, products: list[dict]) -> None:
        site = root / "sites" / site_id
        site.mkdir(parents=True)
        (site / "site.json").write_text(
            json.dumps({"id": site_id, "status": "active", "products": products}),
            encoding="utf-8",
        )

    def test_batch_selects_each_affected_site_once(self) -> None:
        launch = load_launch()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            launch.SITES = root / "sites"
            launch.CHECKPOINT = root / "checkpoint.json"
            self.make_site(
                root,
                "mixed-site",
                [
                    {"id": "old", "contentBatch": "batch-004"},
                    {"id": "new", "contentBatch": "batch-005"},
                ],
            )
            self.make_site(
                root,
                "new-site",
                [{"id": "new-two", "contentBatch": "batch-005"}],
            )
            self.make_site(
                root,
                "old-site",
                [{"id": "old-two", "contentBatch": "batch-003"}],
            )

            selected = launch.selected_sites(arguments(batch=["batch-005"]))

            self.assertEqual([path.name for path in selected], ["mixed-site", "new-site"])

    def test_comma_separated_batches_union_sites_then_apply_limit(self) -> None:
        launch = load_launch()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            launch.SITES = root / "sites"
            launch.CHECKPOINT = root / "checkpoint.json"
            self.make_site(root, "alpha", [{"id": "a", "contentBatch": "batch-004"}])
            self.make_site(root, "beta", [{"id": "b", "contentBatch": "batch-005"}])

            selected = launch.selected_sites(
                arguments(batches="batch-004,batch-005", limit=1)
            )

            self.assertEqual([path.name for path in selected], ["alpha"])

    def test_plain_resume_restores_the_saved_subset(self) -> None:
        launch = load_launch()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            launch.SITES = root / "sites"
            launch.CHECKPOINT = root / "checkpoint.json"
            self.make_site(root, "alpha", [{"id": "a", "contentBatch": "batch-004"}])
            self.make_site(root, "beta", [{"id": "b", "contentBatch": "batch-005"}])
            launch.CHECKPOINT.write_text(
                json.dumps({"siteIds": ["beta"], "nextIndex": 0}),
                encoding="utf-8",
            )

            selected = launch.selected_sites(arguments(resume=True))

            self.assertEqual([path.name for path in selected], ["beta"])

    def test_plain_resume_skips_removed_sites_and_preserves_checkpoint_order(self) -> None:
        launch = load_launch()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            launch.SITES = root / "sites"
            launch.CHECKPOINT = root / "checkpoint.json"
            self.make_site(root, "alpha", [{"id": "a"}])
            self.make_site(root, "beta", [{"id": "b"}])
            launch.CHECKPOINT.write_text(
                json.dumps(
                    {
                        "siteIds": ["beta", "example-invoice-followup", "alpha"],
                        "nextIndex": 0,
                    }
                ),
                encoding="utf-8",
            )

            selected = launch.selected_sites(arguments(resume=True))

            self.assertEqual([path.name for path in selected], ["beta", "alpha"])

    def test_resume_index_tracks_completed_sites_after_pruning(self) -> None:
        launch = load_launch()
        checkpoint = {
            "siteIds": ["alpha", "removed-site", "beta", "gamma"],
            "nextIndex": 2,
        }

        start = launch._resume_start_index(
            checkpoint,
            ["alpha", "beta", "gamma"],
        )

        self.assertEqual(start, 1)

    def test_unknown_batch_is_rejected_with_available_values(self) -> None:
        launch = load_launch()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            launch.SITES = root / "sites"
            launch.CHECKPOINT = root / "checkpoint.json"
            self.make_site(root, "alpha", [{"id": "a", "contentBatch": "batch-005"}])

            with self.assertRaisesRegex(SystemExit, "Available batches: batch-005"):
                launch.selected_sites(arguments(batch=["batch-999"]))


if __name__ == "__main__":
    unittest.main()
