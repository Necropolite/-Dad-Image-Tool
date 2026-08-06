from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import warnings
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable

from PIL import Image, ImageOps, UnidentifiedImageError

try:
    from pillow_heif import register_heif_opener
except ImportError:  # Tests and source inspection can run without optional HEIF support.
    register_heif_opener = None

HEIF_SUPPORT_AVAILABLE = register_heif_opener is not None
if HEIF_SUPPORT_AVAILABLE:
    register_heif_opener()

APP_NAME = "Dad Image Tool"
SUPPORTED_IMAGE_SUFFIXES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".heic",
    ".heif",
    ".tif",
    ".tiff",
    ".bmp",
}
IGNORED_NAMES = {".ds_store", "thumbs.db", "desktop.ini"}
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
WINDOWS_INVALID_PATH_CHARACTERS = frozenset('<>:"|?*')
MAX_NESTED_ZIP_DEPTH = 5
MAX_ARCHIVE_FILES = 10_000
MAX_EXTRACTED_BYTES = 2 * 1024 * 1024 * 1024

StatusCallback = Callable[[str], None]


@dataclass
class JobResult:
    converted: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    output_dir: Path | None = None


@dataclass
class ExtractionBudget:
    files: int = 0
    bytes: int = 0

    def add(self, member: zipfile.ZipInfo) -> None:
        if member.is_dir():
            return
        self.files += 1
        self.bytes += member.file_size
        if self.files > MAX_ARCHIVE_FILES:
            raise ValueError("The ZIP contains too many files to process safely.")
        if self.bytes > MAX_EXTRACTED_BYTES:
            raise ValueError("The ZIP is too large to process safely.")


def process_items(items: Iterable[str], output_root: Path, status_cb: StatusCallback) -> JobResult:
    """Convert local pictures, folders, and ZIP files into one dated output folder."""
    result = JobResult()
    source_items = [str(item) for item in items if str(item).strip()]
    if not source_items:
        result.errors.append("No source item was provided.")
        return result

    output_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dad-image-tool-") as temp_name:
        images = _collect_source_images(source_items, Path(temp_name), status_cb, result)
        if not images and not result.errors:
            result.errors.append("No supported pictures were found.")
        elif images:
            _convert_images(images, output_root, status_cb, result)
    return result


def _collect_source_images(
    source_items: list[str],
    temp_root: Path,
    status_cb: StatusCallback,
    result: JobResult,
) -> list[Path]:
    images: list[Path] = []
    budget = ExtractionBudget()
    for index, raw_item in enumerate(source_items, start=1):
        status_cb(f"Checking item {index} of {len(source_items)}...")
        source = Path(raw_item.strip().strip('"'))
        if not source.exists():
            result.errors.append(f"Could not find {source.name or 'one source item'}.")
            continue
        try:
            found, skipped = collect_images(
                source,
                temp_root / f"item-{index}",
                budget=budget,
                nested_zip_depth=0,
            )
            images.extend(found)
            result.skipped += skipped
        except Exception as exc:
            result.errors.append(f"Could not use {source.name}: {friendly_error(exc)}")
    return images


