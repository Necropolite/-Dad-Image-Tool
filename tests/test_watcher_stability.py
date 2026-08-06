from __future__ import annotations

import watcher_support
from tests.common import DadImageToolTestCase


class WatcherStabilityTests(DadImageToolTestCase):
    def test_partial_download_inside_folder_is_not_ready(self) -> None:
        folder = self.root / "incoming-folder"
        folder.mkdir()
        (folder / "download.crdownload").write_bytes(b"partial")
        self.assertIsNone(watcher_support.item_fingerprint(folder))
