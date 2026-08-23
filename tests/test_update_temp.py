from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import update_temp


class UpdateTempTests(unittest.TestCase):
    def test_cleanup_removes_only_dad_image_tool_update_directories(self) -> None:
        with TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            stale = root / "dad-image-tool-update-old"
            stale.mkdir()
            (stale / "partial.exe").write_bytes(b"partial")
            unrelated = root / "other-program-update"
            unrelated.mkdir()

            with patch.object(update_temp.tempfile, "gettempdir", return_value=temp_name):
                update_temp.cleanup_update_temp_dirs()

            self.assertFalse(stale.exists())
            self.assertTrue(unrelated.exists())


if __name__ == "__main__":
    unittest.main()
