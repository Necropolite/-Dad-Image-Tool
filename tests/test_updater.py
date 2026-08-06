from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import updater


class UpdaterTests(unittest.TestCase):
    def test_version_comparison_is_strict(self) -> None:
        self.assertLess(updater._version_tuple("v0.2.1"), updater._version_tuple("0.2.2"))
        with self.assertRaises(ValueError):
            updater._version_tuple("0.2.2-beta")

    def test_confirm_startup_writes_update_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            marker = Path(temp_name) / "started.txt"
            with mock.patch.dict(os.environ, {updater.STARTUP_MARKER_ENV: str(marker)}):
                self.assertTrue(updater.confirm_startup())
                self.assertNotIn(updater.STARTUP_MARKER_ENV, os.environ)
            self.assertEqual(marker.read_text(encoding="utf-8"), "0.2.2")

    def test_startup_marker_outside_temp_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            allowed_temp = root / "allowed"
            outside = root / "outside.txt"
            with (
                mock.patch.object(updater.tempfile, "gettempdir", return_value=str(allowed_temp)),
                mock.patch.dict(os.environ, {updater.STARTUP_MARKER_ENV: str(outside)}),
            ):
                self.assertFalse(updater.confirm_startup())
            self.assertFalse(outside.exists())

    def test_normal_startup_cleans_stale_files(self) -> None:
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch.object(updater, "cleanup_stale_update_files") as cleanup,
        ):
            self.assertTrue(updater.confirm_startup())
        cleanup.assert_called_once_with()

    def test_windows_executable_header_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "app.exe"
            path.write_bytes(b"not an executable")
            self.assertFalse(updater._is_windows_executable(path))
            path.write_bytes(b"MZ" + b"data")
            self.assertTrue(updater._is_windows_executable(path))

    def test_cmd_paths_escape_percent_characters(self) -> None:
        self.assertEqual(
            updater._cmd_value(Path(r"C:\Users\100%Real^Name\Dad Image Tool.exe")),
            r"C:\Users\100%%Real^^Name\Dad Image Tool.exe",
        )

    def test_stale_update_cleanup_removes_only_safe_leftovers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            staged = root / "Dad Image Tool.exe.update"
            backup = root / "Dad Image Tool.exe.backup"
            staged.write_bytes(b"staged")
            backup.write_bytes(b"backup")
            empty_update_dir = root / "dad-image-tool-update-empty"
            active_update_dir = root / "dad-image-tool-update-active"
            empty_update_dir.mkdir()
            active_update_dir.mkdir()
            (active_update_dir / "still-active.txt").write_text("active", encoding="utf-8")

            updater._remove_stale_update_files(staged, backup, root)

            self.assertFalse(staged.exists())
            self.assertFalse(backup.exists())
            self.assertFalse(empty_update_dir.exists())
            self.assertTrue(active_update_dir.exists())

    def test_update_script_waits_for_startup_marker_and_restores_on_failure(self) -> None:
        root = Path(r"C:\Dad Image Tool")
        text = updater._update_script_text(
            root / "Dad Image Tool.exe",
            root / "Dad Image Tool.exe.update",
            root / "Dad Image Tool.exe.backup",
            root / "startup-ok.txt",
            root / "download.exe",
            root / "download.sha256",
        )
        self.assertIn("DAD_IMAGE_TOOL_STARTUP_MARKER", text)
        self.assertIn('if exist "%MARKER%" goto success', text)
        self.assertIn(":restore_after_start", text)
        self.assertIn('move /y "%BACKUP%" "%CURRENT%"', text)
