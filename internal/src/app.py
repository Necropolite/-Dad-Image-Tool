from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable

from PIL import Image, ImageOps, UnidentifiedImageError

import document_support
import email_support

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
CONTAINER_SUFFIXES = {".zip", ".docx", ".pdf", ".eml"}
IGNORED_NAMES = {".ds_store", "thumbs.db", "desktop.ini"}
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
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


@dataclass(frozen=True)
class CollectedImage:
    source: Path
    relative_path: Path


@dataclass
class ExtractionBudget:
    files: int = 0
    bytes: int = 0

    def add_bytes(self, size: int) -> None:
        self.files += 1
        self.bytes += max(0, int(size))
        if self.files > MAX_ARCHIVE_FILES:
            raise ValueError("The item contains too many files to process safely.")
        if self.bytes > MAX_EXTRACTED_BYTES:
            raise ValueError("The item contains too much data to process safely.")

    def add(self, member: zipfile.ZipInfo) -> None:
        if member.is_dir():
            return
        self.add_bytes(member.file_size)


def process_items(
    items: Iterable[str],
    output_root: Path,
    status_cb: StatusCallback,
    *,
    output_dir: Path | None = None,
) -> JobResult:
    """Convert pictures while preserving their source folder/container structure."""
    result = JobResult()
    source_items = [str(item) for item in items if str(item).strip()]
    if not source_items:
        result.errors.append("No source item was provided.")
        return result

    output_root.mkdir(parents=True, exist_ok=True)
    owns_output_dir = output_dir is None

    with tempfile.TemporaryDirectory(prefix="dad-image-tool-") as temp_name:
        temp_root = Path(temp_name)
        images: list[CollectedImage] = []
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
                    relative_root=source_relative_root(source),
                )
                images.extend(found)
                result.skipped += skipped
            except Exception as exc:
                result.errors.append(f"Could not use {source.name}: {friendly_error(exc)}")

        if not images and not result.errors:
            result.errors.append("No supported pictures were found.")
            return result

        if images:
            if output_dir is None:
                output_dir = create_output_dir(output_root)
            else:
                output_dir.mkdir(parents=True, exist_ok=True)
            result.output_dir = output_dir

        for index, collected in enumerate(images, start=1):
            status_cb(f"Converting picture {index} of {len(images)}...")
            try:
                convert_to_jpeg(collected.source, result.output_dir, collected.relative_path)
                result.converted += 1
            except Exception as exc:
                result.errors.append(f"Could not convert {collected.source.name}: {friendly_error(exc)}")

        if result.converted == 0:
            result.output_dir = None
            if owns_output_dir and output_dir is not None:
                shutil.rmtree(output_dir, ignore_errors=True)

    return result


def source_relative_root(source: Path) -> Path:
    if source.is_dir():
        return Path(sanitize_filename(source.name))
    if source.suffix.lower() in CONTAINER_SUFFIXES:
        return Path(sanitize_filename(source.stem))
    return Path()


def collect_images(
    source: Path,
    extraction_root: Path,
    *,
    budget: ExtractionBudget,
    nested_zip_depth: int,
    relative_root: Path = Path(),
) -> tuple[list[CollectedImage], int]:
    if source.is_dir():
        images: list[CollectedImage] = []
        skipped = 0
        for child in sorted(source.iterdir(), key=lambda path: path.name.casefold()):
            if child.name.casefold() in IGNORED_NAMES:
                continue
            child_root = relative_root
            if child.is_dir():
                child_root = relative_root / sanitize_filename(child.name)
            elif child.suffix.lower() in CONTAINER_SUFFIXES:
                child_root = relative_root / sanitize_filename(child.stem)
            child_images, child_skipped = collect_images(
                child,
                extraction_root,
                budget=budget,
                nested_zip_depth=nested_zip_depth,
                relative_root=child_root,
            )
            images.extend(child_images)
            skipped += child_skipped
        return images, skipped

    suffix = source.suffix.lower()
    if suffix in SUPPORTED_IMAGE_SUFFIXES:
        relative_name = sanitize_filename(source.name)
        return [CollectedImage(source=source, relative_path=relative_root / relative_name)], 0

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
            relative_root=relative_root,
        )

    if suffix == ".docx":
        extraction_root.mkdir(parents=True, exist_ok=True)
        destination = unique_path(
            extraction_root / f"docx-{sanitize_filename(source.stem)}",
            is_dir=True,
        )
        extracted = document_support.extract_docx_images(source, destination, budget.add_bytes)
        return _collect_extracted_images(extracted, relative_root)

    if suffix == ".pdf":
        extraction_root.mkdir(parents=True, exist_ok=True)
        destination = unique_path(
            extraction_root / f"pdf-{sanitize_filename(source.stem)}",
            is_dir=True,
        )
        extracted = document_support.extract_pdf_images(source, destination, budget.add_bytes)
        return _collect_extracted_images(extracted, relative_root)

    if suffix == ".eml":
        extraction_root.mkdir(parents=True, exist_ok=True)
        destination = unique_path(
            extraction_root / f"eml-{sanitize_filename(source.stem)}",
            is_dir=True,
        )
        extracted = email_support.extract_eml_images(source, destination, budget.add_bytes)
        return _collect_extracted_images(extracted, relative_root)

    return [], 1


