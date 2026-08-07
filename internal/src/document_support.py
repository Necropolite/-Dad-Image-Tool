from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Callable
from xml.etree import ElementTree as ET

try:
    import pymupdf
except ImportError:  # Source inspection can still run without optional PDF support.
    pymupdf = None

BudgetCallback = Callable[[int], None]

_DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
_OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_VML_NS = "urn:schemas-microsoft-com:vml"
_IMAGE_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
_SUPPORTED_EXTRACTED_SUFFIXES = {
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


def extract_docx_images(source: Path, destination: Path, budget_add: BudgetCallback) -> list[Path]:
    """Extract embedded DOCX images in the order they appear in the document."""
    destination.mkdir(parents=True, exist_ok=False)
    extracted: list[Path] = []

    with zipfile.ZipFile(source) as package:
        members = package.infolist()
        for info in members:
            if not info.is_dir():
                budget_add(info.file_size)

        names = {info.filename for info in members}
        ordered_members = _docx_image_members(package, names)
        if not ordered_members:
            ordered_members = sorted(
                (name for name in names if name.startswith("word/media/") and not name.endswith("/")),
                key=_natural_key,
            )

        seen_members: set[str] = set()
        sequence = 1
        for member_name in ordered_members:
            if member_name in seen_members or member_name not in names:
                continue
            seen_members.add(member_name)
            info = package.getinfo(member_name)
            if info.is_dir():
                continue

            media_name = PurePosixPath(member_name).name
            suffix = Path(media_name).suffix.lower()
            if suffix not in _SUPPORTED_EXTRACTED_SUFFIXES:
                continue

            target = destination / f"{sequence:03d}-{_safe_leaf_name(media_name)}"
            with package.open(info) as source_file, target.open("wb") as output_file:
                while True:
                    chunk = source_file.read(1024 * 1024)
                    if not chunk:
                        break
                    output_file.write(chunk)
            extracted.append(target)
            sequence += 1

    return extracted


def _docx_image_members(package: zipfile.ZipFile, names: set[str]) -> list[str]:
    document_name = "word/document.xml"
    relationships_name = "word/_rels/document.xml.rels"
    if document_name not in names or relationships_name not in names:
        return []

    try:
        document_root = ET.fromstring(package.read(document_name))
        relationships_root = ET.fromstring(package.read(relationships_name))
    except ET.ParseError as exc:
        raise ValueError("the Word document contains damaged XML") from exc

    relationships: dict[str, str] = {}
    for relationship in relationships_root:
        relationship_id = relationship.get("Id")
        target = relationship.get("Target")
        target_mode = relationship.get("TargetMode", "")
        relationship_type = relationship.get("Type", "")
        if not relationship_id or not target or target_mode.lower() == "external":
            continue
        if relationship_type and relationship_type != _IMAGE_REL_TYPE:
            continue
        member = _resolve_docx_member(target)
        if member is not None:
            relationships[relationship_id] = member

    ordered: list[str] = []
    drawing_tag = f"{{{_DRAWING_NS}}}blip"
    vml_tag = f"{{{_VML_NS}}}imagedata"
    embed_attribute = f"{{{_OFFICE_REL_NS}}}embed"
    relationship_attribute = f"{{{_OFFICE_REL_NS}}}id"

    for element in document_root.iter():
        relationship_id: str | None = None
        if element.tag == drawing_tag:
            relationship_id = element.get(embed_attribute)
        elif element.tag == vml_tag:
            relationship_id = element.get(relationship_attribute)
        if relationship_id:
            member = relationships.get(relationship_id)
            if member:
                ordered.append(member)
    return ordered


def _resolve_docx_member(target: str) -> str | None:
    path = PurePosixPath(target.replace("\\", "/"))
    if path.is_absolute() or not path.parts or ".." in path.parts or ":" in path.parts[0]:
        return None
    full = PurePosixPath("word") / path
    if ".." in full.parts:
        return None
    return full.as_posix()


def extract_pdf_images(source: Path, destination: Path, budget_add: BudgetCallback) -> list[Path]:
    """Extract embedded raster images from a PDF without rendering whole pages."""
    if pymupdf is None:
        raise RuntimeError("PDF picture support is not installed")

    destination.mkdir(parents=True, exist_ok=False)
    extracted: list[Path] = []
    seen_digests: set[str] = set()
    sequence = 1
    budget_add(source.stat().st_size)

    try:
        document = pymupdf.open(source)
    except Exception as exc:
        raise ValueError("the PDF could not be opened") from exc

    try:
        if document.needs_pass:
            raise ValueError("the PDF is password protected")

        for page_number, page in enumerate(document, start=1):
            try:
                blocks = page.get_text("dict").get("blocks", [])
            except Exception as exc:
                raise ValueError(f"page {page_number} of the PDF could not be read") from exc

            for block in blocks:
                if block.get("type") != 1:
                    continue
                image_bytes = block.get("image")
                if not isinstance(image_bytes, (bytes, bytearray)) or not image_bytes:
                    continue
                image_bytes = bytes(image_bytes)

                digest = hashlib.sha256(image_bytes).hexdigest()
                if digest in seen_digests:
                    continue
                seen_digests.add(digest)
                budget_add(len(image_bytes))

                extension = str(block.get("ext") or "png").lower().lstrip(".")
                if extension == "jpeg":
                    extension = "jpg"
                if f".{extension}" not in _SUPPORTED_EXTRACTED_SUFFIXES:
                    try:
                        image_bytes = pymupdf.Pixmap(image_bytes).tobytes("png")
                    except Exception as exc:
                        raise ValueError(
                            f"an embedded picture on PDF page {page_number} could not be decoded"
                        ) from exc
                    extension = "png"

                target = destination / f"{sequence:03d}-page-{page_number}.{extension}"
                target.write_bytes(image_bytes)
                extracted.append(target)
                sequence += 1
    finally:
        document.close()

    return extracted


def _safe_leaf_name(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", value).strip(" .")
    return cleaned[:160] or "picture"


def _natural_key(value: str) -> list[object]:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]
