from __future__ import annotations

import queue
from unittest import mock

import history
import watcher_processing
from tests.common import DadImageToolTestCase


class RoutingTests(DadImageToolTestCase):
    def _worker(self):
        class WorkerStub:
            def __init__(self) -> None:
                self.events = queue.Queue()
                self.blocked_items = {}

            def _send_status(self, _text: str) -> None:
                return

        return WorkerStub()

    def test_successful_and_failed_sources_are_independent(self) -> None:
        incoming = self.root / "Drop Client Pictures Here"
        finished = self.root / "Finished"
        archive = self.root / "Originals Archive"
        attention = self.root / "Needs Attention"
        incoming.mkdir()
        valid = self.make_image(incoming / "valid.png")
        broken = incoming / "broken.zip"
        broken.write_bytes(b"not a zip")

        with (
            mock.patch.object(watcher_processing, "APP_ROOT", self.root),
            mock.patch.object(watcher_processing, "FINISHED", finished),
            mock.patch.object(watcher_processing, "ARCHIVE", archive),
            mock.patch.object(watcher_processing, "NEEDS_ATTENTION", attention),
        ):
            summary = watcher_processing.process_sources(self._worker(), [valid, broken])

        self.assertEqual(summary.converted, 1)
        self.assertEqual(summary.attention_items, 1)
        self.assertEqual(len(summary.outputs), 1)
        self.assertTrue((summary.outputs[0] / "valid.jpg").exists())
        self.assertTrue((archive / "valid.png").exists())
        self.assertTrue((attention / "broken.zip").exists())
        self.assertEqual(len(history.load_history(self.root)), 2)

    def test_files_dropped_together_share_one_finished_folder(self) -> None:
        incoming = self.root / "Drop Client Pictures Here"
        finished = self.root / "Finished"
        archive = self.root / "Originals Archive"
        attention = self.root / "Needs Attention"
        incoming.mkdir()
        first = self.make_image(incoming / "first.jpg", image_format="JPEG")
        second = self.make_image(incoming / "second.jpg", image_format="JPEG")

        with (
            mock.patch.object(watcher_processing, "APP_ROOT", self.root),
            mock.patch.object(watcher_processing, "FINISHED", finished),
            mock.patch.object(watcher_processing, "ARCHIVE", archive),
            mock.patch.object(watcher_processing, "NEEDS_ATTENTION", attention),
        ):
            summary = watcher_processing.process_sources(self._worker(), [first, second])

        self.assertEqual(summary.converted, 2)
        self.assertEqual(summary.attention_items, 0)
        self.assertEqual(len(summary.outputs), 1)
        output = summary.outputs[0]
        self.assertTrue((output / "first.jpg").exists())
        self.assertTrue((output / "second.jpg").exists())
        self.assertTrue((archive / "first.jpg").exists())
        self.assertTrue((archive / "second.jpg").exists())
