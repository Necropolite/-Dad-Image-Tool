from __future__ import annotations

import unittest
from unittest.mock import patch

import updater


class UpdaterTests(unittest.TestCase):
    def test_version_comparison_is_strict(self) -> None:
        self.assertLess(updater._version_tuple("v0.2.0"), updater._version_tuple("0.2.1"))
        with self.assertRaises(ValueError):
            updater._version_tuple("0.2.1-beta")

    def test_updates_use_setup_program_checksum_and_manifest(self) -> None:
        self.assertEqual(updater.CHECKSUM_ASSET_NAME, "Dad-Image-Tool-Setup.exe.sha256")
        self.assertEqual(updater.MANIFEST_ASSET_NAME, "Dad-Image-Tool-Update.json")

    def test_manifest_builds_version_pinned_download_urls(self) -> None:
        info = updater._info_from_manifest(
            {
                "version": "9.9.9",
                "release_name": "Dad Image Tool v9.9.9",
                "setup_asset": "Dad-Image-Tool-Setup.exe",
                "checksum_asset": "Dad-Image-Tool-Setup.exe.sha256",
            }
        )

        self.assertIsNotNone(info)
        assert info is not None
        self.assertEqual(info.version, "9.9.9")
        self.assertIn("/releases/download/v9.9.9/Dad-Image-Tool-Setup.exe", info.download_url)
        self.assertIn("/releases/download/v9.9.9/Dad-Image-Tool-Setup.exe.sha256", info.checksum_url)

    def test_api_failure_uses_release_manifest_fallback(self) -> None:
        expected = updater.UpdateInfo(
            version="9.9.9",
            download_url="https://example.invalid/setup.exe",
            checksum_url="https://example.invalid/setup.sha256",
            release_name="Dad Image Tool v9.9.9",
        )
        with (
            patch.object(updater, "_check_api_latest", side_effect=OSError("api blocked")),
            patch.object(updater, "_check_manifest_latest", return_value=expected) as fallback,
        ):
            result = updater.check_for_update(timeout=1)

        self.assertEqual(result, expected)
        fallback.assert_called_once_with(1)

    def test_successful_api_check_does_not_use_fallback(self) -> None:
        expected = updater.UpdateInfo(
            version="9.9.9",
            download_url="https://example.invalid/setup.exe",
            checksum_url="https://example.invalid/setup.sha256",
            release_name="Dad Image Tool v9.9.9",
        )
        with (
            patch.object(updater, "_check_api_latest", return_value=expected),
            patch.object(updater, "_check_manifest_latest") as fallback,
        ):
            result = updater.check_for_update(timeout=1)

        self.assertEqual(result, expected)
        fallback.assert_not_called()

    def test_both_update_channels_report_failure(self) -> None:
        with (
            patch.object(updater, "_check_api_latest", side_effect=OSError("api blocked")),
            patch.object(updater, "_check_manifest_latest", side_effect=OSError("fallback blocked")),
        ):
            with self.assertRaisesRegex(RuntimeError, "GitHub API.*GitHub release fallback"):
                updater.check_for_update(timeout=1)


if __name__ == "__main__":
    unittest.main()
