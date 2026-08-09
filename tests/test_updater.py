from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
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
        fallback.assert_called_once_with(1, direct=False)

    def test_successful_api_check_does_not_use_fallback(self) -> None:
        expected = updater.UpdateInfo(
            version="9.9.9",
            download_url="https://example.invalid/setup.exe",
            checksum_url="https://example.invalid/setup.sha256",
            release_name="Dad Image Tool v9.9.9",
        )
        with (
            patch.object(updater, "_check_api_latest", return_value=expected) as api,
            patch.object(updater, "_check_manifest_latest") as manifest,
            patch.object(updater, "_check_api_latest_curl") as curl_api,
        ):
            result = updater.check_for_update(timeout=1)

        self.assertEqual(result, expected)
        api.assert_called_once_with(1, direct=False)
        manifest.assert_not_called()
        curl_api.assert_not_called()

    def test_proxy_aware_failures_retry_direct(self) -> None:
        expected = updater.UpdateInfo(
            version="9.9.9",
            download_url="https://example.invalid/setup.exe",
            checksum_url="https://example.invalid/setup.sha256",
            release_name="Dad Image Tool v9.9.9",
        )

        def api_check(timeout: int, *, direct: bool = False):
            if not direct:
                raise OSError("proxy path blocked")
            return expected

        with (
            patch.object(updater, "_check_api_latest", side_effect=api_check) as api,
            patch.object(updater, "_check_manifest_latest", side_effect=OSError("manifest blocked")) as manifest,
            patch.object(updater, "_check_api_latest_curl") as curl_api,
        ):
            result = updater.check_for_update(timeout=1)

        self.assertEqual(result, expected)
        self.assertEqual(api.call_count, 2)
        manifest.assert_called_once_with(1, direct=False)
        curl_api.assert_not_called()

    def test_python_network_failures_use_windows_curl(self) -> None:
        expected = updater.UpdateInfo(
            version="9.9.9",
            download_url="https://example.invalid/setup.exe",
            checksum_url="https://example.invalid/setup.sha256",
            release_name="Dad Image Tool v9.9.9",
        )
        with (
            patch.object(updater, "_check_api_latest", side_effect=OSError("python api failed")),
            patch.object(updater, "_check_manifest_latest", side_effect=OSError("python manifest failed")),
            patch.object(updater, "_check_api_latest_curl", return_value=expected) as curl_api,
            patch.object(updater, "_check_manifest_latest_curl") as curl_manifest,
        ):
            result = updater.check_for_update(timeout=1)

        self.assertEqual(result, expected)
        curl_api.assert_called_once_with(1)
        curl_manifest.assert_not_called()

    def test_all_update_channels_report_failure(self) -> None:
        with (
            patch.object(updater, "_check_api_latest", side_effect=OSError("api blocked")),
            patch.object(updater, "_check_manifest_latest", side_effect=OSError("fallback blocked")),
            patch.object(updater, "_check_api_latest_curl", side_effect=OSError("curl api blocked")),
            patch.object(updater, "_check_manifest_latest_curl", side_effect=OSError("curl fallback blocked")),
        ):
            with self.assertRaisesRegex(RuntimeError, "GitHub API.*Windows curl release fallback"):
                updater.check_for_update(timeout=1)

    def test_download_retries_without_proxy(self) -> None:
        with TemporaryDirectory() as temp_name:
            target = Path(temp_name) / "download.bin"

            def fake_download(url: str, destination: Path, timeout: int, *, direct: bool) -> None:
                if not direct:
                    destination.write_bytes(b"partial")
                    raise OSError("proxy failed")
                destination.write_bytes(b"complete")

            with (
                patch.object(updater, "_download_once", side_effect=fake_download) as download_once,
                patch.object(updater, "_download_with_curl") as curl_download,
            ):
                updater._download("https://example.invalid/file", target, timeout=1)

            self.assertEqual(target.read_bytes(), b"complete")
            self.assertEqual(download_once.call_count, 2)
            curl_download.assert_not_called()

    def test_download_uses_curl_after_python_network_failures(self) -> None:
        with TemporaryDirectory() as temp_name:
            target = Path(temp_name) / "download.bin"

            def fake_curl(url: str, destination: Path, timeout: int) -> None:
                destination.write_bytes(b"curl complete")

            with (
                patch.object(updater, "_download_once", side_effect=OSError("python failed")) as download_once,
                patch.object(updater, "_download_with_curl", side_effect=fake_curl) as curl_download,
            ):
                updater._download("https://example.invalid/file", target, timeout=1)

            self.assertEqual(target.read_bytes(), b"curl complete")
            self.assertEqual(download_once.call_count, 2)
            curl_download.assert_called_once_with("https://example.invalid/file", target, 1)


if __name__ == "__main__":
    unittest.main()
