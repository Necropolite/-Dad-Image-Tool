from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.generate_version_info import render_version_info, write_version_info
from version import (
    APP_BRAND_TITLE,
    APP_NAME,
    APP_VERSION,
    BRAND_ACRONYM,
    BRAND_EXPANSION,
    BRAND_TAGLINE,
    RELEASE_ASSET_NAME,
)


class BrandingTests(unittest.TestCase):
    def test_official_branding_constants(self) -> None:
        self.assertEqual(APP_NAME, "Dad Image Tool")
        self.assertEqual(BRAND_ACRONYM, "D.A.D.")
        self.assertEqual(BRAND_EXPANSION, "Dad's Automated Downloader")
        self.assertEqual(BRAND_TAGLINE, "Download • Archive • Deliver")
        self.assertEqual(APP_BRAND_TITLE, "Dad Image Tool — D.A.D.")

    def test_technical_names_remain_unchanged(self) -> None:
        self.assertEqual(RELEASE_ASSET_NAME, "Dad-Image-Tool.exe")
        self.assertRegex(APP_VERSION, r"^\d+\.\d+\.\d+$")

    def test_windows_version_metadata_contains_brand_and_technical_name(self) -> None:
        text = render_version_info()
        for expected in (
            APP_BRAND_TITLE,
            APP_NAME,
            BRAND_ACRONYM,
            BRAND_EXPANSION,
            BRAND_TAGLINE,
            APP_VERSION,
            "Dad Image Tool.exe",
        ):
            self.assertIn(expected, text)

    def test_windows_version_metadata_can_be_written(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            destination = Path(temp_name) / "generated" / "version-info.txt"
            self.assertEqual(write_version_info(destination), destination)
            self.assertEqual(destination.read_text(encoding="utf-8"), render_version_info())


if __name__ == "__main__":
    unittest.main()
