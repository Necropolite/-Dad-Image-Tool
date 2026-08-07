from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import drop_intake


class DropIntakeTests(unittest.TestCase):
    def test_dropped_file_moves_into_watched_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            incoming = root / "incoming"
            source = root / "Downloads" / "case.zip"
            source.parent.mkdir()
            source.write_bytes(b"zip-data")

            with patch.object(drop_intake, "INCOMING", incoming):
                result = drop_intake.queue_paths([source])

            self.assertEqual(result.errors, [])
            self.assertEqual(len(result.queued), 1)
            self.assertFalse(source.exists())
            self.assertTrue((incoming / "case.zip").exists())

    def test_multiple_dropped_items_get_unique_names(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            incoming = root / "incoming"
            first = root / "one" / "photo.jpg"
            second = root / "two" / "photo.jpg"
            first.parent.mkdir()
            second.parent.mkdir()
            first.write_bytes(b"one")
            second.write_bytes(b"two")

            with patch.object(drop_intake, "INCOMING", incoming):
                result = drop_intake.queue_paths([first, second])

            self.assertEqual(result.errors, [])
            self.assertEqual(len(result.queued), 2)
            self.assertEqual(len({path.name for path in result.queued}), 2)
            self.assertTrue(all(path.exists() for path in result.queued))

    def test_partial_download_is_not_moved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            incoming = root / "incoming"
            source = root / "picture.jpg.crdownload"
            source.write_bytes(b"unfinished")

            with patch.object(drop_intake, "INCOMING", incoming):
                result = drop_intake.queue_paths([source])

            self.assertEqual(result.queued, [])
            self.assertEqual(len(result.errors), 1)
            self.assertIn("still downloading", result.errors[0])
            self.assertTrue(source.exists())

    def test_item_already_in_drop_folder_is_left_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            incoming = Path(temp_name) / "incoming"
            incoming.mkdir()
            source = incoming / "photo.png"
            source.write_bytes(b"image")

            with patch.object(drop_intake, "INCOMING", incoming):
                result = drop_intake.queue_paths([source])

            self.assertEqual(result.errors, [])
            self.assertEqual(result.queued, [source])
            self.assertTrue(source.exists())


if __name__ == "__main__":
    unittest.main()
