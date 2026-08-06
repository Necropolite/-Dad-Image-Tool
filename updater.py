from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from version import APP_VERSION, GITHUB_REPOSITORY, RELEASE_ASSET_NAME


@dataclass(frozen=True)
class UpdateInfo:
    version: str
    download_url: str
    release_name: str


def _version_tuple(value: str) -> tuple[int, ...]:
    cleaned = value.strip().lower().lstrip("v")
    parts: list[int] = []
    for part in cleaned.split("."):
        digits = "".join(character for character in part if character.isdigit())
        parts.append(int(digits or 0))
    return tuple(parts)


def check_for_update(timeout: int = 12) -> UpdateInfo | None:
    api_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest"
    request = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Dad-Image-Tool-Updater",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.load(response)

    latest = str(data.get("tag_name", "")).strip()
    if not latest or _version_tuple(latest) <= _version_tuple(APP_VERSION):
        return None

    for asset in data.get("assets", []):
        if asset.get("name") == RELEASE_ASSET_NAME:
            return UpdateInfo(
                version=latest.lstrip("v"),
                download_url=str(asset["browser_download_url"]),
                release_name=str(data.get("name") or latest),
            )
    return None


def install_update(info: UpdateInfo) -> None:
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Updates can only be installed from the packaged application.")

    current_exe = Path(sys.executable).resolve()
    temp_dir = Path(tempfile.mkdtemp(prefix="dad-image-tool-update-"))
    downloaded_exe = temp_dir / RELEASE_ASSET_NAME

    request = urllib.request.Request(
        info.download_url,
        headers={"User-Agent": "Dad-Image-Tool-Updater"},
    )
    with urllib.request.urlopen(request, timeout=120) as response, downloaded_exe.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)

    if downloaded_exe.stat().st_size < 1_000_000:
        raise RuntimeError("The downloaded update was incomplete.")

    script = temp_dir / "install-update.cmd"
    script.write_text(
        "@echo off\n"
        "setlocal\n"
        "timeout /t 3 /nobreak >nul\n"
        f'copy /y "{downloaded_exe}" "{current_exe}" >nul\n'
        "if errorlevel 1 (\n"
        '  msg * "Dad Image Tool could not finish the update."\n'
        "  exit /b 1\n"
        ")\n"
        f'start "" "{current_exe}"\n'
        f'rmdir /s /q "{temp_dir}"\n',
        encoding="utf-8",
    )

    creation_flags = 0x08000000 if os.name == "nt" else 0
    subprocess.Popen(
        ["cmd.exe", "/c", str(script)],
        creationflags=creation_flags,
        close_fds=True,
    )