def _collect_extracted_images(paths: list[Path], relative_root: Path) -> tuple[list[CollectedImage], int]:
    images: list[CollectedImage] = []
    skipped = 0
    for path in paths:
        if path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES:
            images.append(
                CollectedImage(
                    source=path,
                    relative_path=relative_root / sanitize_filename(path.name),
                )
            )
        else:
            skipped += 1
    return images, skipped


def safe_extract_zip(archive: Path, destination: Path, *, budget: ExtractionBudget | None = None) -> Path:
    destination.mkdir(parents=True, exist_ok=False)
    root = destination.resolve()
    extraction_budget = budget or ExtractionBudget()

    with zipfile.ZipFile(archive) as zip_file:
        members = zip_file.infolist()
        for member in members:
            extraction_budget.add(member)
            if member.flag_bits & 0x1:
                raise ValueError("The ZIP is password protected.")

            member_name = member.filename.replace("\\", "/")
            member_path = PurePosixPath(member_name)
            if (
                member_path.is_absolute()
                or ".." in member_path.parts
                or (member_path.parts and ":" in member_path.parts[0])
            ):
                raise ValueError("The ZIP contains an unsafe file path.")

            unix_mode = (member.external_attr >> 16) & 0o170000
            if unix_mode == stat.S_IFLNK:
                raise ValueError("The ZIP contains an unsupported symbolic link.")

            target = (destination / Path(*member_path.parts)).resolve()
            if target != root and root not in target.parents:
                raise ValueError("The ZIP contains an unsafe file path.")

        for member in members:
            member_name = member.filename.replace("\\", "/")
            member_path = PurePosixPath(member_name)
            if not member_path.parts:
                continue
            target = destination / Path(*member_path.parts)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zip_file.open(member) as source_file, target.open("wb") as output_file:
                shutil.copyfileobj(source_file, output_file, length=1024 * 1024)

    return destination


def create_output_dir(output_root: Path) -> Path:
    batch_name = datetime.now().strftime("%Y-%m-%d %I-%M-%S %p")
    output_dir = unique_path(output_root / batch_name, is_dir=True)
    output_dir.mkdir(parents=True)
    return output_dir


def convert_to_jpeg(source: Path, output_dir: Path | None, relative_path: Path | None = None) -> Path:
    if output_dir is None:
        raise ValueError("The finished folder was not created.")

    if source.suffix.lower() in {".heic", ".heif"} and not HEIF_SUPPORT_AVAILABLE:
        raise RuntimeError("HEIC support is not installed.")

    if relative_path is None:
        relative_path = Path(sanitize_filename(source.name))

    relative_parent = Path(
        *[sanitize_filename(part) for part in relative_path.parent.parts if part not in {"", "."}]
    )
    base = sanitize_filename(relative_path.stem) or "picture"
    target_dir = output_dir / relative_parent
    target_dir.mkdir(parents=True, exist_ok=True)
    target = unique_path(target_dir / f"{base}.jpg")
    temporary = unique_path(target_dir / f".{target.name}.tmp")

    try:
        original_context = Image.open(source)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    try:
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
    if cleaned.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned


def friendly_error(exc: Exception) -> str:
    if isinstance(exc, zipfile.BadZipFile):
        return "the file is damaged or is not a valid ZIP/Word container"
    if isinstance(exc, UnidentifiedImageError):
        return "the picture is damaged or is not a supported image"
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
