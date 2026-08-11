from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SRC_DIR = Path(__file__).resolve().parents[1] / "internal" / "src"
sys.path.insert(0, str(SRC_DIR))

import learning_lab_launcher


class LearningLabLauncherTests(unittest.TestCase):
    def test_source_path_points_to_learning_lab_index(self) -> None:
        with patch.object(sys, "frozen", False, create=True):
            path = learning_lab_launcher.learning_lab_path()
        self.assertEqual(path.name, "index.html")
        self.assertEqual(path.parent.name, "learning_lab")

    def test_packaged_path_uses_meipass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            with (
                patch.object(sys, "frozen", True, create=True),
                patch.object(sys, "_MEIPASS", str(root), create=True),
            ):
                self.assertEqual(
                    learning_lab_launcher.learning_lab_path(),
                    root / "learning_lab" / "index.html",
                )

    def test_open_learning_lab_opens_local_file_uri(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            page = Path(temp_name) / "index.html"
            page.write_text("<html></html>", encoding="utf-8")
            opened: list[str] = []
            with patch.object(learning_lab_launcher, "learning_lab_path", return_value=page):
                uri = learning_lab_launcher.open_learning_lab(opener=opened.append)
        self.assertTrue(uri.startswith("file:"))
        self.assertEqual(opened, [uri])

    def test_missing_bundle_fails_clearly(self) -> None:
        missing = Path("definitely-missing-learning-lab-index.html")
        with patch.object(learning_lab_launcher, "learning_lab_path", return_value=missing):
            with self.assertRaises(FileNotFoundError):
                learning_lab_launcher.open_learning_lab(opener=lambda _url: None)


if __name__ == "__main__":
    unittest.main()
