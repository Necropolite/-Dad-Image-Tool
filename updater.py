from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from version import APP_VERSION, GITHUB_REPOSITORY, RELEASE_ASSET_NAME

CHECKSUM_ASSET_NAME = f"{RELEASE_ASSET_NAME}.sha256"


@dataclass(frozen=True)
class UpdateInfo:
    version: str
    download_url: str
    checksum_url: str
    release_name: str


def _version_tuple(value: str) -> tuple[int, ...]:
    cleaned = value.strip().lower().lstrip("v")
    parts: list[int] = []
    for part in cleaned.split("."):
        digits = "".join(character for character in part if character.isdigit())
        parts.append(int(digits or 0))
    return tuple(parts)


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
    if not latest or _version_tuple(latest) <= _version_tuple(APP_VERSION):
        return None

    asset_urls = {
        str(asset.get("name")): str(asset.get("browser_download_url"))
        for asset in data.get("assets", [])
        if asset.get("name") and asset.get("browser_download_url")
    }
    executable_url = asset_urls.get(RELEASE_ASSET_NAME)
    checksum_url = asset_urls.get(CHECKSUM_ASSET_NAME)
    if not executable_url or not checksum_url:
        return None

    return UpdateInfo(
        version=latest.lstrip("v"),
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


def install_update(info: UpdateInfo) -> None:
    if os.name != "nt" or not getattr(sys, "frozen", False):
        raise RuntimeError("Updates can only be installed from the packaged Windows application.")

    current_exe = Path(sys.executable).resolve()
    temp_dir = Path(tempfile.mkdtemp(prefix="dad-image-tool-update-"))
    downloaded_exe = temp_dir / RELEASE_ASSET_NAME
    checksum_file = temp_dir / CHECKSUM_ASSET_NAME

    _download(info.download_url, downloaded_exe)
    _download(info.checksum_url, checksum_file, timeout=30)

    if downloaded_exe.stat().st_size < 1_000_000:
        raise RuntimeError("The downloaded update was incomplete.")

    expected = checksum_file.read_text(encoding="utf-8").strip().split()[0].lower()
    actual = _sha256(downloaded_exe)
    if len(expected) != 64 or actual != expected:
        raise RuntimeError("The downloaded update could not be verified.")

    script = temp_dir / "install-update.cmd"
    script.write_text(
        "@echo off\n"
        "setlocal\n"
        "for /l %%i in (1,1,30) do (\n"
        f'  copy /y "{downloaded_exe}" "{current_exe}" >nul 2>nul\n'
        "  if not errorlevel 1 goto updated\n"
        "  timeout /t 1 /nobreak >nul\n"
        ")\n"
        'msg * "Dad Image Tool could not finish the update. The current version was left unchanged."\n'
        "exit /b 1\n"
        ":updated\n"
        f'start "" "{current_exe}"\n'
        "timeout /t 2 /nobreak >nul\n"
        f'rmdir /s /q "{temp_dir}"\n',
        encoding="utf-8",
    )

    subprocess.Popen(
        ["cmd.exe", "/c", str(script)],
        creationflags=0x08000000,
        close_fds=True,
    )
