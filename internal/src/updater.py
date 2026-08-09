from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from version import APP_VERSION, GITHUB_REPOSITORY, SETUP_ASSET_NAME

CHECKSUM_ASSET_NAME = f"{SETUP_ASSET_NAME}.sha256"
MANIFEST_ASSET_NAME = "Dad-Image-Tool-Update.json"
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


def _request(url: str, *, api: bool = False) -> urllib.request.Request:
    headers = {"User-Agent": "Dad-Image-Tool-Updater"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
    else:
        headers["Accept"] = "application/octet-stream"
    return urllib.request.Request(url, headers=headers)


def _open(request: urllib.request.Request, timeout: int, *, direct: bool = False):
    if direct:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        return opener.open(request, timeout=timeout)
    return urllib.request.urlopen(request, timeout=timeout)


def _load_json(url: str, timeout: int, *, api: bool = False, direct: bool = False) -> dict[str, object]:
    with _open(_request(url, api=api), timeout, direct=direct) as response:
        data = json.load(response)
    if not isinstance(data, dict):
        raise RuntimeError("The update service returned an unexpected response.")
    return data


def _info_from_api_release(data: dict[str, object]) -> UpdateInfo | None:
    latest = str(data.get("tag_name", "")).strip()
    if not latest:
        raise RuntimeError("The latest release does not have a version tag.")
    if _version_tuple(latest) <= _version_tuple(APP_VERSION):
        return None

    raw_assets = data.get("assets", [])
    assets = raw_assets if isinstance(raw_assets, list) else []
    asset_urls = {
        str(asset.get("name")): str(asset.get("browser_download_url"))
        for asset in assets
        if isinstance(asset, dict) and asset.get("name") and asset.get("browser_download_url")
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


def _info_from_manifest(data: dict[str, object]) -> UpdateInfo | None:
    latest = str(data.get("version", "")).strip().lstrip("vV")
    if not latest:
        raise RuntimeError("The fallback update manifest does not contain a version.")
    _version_tuple(latest)
    if _version_tuple(latest) <= _version_tuple(APP_VERSION):
        return None

    setup_asset = str(data.get("setup_asset") or SETUP_ASSET_NAME).strip()
    checksum_asset = str(data.get("checksum_asset") or CHECKSUM_ASSET_NAME).strip()
    if setup_asset != SETUP_ASSET_NAME or checksum_asset != CHECKSUM_ASSET_NAME:
        raise RuntimeError("The fallback update manifest contains unexpected asset names.")

    tag = f"v{latest}"
    release_base = f"https://github.com/{GITHUB_REPOSITORY}/releases/download/{tag}"
    return UpdateInfo(
        version=latest,
        download_url=f"{release_base}/{SETUP_ASSET_NAME}",
        checksum_url=f"{release_base}/{CHECKSUM_ASSET_NAME}",
        release_name=str(data.get("release_name") or f"Dad Image Tool {tag}"),
    )


def _check_api_latest(timeout: int, *, direct: bool = False) -> UpdateInfo | None:
    api_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest"
    return _info_from_api_release(_load_json(api_url, timeout, api=True, direct=direct))


def _check_manifest_latest(timeout: int, *, direct: bool = False) -> UpdateInfo | None:
    manifest_url = f"https://github.com/{GITHUB_REPOSITORY}/releases/latest/download/{MANIFEST_ASSET_NAME}"
    return _info_from_manifest(_load_json(manifest_url, timeout, direct=direct))


def check_for_update(timeout: int = 12) -> UpdateInfo | None:
    """Check GitHub through redundant URLs and network paths.

    Normal Windows/environment proxy behavior is tried first. If those attempts
    fail, the updater retries without any auto-detected proxy. This keeps stale
    proxy configuration from stranding an otherwise connected computer.
    """
    attempts = (
        ("GitHub API", _check_api_latest, False),
        ("GitHub release fallback", _check_manifest_latest, False),
        ("GitHub API direct", _check_api_latest, True),
        ("GitHub release fallback direct", _check_manifest_latest, True),
    )
    failures: list[str] = []
    for label, checker, direct in attempts:
        try:
            return checker(timeout, direct=direct)
        except Exception as exc:
            failures.append(f"{label}: {exc}")

    raise RuntimeError("; ".join(failures))


def record_update_error(stage: str, error: BaseException | str) -> None:
    """Keep useful updater diagnostics without exposing technical noise in Dad's UI."""
    try:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            return
        log_path = Path(local_app_data) / "Dad Image Tool" / "update.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().astimezone().isoformat(timespec="seconds")
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{stamp} [{stage}] {error}\n")
    except Exception:
        pass


def _download_once(url: str, destination: Path, timeout: int, *, direct: bool) -> None:
    with _open(_request(url), timeout, direct=direct) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)


def _download(url: str, destination: Path, timeout: int = 120) -> None:
    try:
        _download_once(url, destination, timeout, direct=False)
    except Exception as first_error:
        try:
            destination.unlink(missing_ok=True)
            _download_once(url, destination, timeout, direct=True)
        except Exception as direct_error:
            raise RuntimeError(f"normal connection failed: {first_error}; direct connection failed: {direct_error}") from direct_error


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
