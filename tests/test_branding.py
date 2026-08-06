from __future__ import annotations

import unittest

import build_version_info
from version import (
    APP_DISPLAY_NAME,
    APP_NAME,
    APP_VERSION,
    BRAND_FULL_NAME,
    BRAND_NAME,
    PRODUCT_DESCRIPTION,
    RELEASE_ASSET_NAME,
    SETUP_ASSET_NAME,
    TAGLINE,
)


class BrandingTests(unittest.TestCase):
    def test_product_name_is_primary(self) -> None:
        self.assertEqual(APP_NAME, "Dad Image Tool")
        self.assertEqual(APP_DISPLAY_NAME, APP_NAME)
        self.assertEqual(PRODUCT_DESCRIPTION, "Automatic image converter")
        self.assertEqual(SETUP_ASSET_NAME, "Dad-Image-Tool-Setup.exe")
        self.assertEqual(RELEASE_ASSET_NAME, "Dad-Image-Tool.exe")

    def test_secondary_nickname_is_preserved(self) -> None:
        self.assertEqual(BRAND_NAME, "D.A.D.")
        self.assertEqual(BRAND_FULL_NAME, "Dad's Automated Dropzone")
        self.assertEqual(TAGLINE, "Drop • Archive • Deliver")

    def test_windows_metadata_leads_with_product_name(self) -> None:
        metadata = build_version_info.render_version_info()
        self.assertIn(f"StringStruct('ProductVersion', '{APP_VERSION}')", metadata)
        self.assertIn(f"StringStruct('ProductName', '{APP_NAME}')", metadata)
        self.assertIn(f"StringStruct('FileDescription', '{APP_NAME}')", metadata)
        self.assertIn(PRODUCT_DESCRIPTION, metadata)


if __name__ == "__main__":
    unittest.main()
