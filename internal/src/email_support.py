from __future__ import annotations

from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Callable

BudgetCallback = Callable[[int], None]

_SUPPORTED_IMAGE_EXTENSIONS = {
    "jpeg": ".jpg",
    "jpg": ".jpg",
    "png": ".png",
    "webp": ".webp",
    "heic": ".heic",
    "heif": ".heif",
    "tiff": ".tiff",
    "tif": ".tif",
    "bmp": ".bmp",
    "x-ms-bmp": ".bmp",
}
_SUPPORTED_SUFFIXES = set(_SUPPORTED_IMAGE_EXTENSIONS.values()) | {".jpeg"}


def extract_eml_images(source: Path, destination: Path, budget_add: BudgetCallback) -> list[Path]:
    """Extract supported inline and attached MIME images from an EML message in message order."""
    destination.mkdir(parents=True, exist_ok=False)

    try:
        with source.open("rb") as message_file:
            message = BytesParser(policy=policy.default).parse(message_file)
    except Exception as exc:
        raise ValueError("the email message could not be opened") from exc

    extracted: list[Path] = []
    sequence = 1

    for part in message.walk():
        if part.is_multipart() or part.get_content_maintype().lower() != "image":
            continue

        subtype = part.get_content_subtype().lower()
        default_suffix = _SUPPORTED_IMAGE_EXTENSIONS.get(subtype)
        filename = part.get_filename()
        filename_suffix = Path(filename).suffix.lower() if filename else ""

        if filename_suffix in _SUPPORTED_SUFFIXES:
            suffix = ".jpg" if filename_suffix == ".jpeg" else filename_suffix
        elif default_suffix is not None:
            suffix = default_suffix
        else:
            continue

        try:
            payload = part.get_payload(decode=True)
        except Exception as exc:
            raise ValueError("an embedded email picture could not be decoded") from exc

        if not isinstance(payload, (bytes, bytearray)) or not payload:
            continue
        image_bytes = bytes(payload)
        budget_add(len(image_bytes))

        leaf_name = _image_leaf_name(filename, part.get("Content-ID"), sequence, suffix)
        target = destination / f"{sequence:03d}-{leaf_name}"
        target.write_bytes(image_bytes)
        extracted.append(target)
        sequence += 1

    return extracted


def _image_leaf_name(filename: str | None, content_id: str | None, sequence: int, suffix: str) -> str:
    if filename:
        stem = Path(filename).stem
    elif content_id:
        stem = str(content_id).strip().strip("<>")
        stem = Path(stem).stem
    else:
        stem = f"image{sequence}"

    cleaned = _safe_leaf_name(stem)
    return f"{cleaned}{suffix}"


def _safe_leaf_name(value: str) -> str:
    forbidden = '<>:"/\\|?*'
    cleaned = "".join("_" if character in forbidden or ord(character) < 32 else character for character in value)
    cleaned = cleaned.strip(" .")
    return cleaned[:150] or "image"
