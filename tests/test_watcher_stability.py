from __future__ import annotations

from unittest.mock import patch

import watcher_support
from tests.common import DadImageToolTestCase


class WatcherStabilityTests(DadImageToolTestCase):
    def test_partial_download_inside_folder_is_not_ready(self) -> None:
        folder = self.root / "incoming-folder"
        folder.mkdir()
        (folder / "download.crdownload").write_bytes(b"partial")
        self.assertIsNone(watcher_support.item_fingerprint(folder))

    def test_closed_file_passes_readiness_probe(self) -> None:
        source = self.root / "ready.jpg"
        source.write_bytes(b"complete")
        self.assertTrue(watcher_support.item_ready_for_processing(source))

    def test_unavailable_file_blocks_whole_source(self) -> None:
        folder = self.root / "incoming-folder"
        folder.mkdir()
        (folder / "one.jpg").write_bytes(b"one")
        (folder / "two.jpg").write_bytes(b"two")

        with patch.object(watcher_support, "_file_ready_for_processing", return_value=False):
            self.assertFalse(watcher_support.item_ready_for_processing(folder))
