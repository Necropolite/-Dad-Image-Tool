from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from version import APP_BRAND_TITLE, APP_NAME, APP_VERSION, GITHUB_REPOSITORY, RELEASE_ASSET_NAME

CHECKSUM_ASSET_NAME = f"{RELEASE_ASSET_NAME}.sha256"
STARTUP_MARKER_ENV = "DAD_IMAGE_TOOL_STARTUP_MARKER"
_VERSION_PATTERN = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$", flags=re.IGNORECASE)


@dataclass(frozen=True)
class UpdateInfo:
    version: str
    download_url: str
    checksum_url: str
    release_name: str


def _version_tuple(value: str) -> tuple[int, int, int]:
    match = _VERSION_PATTERN.fullmatch(value.strip())
    if match is None:
        raise ValueError(f"Unsupported version number: {value}")
    return tuple(int(part) for part in match.groups())


def _request(url: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "DAD-Dad-Image-Tool-Updater",
        },
    )


def check_for_update(timeout: int = 12) -> UpdateInfo | None:
    api_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest"
    with urllib.request.urlopen(_request(api_url), timeout=timeout) as response:
        data = json.load(response)

    latest = str(data.get("tag_name", "")).strip()
    if not latest:
        raise RuntimeError("The latest release does not have a version tag.")
    if _version_tuple(latest) <= _version_tuple(APP_VERSION):
        return None

    asset_urls = {
        str(asset.get("name")): str(asset.get("browser_download_url"))
        for asset in data.get("assets", [])
        if asset.get("name") and asset.get("browser_download_url")
    }
    executable_url = asset_urls.get(RELEASE_ASSET_NAME)
    checksum_url = asset_urls.get(CHECKSUM_ASSET_NAME)
    if not executable_url or not checksum_url:
        raise RuntimeError("The new release is missing its executable or checksum file.")

    return UpdateInfo(
        version=latest.lstrip("vV"),
        download_url=executable_url,
        checksum_url=checksum_url,
        release_name=str(data.get("name") or latest),
    )


def _download(url: str, destination: Path, timeout: int = 120) -> None:
    with urllib.request.urlopen(_request(url), timeout=timeout) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_windows_executable(path: Path) -> bool:
    with path.open("rb") as file:
        return file.read(2) == b"MZ"


def _installed_paths() -> tuple[Path, Path, Path]:
    current_exe = Path(sys.executable).resolve()
    staged_exe = current_exe.with_name(f"{current_exe.name}.update")
    backup_exe = current_exe.with_name(f"{current_exe.name}.backup")
    return current_exe, staged_exe, backup_exe


def _startup_marker_path(value: str) -> Path | None:
    try:
        marker = Path(value).resolve(strict=False)
        temp_root = Path(tempfile.gettempdir()).resolve(strict=False)
    except OSError:
        return None
    if marker == temp_root or temp_root not in marker.parents:
        return None
    return marker


def confirm_startup() -> bool:
    """Confirm that the packaged app reached a usable initialized window."""
    marker_value = os.environ.pop(STARTUP_MARKER_ENV, "").strip()
    if marker_value:
        marker = _startup_marker_path(marker_value)
        if marker is None:
            return False
        try:
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text(APP_VERSION, encoding="utf-8")
            return True
        except OSError:
            return False

    cleanup_stale_update_files()
    return True


def _remove_stale_update_files(staged_exe: Path, backup_exe: Path, temp_root: Path) -> None:
    for stale_path in (staged_exe, backup_exe):
        try:
            stale_path.unlink()
        except OSError:
            pass

    for update_dir in temp_root.glob("dad-image-tool-update-*"):
        try:
            update_dir.rmdir()  # Removes only empty directories from completed updates.
        except OSError:
            pass


def cleanup_stale_update_files() -> None:
    if os.name != "nt" or not getattr(sys, "frozen", False):
        return
    _current_exe, staged_exe, backup_exe = _installed_paths()
    _remove_stale_update_files(staged_exe, backup_exe, Path(tempfile.gettempdir()))


def _cmd_value(path: Path) -> str:
    """Escape a path for storage in a quoted CMD environment variable."""
    return str(path).replace("^", "^^").replace("%", "%%")


