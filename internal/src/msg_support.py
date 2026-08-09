from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Callable

import extract_msg
from PIL import Image, UnidentifiedImageError

BudgetCallback = Callable[[int], None]

_SUPPORTED_SUFFIXES = {
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
_MIME_SUFFIXES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/heif": ".heif",
    "image/tiff": ".tiff",
    "image/bmp": ".bmp",
    "image/x-ms-bmp": ".bmp",
}
_PIL_SUFFIXES = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "TIFF": ".tiff",
    "BMP": ".bmp",
}


def extract_msg_images(source: Path, destination: Path, budget_add: BudgetCallback) -> list[Path]:
    """Extract supported image attachments, including inline Outlook images, from an MSG file."""
    destination.mkdir(parents=True, exist_ok=False)

    try:
        message = extract_msg.openMsg(str(source))
    except Exception as exc:
        raise ValueError("the Outlook message could not be opened") from exc

    extracted: list[Path] = []
    sequence = 1
    try:
        for attachment in message.attachments:
            try:
                payload = attachment.data
            except Exception:
                continue
            if not isinstance(payload, (bytes, bytearray)) or not payload:
                # Embedded MSG objects and unsupported OLE/web attachments are not image byte streams.
                continue
            image_bytes = bytes(payload)

            filename = _first_text(
                getattr(attachment, "name", None),
                getattr(attachment, "longFilename", None),
                getattr(attachment, "shortFilename", None),
            )
            content_id = _first_text(
                getattr(attachment, "contentId", None),
                getattr(attachment, "cid", None),
            )
            mimetype = str(getattr(attachment, "mimetype", "") or "").strip().lower()
            extension = str(getattr(attachment, "extension", "") or "").strip().lower()

            suffix = _image_suffix(filename, extension, mimetype, image_bytes)
            if suffix is None:
                continue

            budget_add(len(image_bytes))
            leaf_name = _image_leaf_name(filename, content_id, sequence, suffix)
            target = destination / f"{sequence:03d}-{leaf_name}"
            target.write_bytes(image_bytes)
            extracted.append(target)
            sequence += 1
    finally:
        try:
            message.close()
        except Exception:
            pass

    return extracted


def _image_suffix(filename: str | None, extension: str, mimetype: str, data: bytes) -> str | None:
    if filename:
        filename_suffix = Path(filename).suffix.lower()
        if filename_suffix in _SUPPORTED_SUFFIXES:
            return ".jpg" if filename_suffix == ".jpeg" else filename_suffix

    if extension:
        normalized = extension if extension.startswith(".") else f".{extension}"
        if normalized in _SUPPORTED_SUFFIXES:
            return ".jpg" if normalized == ".jpeg" else normalized

    mime_suffix = _MIME_SUFFIXES.get(mimetype)
    if mime_suffix is not None:
        return mime_suffix

    # Some Outlook inline images have neither a useful filename nor MIME type.
    # Sniff common raster formats so those images can still be recovered.
    try:
        with Image.open(BytesIO(data)) as image:
            return _PIL_SUFFIXES.get(str(image.format or "").upper())
    except (UnidentifiedImageError, OSError):
        return None


def _image_leaf_name(filename: str | None, content_id: str | None, sequence: int, suffix: str) -> str:
    if filename:
        stem = Path(filename).stem
    elif content_id:
        stem = str(content_id).strip().strip("<>")
        stem = Path(stem).stem
    else:
        stem = f"image{sequence}"
    return f"{_safe_leaf_name(stem)}{suffix}"


def _first_text(*values: object) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _safe_leaf_name(value: str) -> str:
    forbidden = '<>:"/\\|?*'
    cleaned = "".join("_" if character in forbidden or ord(character) < 32 else character for character in value)
    cleaned = cleaned.strip(" .")
    return cleaned[:150] or "image"
