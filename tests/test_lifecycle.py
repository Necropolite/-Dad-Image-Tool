from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import watcher


class _Status:
    def __init__(self) -> None:
        self.text = ""

    def config(self, *, text: str) -> None:
        self.text = text


class _Progress:
    def __init__(self) -> None:
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True


class _WindowStub:
    def __init__(self, *, busy: bool = False, updating: bool = False) -> None:
        self.busy = busy
        self.update_install_running = updating
        self.close_when_idle = False
        self.status = _Status()
        self.progress = _Progress()
        self.destroyed = False
        self.observations = {}
        self.blocked_items = {}

    def destroy(self) -> None:
        self.destroyed = True

    def after(self, _delay: int, callback) -> None:
        callback()

    def offer_pending_update(self) -> None:
        raise AssertionError("A pending update must not be offered while closing.")


class LifecycleTests(unittest.TestCase):
    def test_close_waits_for_active_processing(self) -> None:
        window = _WindowStub(busy=True)
        watcher.FolderWatcher.request_close(window)
        self.assertTrue(window.close_when_idle)
        self.assertFalse(window.destroyed)
        self.assertIn("Finishing", window.status.text)

    def test_idle_window_closes_immediately(self) -> None:
        window = _WindowStub()
        watcher.FolderWatcher.request_close(window)
        self.assertTrue(window.destroyed)

    def test_window_cannot_close_during_update_install(self) -> None:
        window = _WindowStub(updating=True)
        with mock.patch.object(watcher.messagebox, "showinfo") as showinfo:
            watcher.FolderWatcher.request_close(window)
        self.assertFalse(window.destroyed)
        showinfo.assert_called_once()

    def test_close_after_processing_skips_new_windows_and_dialogs(self) -> None:
        window = _WindowStub()
        window.close_when_idle = True
        summary = watcher.ProcessingSummary(
            converted=1,
            attention_items=1,
            outputs=[Path("finished")],
        )
        with (
            mock.patch.object(watcher.app, "open_path") as open_path,
            mock.patch.object(watcher.messagebox, "showwarning") as warning,
        ):
            watcher.FolderWatcher._finish(window, summary)
        self.assertTrue(window.destroyed)
        self.assertTrue(window.progress.stopped)
        open_path.assert_not_called()
        warning.assert_not_called()

    def test_unexpected_failure_blocks_unchanged_source_from_retrying(self) -> None:
        window = _WindowStub()
        with tempfile.TemporaryDirectory() as temp_name:
            source = Path(temp_name) / "source.zip"
            source.write_bytes(b"data")
            with mock.patch.object(watcher.messagebox, "showerror") as showerror:
                watcher.FolderWatcher._finish_processing_error(window, [source], "unexpected")
        self.assertIn(source, window.blocked_items)
        showerror.assert_called_once()


class RuntimeFolderTests(unittest.TestCase):
    def test_runtime_folders_are_recreated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            folders = [root / name for name in ("incoming", "finished", "archive", "attention")]
            with (
                mock.patch.object(watcher, "INCOMING", folders[0]),
                mock.patch.object(watcher, "FINISHED", folders[1]),
                mock.patch.object(watcher, "ARCHIVE", folders[2]),
                mock.patch.object(watcher, "NEEDS_ATTENTION", folders[3]),
            ):
                watcher.FolderWatcher._make_folders(object())
            self.assertTrue(all(folder.is_dir() for folder in folders))
