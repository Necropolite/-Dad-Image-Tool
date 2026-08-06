from __future__ import annotations

import unittest

import build_installer_config
import build_version_info
from version import APP_NAME, APP_VERSION, BRAND_FULL_NAME, BRAND_NAME, RELEASE_ASSET_NAME, TAGLINE


class BrandingTests(unittest.TestCase):
    def test_official_identity_is_locked(self) -> None:
        self.assertEqual(BRAND_NAME, "D.A.D.")
        self.assertEqual(BRAND_FULL_NAME, "Dad's Automated Dropzone")
        self.assertEqual(TAGLINE, "Drop • Archive • Deliver")
        self.assertEqual(APP_NAME, "Dad Image Tool")
        self.assertEqual(RELEASE_ASSET_NAME, "Dad-Image-Tool.exe")

    def test_windows_version_info_matches_application_version(self) -> None:
        metadata = build_version_info.render_version_info()
        self.assertIn(f"StringStruct('ProductVersion', '{APP_VERSION}')", metadata)
        self.assertIn(f"StringStruct('ProductName', '{APP_NAME}')", metadata)
        self.assertIn(BRAND_FULL_NAME, metadata)
        self.assertIn(TAGLINE, metadata)

    def test_installer_config_matches_official_identity(self) -> None:
        config = build_installer_config.render_installer_config()
        self.assertIn(f'#define MyAppVersion "{APP_VERSION}"', config)
        self.assertIn(f'#define MyAppName "{APP_NAME}"', config)
        self.assertIn(f'#define MyBrandFullName "{BRAND_FULL_NAME}"', config)
        self.assertIn(f'#define MyTagline "{TAGLINE}"', config)


if __name__ == "__main__":
    unittest.main()
