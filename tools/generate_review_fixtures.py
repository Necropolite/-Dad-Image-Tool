from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

from PIL import Image


def make_image(path: Path, image_format: str, *, size: tuple[int, int] = (48, 32)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, (120, 80, 40)).save(path, format=image_format)


def create_fixtures(destination: Path) -> Path:
    destination = destination.resolve()
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    ordinary = destination / "ordinary-images"
    for filename, image_format in (
        ("horse.jpg", "JPEG"),
        ("horse.png", "PNG"),
        ("horse.webp", "WEBP"),
        ("horse.tiff", "TIFF"),
        ("horse.bmp", "BMP"),
    ):
        make_image(ordinary / filename, image_format)

    duplicates = destination / "duplicate-names"
    make_image(duplicates / "first" / "same.png", "PNG")
    make_image(duplicates / "second" / "same.png", "PNG")

    nested_source = destination / "_working" / "nested"
    make_image(nested_source / "case" / "hoof.png", "PNG")
    inner_zip = destination / "_working" / "inner.zip"
    with zipfile.ZipFile(inner_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(nested_source / "case" / "hoof.png", arcname="case/hoof.png")
    with zipfile.ZipFile(destination / "nested-zip.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(inner_zip, arcname="nested/inner.zip")

    (destination / "corrupt-image.png").write_bytes(b"not an image")
    (destination / "corrupt-zip.zip").write_bytes(b"not a zip")
    (destination / "unsupported.txt").write_text("not a picture", encoding="utf-8")

    with zipfile.ZipFile(destination / "path-traversal.zip", "w") as archive:
        archive.writestr("../escape.png", b"not an image")
    with zipfile.ZipFile(destination / "case-collision.zip", "w") as archive:
        archive.writestr("Photo.png", b"first")
        archive.writestr("photo.png", b"second")
    with zipfile.ZipFile(destination / "windows-invalid-name.zip", "w") as archive:
        archive.writestr("case/photo.png:stream", b"not an image")
    with zipfile.ZipFile(destination / "file-folder-conflict.zip", "w") as archive:
        archive.writestr("case", b"file")
        archive.writestr("case/photo.png", b"not an image")

    shutil.rmtree(destination / "_working")
    (destination / "README.txt").write_text(
        "Generated test data only. No client images are included.\n"
        "Use ordinary-images, duplicate-names, and nested-zip.zip for successful cases.\n"
        "The other files are intentional failure and archive-safety cases.\n",
        encoding="utf-8",
    )
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate repeatable, non-client fixtures for Dad Image Tool review.")
    parser.add_argument(
        "destination",
        nargs="?",
        default="review-fixtures",
        type=Path,
        help="Folder to replace with generated fixtures (default: review-fixtures)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    destination = create_fixtures(args.destination)
    print(f"Review fixtures created at: {destination}")


if __name__ == "__main__":
    main()