def _convert_images(
    images: list[Path],
    output_root: Path,
    status_cb: StatusCallback,
    result: JobResult,
) -> None:
    result.output_dir = create_output_dir(output_root)
    for index, image_path in enumerate(images, start=1):
        status_cb(f"Converting picture {index} of {len(images)}...")
        try:
            convert_to_jpeg(image_path, result.output_dir)
            result.converted += 1
        except Exception as exc:
            result.errors.append(f"Could not convert {image_path.name}: {friendly_error(exc)}")

    if result.converted == 0 and result.output_dir is not None:
        try:
            result.output_dir.rmdir()
        except OSError:
            pass
        result.output_dir = None


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def collect_images(
    source: Path,
    extraction_root: Path,
    *,
    budget: ExtractionBudget,
    nested_zip_depth: int,
) -> tuple[list[Path], int]:
    if _is_link_or_junction(source):
        raise ValueError("The folder contains an unsupported shortcut or linked folder.")

    if source.is_dir():
        images: list[Path] = []
        skipped = 0
        for child in sorted(source.iterdir(), key=lambda path: path.name.casefold()):
            if child.name.casefold() in IGNORED_NAMES:
                continue
            child_images, child_skipped = collect_images(
                child,
                extraction_root,
                budget=budget,
                nested_zip_depth=nested_zip_depth,
            )
            images.extend(child_images)
            skipped += child_skipped
        return images, skipped

    suffix = source.suffix.lower()
    if suffix in SUPPORTED_IMAGE_SUFFIXES:
        return [source], 0

    if suffix == ".zip":
        if nested_zip_depth >= MAX_NESTED_ZIP_DEPTH:
            raise ValueError("The ZIP contains too many nested ZIP files.")
        extraction_root.mkdir(parents=True, exist_ok=True)
        destination = unique_path(
            extraction_root / f"unzipped-{sanitize_filename(source.stem)}",
            is_dir=True,
        )
        safe_extract_zip(source, destination, budget=budget)
        return collect_images(
            destination,
            extraction_root,
            budget=budget,
            nested_zip_depth=nested_zip_depth + 1,
        )

    return [], 1


def _validated_zip_parts(member_name: str) -> tuple[str, ...]:
    """Return a Windows-safe relative ZIP path or raise a plain-language error."""
    normalized_name = member_name.replace("\\", "/")
    member_path = PurePosixPath(normalized_name)
    if member_path.is_absolute() or ".." in member_path.parts:
        raise ValueError("The ZIP contains an unsafe file path.")

    parts = tuple(member_path.parts)
    for part in parts:
        if not part or part.rstrip(" .") != part:
            raise ValueError("The ZIP contains a filename Windows cannot use safely.")
        if any(ord(character) < 32 or character in WINDOWS_INVALID_PATH_CHARACTERS for character in part):
            raise ValueError("The ZIP contains a filename Windows cannot use safely.")
        if part.split(".", 1)[0].rstrip(" ").upper() in WINDOWS_RESERVED_NAMES:
            raise ValueError("The ZIP contains a filename reserved by Windows.")
    return parts


def _zip_path_key(parts: tuple[str, ...]) -> str:
    return "/".join(part.casefold() for part in parts)


def _prepare_zip_members(
    zip_file: zipfile.ZipFile,
    destination: Path,
    extraction_budget: ExtractionBudget,
) -> list[tuple[zipfile.ZipInfo, tuple[str, ...]]]:
    root = destination.resolve()
    prepared_members: list[tuple[zipfile.ZipInfo, tuple[str, ...]]] = []
    seen_member_paths: set[str] = set()
    file_paths: set[str] = set()
    directory_paths: set[str] = set()

    for member in zip_file.infolist():
        extraction_budget.add(member)
        if member.flag_bits & 0x1:
            raise ValueError("The ZIP is password protected.")

        unix_mode = (member.external_attr >> 16) & 0o170000
        if unix_mode == stat.S_IFLNK:
            raise ValueError("The ZIP contains an unsupported symbolic link.")

        parts = _validated_zip_parts(member.filename)
        if not parts:
            continue

        key = _zip_path_key(parts)
        parent_keys = {_zip_path_key(parts[:index]) for index in range(1, len(parts))}
        if key in seen_member_paths:
            raise ValueError("The ZIP contains duplicate file paths.")
        if any(parent in file_paths for parent in parent_keys):
            raise ValueError("The ZIP contains conflicting file and folder paths.")

        if member.is_dir():
            if key in file_paths:
                raise ValueError("The ZIP contains conflicting file and folder paths.")
            directory_paths.add(key)
        else:
            if key in file_paths or key in directory_paths:
                raise ValueError("The ZIP contains conflicting file and folder paths.")
            file_paths.add(key)
            directory_paths.update(parent_keys)

        seen_member_paths.add(key)
        target = (destination / Path(*parts)).resolve()
        if target != root and root not in target.parents:
            raise ValueError("The ZIP contains an unsafe file path.")
        prepared_members.append((member, parts))

    return prepared_members


