from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.generate_review_fixtures import create_fixtures


class ReviewFixtureTests(unittest.TestCase):
    def test_fixture_generator_creates_success_and_failure_cases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            destination = create_fixtures(Path(temp_name) / "fixtures")
            self.assertTrue((destination / "ordinary-images" / "horse.png").exists())
            self.assertTrue((destination / "duplicate-names" / "first" / "same.png").exists())
            self.assertTrue((destination / "nested-zip.zip").exists())
            self.assertTrue((destination / "corrupt-image.png").exists())
            self.assertTrue((destination / "path-traversal.zip").exists())
            with zipfile.ZipFile(destination / "nested-zip.zip") as archive:
                self.assertIn("nested/inner.zip", archive.namelist())
