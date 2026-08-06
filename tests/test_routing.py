from __future__ import annotations

import queue
from unittest import mock

import history
import watcher_processing
from tests.common import DadImageToolTestCase


class RoutingTests(DadImageToolTestCase):
    def test_successful_and_failed_sources_are_independent(self) -> None:
        incoming = self.root / "Drop Client Pictures Here"
        finished = self.root / "Finished"
        archive = self.root / "Originals Archive"
        attention = self.root / "Needs Attention"
        incoming.mkdir()
        valid = self.make_image(incoming / "valid.png")
        broken = incoming / "broken.zip"
        broken.write_bytes(b"not a zip")

        class WorkerStub:
            def __init__(self) -> None:
                self.events = queue.Queue()
                self.blocked_items = {}

            def _send_status(self, _text: str) -> None:
                return

        with (
            mock.patch.object(watcher_processing, "APP_ROOT", self.root),
            mock.patch.object(watcher_processing, "FINISHED", finished),
            mock.patch.object(watcher_processing, "ARCHIVE", archive),
            mock.patch.object(watcher_processing, "NEEDS_ATTENTION", attention),
        ):
            summary = watcher_processing.process_sources(WorkerStub(), [valid, broken])

        self.assertEqual(summary.converted, 1)
        self.assertEqual(summary.attention_items, 1)
        self.assertTrue((archive / "valid.png").exists())
        self.assertTrue((attention / "broken.zip").exists())
        self.assertEqual(len(history.load_history(self.root)), 2)