def _update_script_text(
    current_exe: Path,
    staged_exe: Path,
    backup_exe: Path,
    startup_marker: Path,
    downloaded_exe: Path,
    checksum_file: Path,
) -> str:
    return (
        "@echo off\n"
        "setlocal EnableExtensions\n"
        f'set "CURRENT={_cmd_value(current_exe)}"\n'
        f'set "STAGED={_cmd_value(staged_exe)}"\n'
        f'set "BACKUP={_cmd_value(backup_exe)}"\n'
        f'set "MARKER={_cmd_value(startup_marker)}"\n'
        "del /q \"%MARKER%\" >nul 2>nul\n"
        "for /l %%i in (1,1,30) do (\n"
        "  move /y \"%CURRENT%\" \"%BACKUP%\" >nul 2>nul\n"
        "  if not errorlevel 1 goto install\n"
        "  timeout /t 1 /nobreak >nul\n"
        ")\n"
        "goto unchanged\n"
        ":install\n"
        "move /y \"%STAGED%\" \"%CURRENT%\" >nul 2>nul\n"
        "if errorlevel 1 goto restore\n"
        "set \"DAD_IMAGE_TOOL_STARTUP_MARKER=%MARKER%\"\n"
        "start \"\" \"%CURRENT%\"\n"
        "if errorlevel 1 goto restore_after_start\n"
        "for /l %%i in (1,1,45) do (\n"
        "  if exist \"%MARKER%\" goto success\n"
        "  timeout /t 1 /nobreak >nul\n"
        ")\n"
        "taskkill /im \"Dad Image Tool.exe\" /f >nul 2>nul\n"
        ":restore_after_start\n"
        "del /q \"%CURRENT%\" >nul 2>nul\n"
        "move /y \"%BACKUP%\" \"%CURRENT%\" >nul 2>nul\n"
        "set \"DAD_IMAGE_TOOL_STARTUP_MARKER=\"\n"
        "start \"\" \"%CURRENT%\"\n"
        "powershell -NoProfile -Command \"Add-Type -AssemblyName PresentationFramework; "
        f"[System.Windows.MessageBox]::Show('{APP_NAME} could not start the new version. "
        f"The previous version was restored.','{APP_BRAND_TITLE}')\"\n"
        "goto cleanup\n"
        ":restore\n"
        "move /y \"%BACKUP%\" \"%CURRENT%\" >nul 2>nul\n"
        "set \"DAD_IMAGE_TOOL_STARTUP_MARKER=\"\n"
        "start \"\" \"%CURRENT%\"\n"
        "powershell -NoProfile -Command \"Add-Type -AssemblyName PresentationFramework; "
        f"[System.Windows.MessageBox]::Show('{APP_NAME} could not finish the update. "
        f"The previous version was restored.','{APP_BRAND_TITLE}')\"\n"
        "goto cleanup\n"
        ":unchanged\n"
        "set \"DAD_IMAGE_TOOL_STARTUP_MARKER=\"\n"
        "start \"\" \"%CURRENT%\"\n"
        "powershell -NoProfile -Command \"Add-Type -AssemblyName PresentationFramework; "
        f"[System.Windows.MessageBox]::Show('{APP_NAME} could not replace the current version. "
        f"The current version was left unchanged.','{APP_BRAND_TITLE}')\"\n"
        "goto cleanup\n"
        ":success\n"
        "del /q \"%BACKUP%\" >nul 2>nul\n"
        ":cleanup\n"
        "del /q \"%STAGED%\" \"%MARKER%\" >nul 2>nul\n"
        f'del /q "{_cmd_value(downloaded_exe)}" "{_cmd_value(checksum_file)}" >nul 2>nul\n'
        "del /q \"%~f0\" >nul 2>nul\n"
    )


def install_update(info: UpdateInfo) -> None:
    if os.name != "nt" or not getattr(sys, "frozen", False):
        raise RuntimeError("Updates can only be installed from the packaged Windows application.")

    current_exe, staged_exe, backup_exe = _installed_paths()
    temp_dir = Path(tempfile.mkdtemp(prefix="dad-image-tool-update-"))
    downloaded_exe = temp_dir / RELEASE_ASSET_NAME
    checksum_file = temp_dir / CHECKSUM_ASSET_NAME
    startup_marker = temp_dir / "startup-ok.txt"
    script = temp_dir / "install-update.cmd"

    try:
        _download(info.download_url, downloaded_exe)
        _download(info.checksum_url, checksum_file, timeout=30)

        if downloaded_exe.stat().st_size < 1_000_000 or not _is_windows_executable(downloaded_exe):
            raise RuntimeError("The downloaded update was incomplete or was not a Windows application.")

        checksum_text = checksum_file.read_text(encoding="utf-8").strip().split()
        if not checksum_text:
            raise RuntimeError("The update checksum file was empty.")
        expected = checksum_text[0].lower()
        actual = _sha256(downloaded_exe)
        if len(expected) != 64 or not re.fullmatch(r"[0-9a-f]{64}", expected) or actual != expected:
            raise RuntimeError("The downloaded update could not be verified.")

        for stale_path in (staged_exe, backup_exe):
            try:
                stale_path.unlink()
            except FileNotFoundError:
                pass

        shutil.copy2(downloaded_exe, staged_exe)
        if _sha256(staged_exe) != expected:
            raise RuntimeError("The staged update could not be verified.")

        script.write_text(
            _update_script_text(
                current_exe,
                staged_exe,
                backup_exe,
                startup_marker,
                downloaded_exe,
                checksum_file,
            ),
            encoding="utf-8",
        )

        subprocess.Popen(
            ["cmd.exe", "/d", "/c", str(script)],
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
            close_fds=True,
        )
    except Exception:
        staged_exe.unlink(missing_ok=True)
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
