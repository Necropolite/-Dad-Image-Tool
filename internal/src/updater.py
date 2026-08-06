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

from version import APP_VERSION, GITHUB_REPOSITORY, RELEASE_ASSET_NAME

CHECKSUM_ASSET_NAME = f"{RELEASE_ASSET_NAME}.sha256"
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
            "User-Agent": "Dad-Image-Tool-Updater",
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



def cleanup_stale_update_files() -> None:
    if os.name != "nt" or not getattr(sys, "frozen", False):
        return
    current_exe = Path(sys.executable).resolve()
    for stale_path in (
        current_exe.with_name(f"{current_exe.name}.update"),
        current_exe.with_name(f"{current_exe.name}.backup"),
    ):
        try:
            stale_path.unlink()
        except OSError:
            pass


def install_update(info: UpdateInfo) -> None:
    if os.name != "nt" or not getattr(sys, "frozen", False):
        raise RuntimeError("Updates can only be installed from the packaged Windows application.")

    current_exe = Path(sys.executable).resolve()
    staged_exe = current_exe.with_name(f"{current_exe.name}.update")
    backup_exe = current_exe.with_name(f"{current_exe.name}.backup")
    temp_dir = Path(tempfile.mkdtemp(prefix="dad-image-tool-update-"))
    downloaded_exe = temp_dir / RELEASE_ASSET_NAME
    checksum_file = temp_dir / CHECKSUM_ASSET_NAME

    _download(info.download_url, downloaded_exe)
    _download(info.checksum_url, checksum_file, timeout=30)

    if downloaded_exe.stat().st_size < 1_000_000:
        raise RuntimeError("The downloaded update was incomplete.")

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
        staged_exe.unlink(missing_ok=True)
        raise RuntimeError("The staged update could not be verified.")

    script = temp_dir / "install-update.cmd"
    script.write_text(
        "@echo off\n"
        "setlocal\n"
        f'set "CURRENT={current_exe}"\n'
        f'set "STAGED={staged_exe}"\n'
        f'set "BACKUP={backup_exe}"\n'
        "for /l %%i in (1,1,30) do (\n"
        "  move /y \"%CURRENT%\" \"%BACKUP%\" >nul 2>nul\n"
        "  if not errorlevel 1 goto install\n"
        "  timeout /t 1 /nobreak >nul\n"
        ")\n"
        "goto unchanged\n"
        ":install\n"
        "move /y \"%STAGED%\" \"%CURRENT%\" >nul 2>nul\n"
        "if errorlevel 1 goto restore\n"
        "start \"\" \"%CURRENT%\"\n"
        "if errorlevel 1 goto restore_after_start\n"
        "goto cleanup\n"
        ":restore_after_start\n"
        "del /q \"%CURRENT%\" >nul 2>nul\n"
        "move /y \"%BACKUP%\" \"%CURRENT%\" >nul 2>nul\n"
        "start \"\" \"%CURRENT%\"\n"
        "powershell -NoProfile -Command \"Add-Type -AssemblyName PresentationFramework; "
        "[System.Windows.MessageBox]::Show('Dad Image Tool could not start the new version. The previous version was restored.','Dad Image Tool')\"\n"
        "goto cleanup\n"
        ":restore\n"
        "move /y \"%BACKUP%\" \"%CURRENT%\" >nul 2>nul\n"
        "start \"\" \"%CURRENT%\"\n"
        "powershell -NoProfile -Command \"Add-Type -AssemblyName PresentationFramework; "
        "[System.Windows.MessageBox]::Show('Dad Image Tool could not finish the update. The previous version was restored.','Dad Image Tool')\"\n"
        "goto cleanup\n"
        ":unchanged\n"
        "start \"\" \"%CURRENT%\"\n"
        "powershell -NoProfile -Command \"Add-Type -AssemblyName PresentationFramework; "
        "[System.Windows.MessageBox]::Show('Dad Image Tool could not replace the current version. The current version was left unchanged.','Dad Image Tool')\"\n"
        ":cleanup\n"
        "del /q \"%STAGED%\" >nul 2>nul\n"
        f'del /q "{downloaded_exe}" "{checksum_file}" >nul 2>nul\n'
        "del /q \"%~f0\" >nul 2>nul\n",
        encoding="utf-8",
    )

    subprocess.Popen(
        ["cmd.exe", "/d", "/c", str(script)],
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
        close_fds=True,
    )
