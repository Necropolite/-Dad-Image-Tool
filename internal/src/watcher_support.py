from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

import app

IGNORED_SUFFIXES = {
    ".crdownload",
    ".download",
    ".filepart",
    ".opdownload",
    ".part",
    ".partial",
    ".tmp",
}
STABLE_CHECKS_REQUIRED = 3
_INSTANCE_MUTEX_HANDLE: int | None = None


def pictures_folder() -> Path:
    if os.name == "nt":
        try:
            import winreg

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                value, _kind = winreg.QueryValueEx(key, "My Pictures")
            return Path(os.path.expandvars(str(value)))
        except (OSError, ImportError):
            pass
    return Path.home() / "Pictures"


APP_ROOT = pictures_folder() / "Dad Image Tool"
INCOMING = APP_ROOT / "Drop Client Pictures Here"
FINISHED = APP_ROOT / "Finished"
ARCHIVE = APP_ROOT / "Originals Archive"
NEEDS_ATTENTION = APP_ROOT / "Needs Attention"


@dataclass(frozen=True)
class ItemFingerprint:
    total_bytes: int
    newest_mtime_ns: int
    file_count: int


@dataclass
class Observation:
    fingerprint: ItemFingerprint
    unchanged_checks: int = 0


def item_fingerprint(path: Path) -> ItemFingerprint | None:
    if path.is_file():
        if path.suffix.lower() in IGNORED_SUFFIXES:
            return None
        details = path.stat()
        return ItemFingerprint(details.st_size, details.st_mtime_ns, 1)

    root_details = path.stat()
    total_bytes = 0
    newest_mtime_ns = root_details.st_mtime_ns
    file_count = 0
    for child in path.rglob("*"):
        if not child.is_file():
            continue
        if child.suffix.lower() in IGNORED_SUFFIXES:
            return None
        details = child.stat()
        total_bytes += details.st_size
        newest_mtime_ns = max(newest_mtime_ns, details.st_mtime_ns)
        file_count += 1
    return ItemFingerprint(total_bytes, newest_mtime_ns, file_count)


def _file_ready_for_processing(path: Path) -> bool:
    """Return True only when a source file can be safely consumed now.

    On Windows, Dad Image Tool requests an exclusive read handle. Active copy or
    download operations normally retain a write handle, so this avoids treating
    a briefly paused transfer as complete merely because size/mtime stopped
    changing for a few scans.
    """
    if path.suffix.lower() in IGNORED_SUFFIXES:
        return False

    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateFileW.argtypes = (
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        )
        kernel32.CreateFileW.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel32.CloseHandle.restype = wintypes.BOOL

        generic_read = 0x80000000
        open_existing = 3
        file_attribute_normal = 0x80
        invalid_handle = ctypes.c_void_p(-1).value
        handle = kernel32.CreateFileW(
            str(path),
            generic_read,
            0,
            None,
            open_existing,
            file_attribute_normal,
            None,
        )
        if handle in (None, invalid_handle):
            return False
        kernel32.CloseHandle(handle)
        return True

    try:
        with path.open("rb") as source:
            for _chunk in iter(lambda: source.read(1024 * 1024), b""):
                pass
        return True
    except OSError:
        return False


def item_ready_for_processing(path: Path) -> bool:
    """Probe every source file after the fingerprint stability window passes."""
    try:
        if path.is_file():
            return _file_ready_for_processing(path)

        for child in path.rglob("*"):
            if child.is_file() and not _file_ready_for_processing(child):
                return False
        return True
    except OSError:
        return False


def move_target(source: Path, folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    destination = app.unique_path(folder / source.name, is_dir=source.is_dir())
    return Path(shutil.move(str(source), str(destination)))


def acquire_single_instance() -> bool:
    global _INSTANCE_MUTEX_HANDLE
    if os.name != "nt":
        return True

    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.argtypes = (ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR)
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL

    handle = kernel32.CreateMutexW(None, False, "Local\\DadImageTool-WatchedFolder")
    if not handle:
        return True
    if kernel32.GetLastError() == 183:
        kernel32.CloseHandle(handle)
        return False
    _INSTANCE_MUTEX_HANDLE = int(handle)
    return True
