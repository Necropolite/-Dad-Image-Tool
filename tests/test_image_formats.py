from __future__ import annotations

import unittest

from PIL import Image

import app
from tests.common import DadImageToolTestCase


class SupportedImageFormatTests(DadImageToolTestCase):
    def test_every_advertised_image_format_converts_to_jpeg(self) -> None:
        self.assertTrue(app.HEIF_SUPPORT_AVAILABLE, "pillow-heif must be installed for advertised HEIC/HEIF support")

        formats = (
            ("photo.jpg", "JPEG"),
            ("photo.jpeg", "JPEG"),
            ("photo.png", "PNG"),
            ("photo.heic", "HEIF"),
            ("photo.heif", "HEIF"),
            ("photo.webp", "WEBP"),
            ("photo.tiff", "TIFF"),
            ("photo.bmp", "BMP"),
        )

        for index, (filename, image_format) in enumerate(formats, start=1):
            with self.subTest(filename=filename):
                source = self.root / f"format-{index}" / filename
                source.parent.mkdir(parents=True, exist_ok=True)
                Image.new("RGB", (29, 17), (100, 70, 40)).save(source, format=image_format)

                result = self.process(source)

                self.assertEqual(result.converted, 1)
                self.assertEqual(result.errors, [])
                output = next(result.output_dir.glob("*.jpg"))
                with Image.open(output) as converted:
                    self.assertEqual(converted.format, "JPEG")
                    self.assertEqual(converted.size, (29, 17))


if __name__ == "__main__":
    unittest.main()
