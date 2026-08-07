from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

import pymupdf
from PIL import Image

import app


class DadImageToolTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.output = self.root / "output"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_image(self, path: Path, image_format: str = "PNG", size: tuple[int, int] = (24, 16)) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", size, (120, 80, 40)).save(path, format=image_format)
        return path

    def make_docx_with_images(self, path: Path, images: list[Path]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        relationships: list[str] = []
        blips: list[str] = []
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for index, image in enumerate(images, start=1):
                relationship_id = f"rId{index + 4}"
                media_name = f"image{index}{image.suffix.lower()}"
                relationships.append(
                    f'<Relationship Id="{relationship_id}" '
                    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                    f'Target="media/{media_name}"/>'
                )
                blips.append(f'<a:blip r:embed="{relationship_id}"/>')
                package.write(image, arcname=f"word/media/{media_name}")

            package.writestr(
                "word/document.xml",
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                f'<w:body>{"".join(blips)}</w:body></w:document>',
            )
            package.writestr(
                "word/_rels/document.xml.rels",
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'{"".join(relationships)}</Relationships>',
            )
        return path

    def make_pdf_with_images(self, path: Path, images: list[Path]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        document = pymupdf.open()
        page_height = max(200, 140 * len(images) + 20)
        page = document.new_page(width=400, height=page_height)
        for index, image in enumerate(images):
            top = 20 + index * 140
            page.insert_image(pymupdf.Rect(20, top, 220, top + 120), filename=str(image))
        document.save(path)
        document.close()
        return path

    def process(self, *items: Path) -> app.JobResult:
        return app.process_items([str(item) for item in items], self.output, lambda _text: None)
