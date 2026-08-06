from __future__ import annotations

import watcher_support
from tests.common import DadImageToolTestCase


class WatcherStabilityTests(DadImageToolTestCase):
    def test_recent_item_is_not_old_enough(self) -> None:
        fingerprint = watcher_support.ItemFingerprint(10, 95_000_000_000, 1)
        self.assertFalse(watcher_support.is_old_enough(fingerprint, now_ns=100_000_000_000))

    def test_older_item_is_old_enough(self) -> None:
        fingerprint = watcher_support.ItemFingerprint(10, 80_000_000_000, 1)
        self.assertTrue(watcher_support.is_old_enough(fingerprint, now_ns=100_000_000_000))

    def test_partial_download_inside_folder_is_not_ready(self) -> None:
        folder = self.root / "incoming-folder"
        folder.mkdir()
        (folder / "download.crdownload").write_bytes(b"partial")
        self.assertIsNone(watcher_support.item_fingerprint(folder))

    def test_linked_folder_fingerprint_does_not_scan_target(self) -> None:
        import os

        target = self.root / "target"
        target.mkdir()
        (target / "large.bin").write_bytes(b"x" * 100)
        link = self.root / "link"
        try:
            os.symlink(target, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Directory links are not available on this system")

        fingerprint = watcher_support.item_fingerprint(link)
        self.assertEqual(fingerprint.total_bytes, 0)
        self.assertEqual(fingerprint.file_count, 1)

    def test_link_inside_folder_is_not_followed(self) -> None:
        import os

        folder = self.root / "incoming-folder"
        folder.mkdir()
        target = self.root / "outside"
        target.mkdir()
        (target / "large.bin").write_bytes(b"x" * 100)
        link = folder / "linked"
        try:
            os.symlink(target, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Directory links are not available on this system")

        fingerprint = watcher_support.item_fingerprint(folder)
        self.assertEqual(fingerprint.total_bytes, 0)
        self.assertEqual(fingerprint.file_count, 1)
