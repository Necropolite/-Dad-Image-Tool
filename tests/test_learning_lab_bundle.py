from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "internal" / "learning_lab"


class LearningLabBundleTests(unittest.TestCase):
    def test_required_static_files_exist(self) -> None:
        for name in ("index.html", "app.js", "styles.css"):
            self.assertTrue((LAB / name).is_file(), f"Missing Learning Lab asset: {name}")

    def test_bundle_is_the_learning_lab_lite_interface(self) -> None:
        index = (LAB / "index.html").read_text(encoding="utf-8")
        script = (LAB / "app.js").read_text(encoding="utf-8")
        self.assertIn("Learning Lab Lite", index)
        self.assertIn("Learn", index)
        self.assertIn("Ask", index)
        self.assertIn("pete-ramey-assistant-api.cramey254.workers.dev", script)
        self.assertIn("Nutrition & Hoof Health", script)
        self.assertIn("Rehabilitation Cases", script)


if __name__ == "__main__":
    unittest.main()
