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

from version import APP_VERSION, GITHUB_REPOSITORY, SETUP_ASSET_NAME

CHECKSUM_ASSET_NAME = f"{SETUP_ASSET_NAME}.sha256"
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
    setup_url = asset_urls.get(SETUP_ASSET_NAME)
    checksum_url = asset_urls.get(CHECKSUM_ASSET_NAME)
    if not setup_url or not checksum_url:
        raise RuntimeError("The new release is missing its setup program or checksum file.")

    return UpdateInfo(
        version=latest.lstrip("vV"),
        download_url=setup_url,
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
    temp_dir = Path(tempfile.mkdtemp(prefix="dad-image-tool-update-"))
    downloaded_setup = temp_dir / SETUP_ASSET_NAME
    checksum_file = temp_dir / CHECKSUM_ASSET_NAME

    _download(info.download_url, downloaded_setup)
    _download(info.checksum_url, checksum_file, timeout=30)

    if downloaded_setup.stat().st_size < 1_000_000:
        raise RuntimeError("The downloaded update was incomplete.")

    checksum_text = checksum_file.read_text(encoding="utf-8").strip().split()
    if not checksum_text:
        raise RuntimeError("The update checksum file was empty.")
    expected = checksum_text[0].lower()
    actual = _sha256(downloaded_setup)
    if len(expected) != 64 or not re.fullmatch(r"[0-9a-f]{64}", expected) or actual != expected:
        raise RuntimeError("The downloaded update could not be verified.")

    script = temp_dir / "install-update.cmd"
    script.write_text(
        "@echo off\n"
        "setlocal\n"
        "timeout /t 2 /nobreak >nul\n"
        f'"{downloaded_setup}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS\n'
        "if errorlevel 1 goto failed\n"
        f'start "" "{current_exe}"\n'
        "goto cleanup\n"
        ":failed\n"
        f'start "" "{current_exe}"\n'
        ":cleanup\n"
        f'del /q "{downloaded_setup}" "{checksum_file}" >nul 2>nul\n'
        "del /q \"%~f0\" >nul 2>nul\n",
        encoding="utf-8",
    )

    subprocess.Popen(
        ["cmd.exe", "/d", "/c", str(script)],
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000),
        close_fds=True,
    )
