from __future__ import annotations

import queue
import zipfile
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

    def _paths(self):
        incoming = self.root / "Drop Client Pictures Here"
        finished = self.root / "Finished"
        archive = self.root / "Originals Archive"
        attention = self.root / "Needs Attention"
        incoming.mkdir(exist_ok=True)
        return incoming, finished, archive, attention

    def _process_watched(self, items):
        incoming, finished, archive, attention = self._paths()
        with (
            mock.patch.object(watcher_processing, "APP_ROOT", self.root),
            mock.patch.object(watcher_processing, "FINISHED", finished),
            mock.patch.object(watcher_processing, "ARCHIVE", archive),
            mock.patch.object(watcher_processing, "NEEDS_ATTENTION", attention),
        ):
            summary = watcher_processing.process_sources(self._worker(), items)
        return summary, incoming, finished, archive, attention

    def test_successful_and_failed_sources_are_independent(self) -> None:
        incoming, _finished, _archive, _attention = self._paths()
        valid = self.make_image(incoming / "valid.png")
        broken = incoming / "broken.zip"
        broken.write_bytes(b"not a zip")

        summary, _incoming, _finished, archive, attention = self._process_watched([valid, broken])

        self.assertEqual(summary.converted, 1)
        self.assertEqual(summary.attention_items, 1)
        self.assertEqual(len(summary.outputs), 1)
        self.assertTrue((summary.outputs[0] / "valid.jpg").exists())
        self.assertTrue((archive / "valid.png").exists())
        self.assertTrue((attention / "broken.zip").exists())
        self.assertEqual(len(history.load_history(self.root)), 2)

    def test_files_dropped_together_share_one_finished_folder(self) -> None:
        incoming, _finished, _archive, _attention = self._paths()
        first = self.make_image(incoming / "first.jpg", image_format="JPEG")
        second = self.make_image(incoming / "second.jpg", image_format="JPEG")

        summary, _incoming, _finished, archive, _attention = self._process_watched([first, second])

        self.assertEqual(summary.converted, 2)
        self.assertEqual(summary.attention_items, 0)
        self.assertEqual(len(summary.outputs), 1)
        output = summary.outputs[0]
        self.assertTrue((output / "first.jpg").exists())
        self.assertTrue((output / "second.jpg").exists())
        self.assertTrue((archive / "first.jpg").exists())
        self.assertTrue((archive / "second.jpg").exists())

    def test_zip_dropped_directly_into_watched_folder_is_processed(self) -> None:
        incoming, _finished, _archive, _attention = self._paths()
        first = self.make_image(self.root / "source" / "front.jpg", image_format="JPEG")
        second = self.make_image(self.root / "source" / "side.jpg", image_format="JPEG")
        dropped_zip = incoming / "client-pictures.zip"
        with zipfile.ZipFile(dropped_zip, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(first, arcname="front.jpg")
            zip_file.write(second, arcname="nested/side.jpg")

        summary, _incoming, _finished, archive, attention = self._process_watched([dropped_zip])

        self.assertEqual(summary.converted, 2)
        self.assertEqual(summary.attention_items, 0)
        self.assertEqual(len(summary.outputs), 1)
        output = summary.outputs[0]
        self.assertTrue((output / "client-pictures" / "front.jpg").exists())
        self.assertTrue((output / "client-pictures" / "nested" / "side.jpg").exists())
        self.assertTrue((archive / "client-pictures.zip").exists())
        self.assertFalse((attention / "client-pictures.zip").exists())

    def test_docx_dropped_directly_into_watched_folder_is_processed(self) -> None:
        incoming, _finished, _archive, _attention = self._paths()
        picture = self.make_image(self.root / "source" / "hoof.jpg", image_format="JPEG")
        document = self.make_docx_with_images(incoming / "consultant-notes.docx", [picture])

        summary, _incoming, _finished, archive, attention = self._process_watched([document])

        self.assertEqual(summary.converted, 1)
        self.assertEqual(summary.attention_items, 0)
        self.assertTrue((summary.outputs[0] / "consultant-notes" / "001-image1.jpg").exists())
        self.assertTrue((archive / "consultant-notes.docx").exists())
        self.assertFalse((attention / "consultant-notes.docx").exists())

    def test_pdf_dropped_directly_into_watched_folder_is_processed(self) -> None:
        incoming, _finished, _archive, _attention = self._paths()
        picture = self.make_image(self.root / "source" / "hoof.jpg", image_format="JPEG")
        document = self.make_pdf_with_images(incoming / "consultant-report.pdf", [picture])

        summary, _incoming, _finished, archive, attention = self._process_watched([document])

        self.assertEqual(summary.converted, 1)
        self.assertEqual(summary.attention_items, 0)
        self.assertTrue((summary.outputs[0] / "consultant-report" / "001-page-1.jpg").exists())
        self.assertTrue((archive / "consultant-report.pdf").exists())
        self.assertFalse((attention / "consultant-report.pdf").exists())