def safe_extract_zip(archive: Path, destination: Path, *, budget: ExtractionBudget | None = None) -> Path:
    destination.mkdir(parents=True, exist_ok=False)
    extraction_budget = budget or ExtractionBudget()

    with zipfile.ZipFile(archive) as zip_file:
        prepared_members = _prepare_zip_members(zip_file, destination, extraction_budget)
        for member, parts in prepared_members:
            target = destination / Path(*parts)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zip_file.open(member) as source_file, target.open("xb") as output_file:
                shutil.copyfileobj(source_file, output_file, length=1024 * 1024)

    return destination


def create_output_dir(output_root: Path) -> Path:
    batch_name = datetime.now().strftime("%Y-%m-%d %I-%M-%S %p")
    output_dir = unique_path(output_root / batch_name, is_dir=True)
    output_dir.mkdir(parents=True)
    return output_dir


def convert_to_jpeg(source: Path, output_dir: Path | None) -> Path:
    if output_dir is None:
        raise ValueError("The finished folder was not created.")

    if source.suffix.lower() in {".heic", ".heif"} and not HEIF_SUPPORT_AVAILABLE:
        raise RuntimeError("HEIC support is not installed.")

    base = sanitize_filename(source.stem) or "picture"
    target = unique_path(output_dir / f"{base}.jpg")
    temporary = unique_path(output_dir / f".{target.name}.tmp")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            original_context = Image.open(source)
            with original_context as original:
                original.load()
                icc_profile = original.info.get("icc_profile")
                dpi = original.info.get("dpi")
                image = ImageOps.exif_transpose(original)
                exif = image.getexif()
                exif.pop(274, None)  # Orientation is now applied to the pixels.

                if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                    rgba = image.convert("RGBA")
                    background = Image.new("RGB", rgba.size, "white")
                    background.paste(rgba, mask=rgba.getchannel("A"))
                    image = background
                else:
                    image = image.convert("RGB")

                save_options: dict[str, object] = {
                    "format": "JPEG",
                    "quality": 95,
                    "optimize": True,
                }
                if exif:
                    save_options["exif"] = exif.tobytes()
                if icc_profile:
                    save_options["icc_profile"] = icc_profile
                if dpi:
                    save_options["dpi"] = dpi
                image.save(temporary, **save_options)
        temporary.replace(target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return target


def unique_path(path: Path, is_dir: bool = False) -> Path:
    if not path.exists():
        return path
    parent = path.parent
    stem = path.name if is_dir else path.stem
    suffix = "" if is_dir else path.suffix
    counter = 2
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def sanitize_filename(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", value).strip(" .")
    cleaned = cleaned[:180] or "file"
    if cleaned.split(".", 1)[0].rstrip(" ").upper() in WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned


def friendly_error(exc: Exception) -> str:
    if isinstance(exc, zipfile.BadZipFile):
        return "the ZIP is damaged or is not a real ZIP file"
    if isinstance(exc, UnidentifiedImageError):
        return "the picture is damaged or is not a supported image"
    if isinstance(exc, (Image.DecompressionBombWarning, Image.DecompressionBombError)):
        return "the picture is too large to process safely"
    if isinstance(exc, PermissionError):
        return "Windows would not allow the file to be opened"
    if isinstance(exc, OSError) and getattr(exc, "winerror", None) == 32:
        return "the file is still being used by another program"
    text = str(exc).strip()
    return text or exc.__class__.__name__


def open_path(path: Path) -> None:
    if os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
