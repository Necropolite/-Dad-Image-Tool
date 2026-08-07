from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

import ui_assets


class UiAssetTests(unittest.TestCase):
    def test_windows_icon_is_generated_from_embedded_horse_asset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            icon_path = ui_assets.write_windows_icon(Path(temp_name) / "Dad-Image-Tool.ico")
            self.assertTrue(icon_path.exists())
            self.assertGreater(icon_path.stat().st_size, 1000)

            with Image.open(icon_path) as icon:
                self.assertEqual(icon.format, "ICO")
                self.assertEqual(icon.size, (256, 256))


if __name__ == "__main__":
    unittest.main()
