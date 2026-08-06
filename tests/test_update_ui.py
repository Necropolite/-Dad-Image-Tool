from __future__ import annotations

import unittest
from unittest import mock

import update_ui


class _Status:
    def config(self, **_kwargs) -> None:
        return


class _UpdateStub(update_ui.UpdateMixin):
    def __init__(self) -> None:
        self.busy = True
        self.update_check_running = False
        self.update_install_running = False
        self.pending_update = None
        self.status = _Status()
        self.scheduled: list[tuple[int, object]] = []

    def after(self, delay: int, callback) -> None:
        self.scheduled.append((delay, callback))


class UpdateUiTests(unittest.TestCase):
    def test_manual_update_check_waits_until_processing_finishes(self) -> None:
        window = _UpdateStub()
        with (
            mock.patch.object(update_ui.messagebox, "showinfo") as showinfo,
            mock.patch.object(update_ui.threading, "Thread") as thread,
        ):
            window.check_for_updates(silent=False)
        showinfo.assert_called_once()
        thread.assert_not_called()
        self.assertEqual(window.scheduled, [])

    def test_silent_update_check_is_rescheduled_when_processing(self) -> None:
        window = _UpdateStub()
        with (
            mock.patch.object(update_ui.messagebox, "showinfo") as showinfo,
            mock.patch.object(update_ui.threading, "Thread") as thread,
        ):
            window.check_for_updates(silent=True)
        showinfo.assert_not_called()
        thread.assert_not_called()
        self.assertEqual(len(window.scheduled), 1)
        self.assertEqual(window.scheduled[0][0], 15_000)
