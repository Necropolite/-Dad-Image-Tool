from __future__ import annotations

import os
import zipfile
from unittest import mock

from PIL import Image

import app
from tests.common import DadImageToolTestCase


class ProcessingTests(DadImageToolTestCase):
    def test_png_converts_to_jpeg(self) -> None:
        source = self.make_image(self.root / "horse.png")
        result = self.process(source)

        self.assertEqual(result.converted, 1)
        self.assertEqual(result.errors, [])
        outputs = list(result.output_dir.glob("*.jpg"))
        self.assertEqual(len(outputs), 1)
        with Image.open(outputs[0]) as converted:
            self.assertEqual(converted.format, "JPEG")
            self.assertEqual(converted.size, (24, 16))

    def test_pillow_native_formats_convert(self) -> None:
        cases = (
            ("photo.jpg", "JPEG"),
            ("photo.webp", "WEBP"),
            ("photo.tiff", "TIFF"),
            ("photo.bmp", "BMP"),
        )
        for filename, image_format in cases:
            with self.subTest(image_format=image_format):
                source = self.make_image(self.root / image_format / filename, image_format=image_format)
                result = self.process(source)
                self.assertEqual(result.converted, 1)
                self.assertEqual(result.errors, [])
                with Image.open(next(result.output_dir.glob("*.jpg"))) as converted:
                    self.assertEqual(converted.format, "JPEG")

    def test_transparency_is_flattened_onto_white(self) -> None:
        source = self.root / "transparent.png"
        Image.new("RGBA", (8, 8), (0, 0, 0, 0)).save(source, format="PNG")

        result = self.process(source)

        with Image.open(next(result.output_dir.glob("*.jpg"))) as converted:
            red, green, blue = converted.getpixel((0, 0))
            self.assertGreater(min(red, green, blue), 240)

    def test_exif_and_dpi_metadata_are_preserved_when_valid(self) -> None:
        source = self.root / "metadata.jpg"
        exif = Image.Exif()
        exif[270] = "Horse case"
        Image.new("RGB", (10, 10), (20, 40, 60)).save(
            source,
            format="JPEG",
            exif=exif,
            dpi=(300, 300),
        )

        result = self.process(source)

        with Image.open(next(result.output_dir.glob("*.jpg"))) as converted:
            self.assertEqual(converted.getexif().get(270), "Horse case")
            self.assertAlmostEqual(converted.info["dpi"][0], 300, delta=1)

    def test_nested_zip_inside_zip_is_processed(self) -> None:
        image = self.make_image(self.root / "source" / "hoof.png")
        inner_archive = self.root / "inner.zip"
        with zipfile.ZipFile(inner_archive, "w") as zip_file:
            zip_file.write(image, arcname="case/hoof.png")

        outer_archive = self.root / "client-pictures.zip"
        with zipfile.ZipFile(outer_archive, "w") as zip_file:
            zip_file.write(inner_archive, arcname="nested/inner.zip")

        result = self.process(outer_archive)

        self.assertEqual(result.converted, 1)
        self.assertEqual(result.errors, [])
        self.assertEqual(len(list(result.output_dir.glob("*.jpg"))), 1)

    def test_folder_with_nested_zip_is_processed(self) -> None:
        source_folder = self.root / "client-folder"
        image = self.make_image(self.root / "source" / "leg.png")
        archive = source_folder / "more-pictures.zip"
        archive.parent.mkdir(parents=True)
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.write(image, arcname="leg.png")

        result = self.process(source_folder)

        self.assertEqual(result.converted, 1)
        self.assertEqual(result.errors, [])

    def test_duplicate_names_do_not_overwrite(self) -> None:
        first = self.make_image(self.root / "one" / "same.png")
        second = self.make_image(self.root / "two" / "same.png")

        result = self.process(first, second)

        names = sorted(path.name for path in result.output_dir.glob("*.jpg"))
        self.assertEqual(result.converted, 2)
        self.assertEqual(names, ["same (2).jpg", "same.jpg"])

    def test_corrupt_zip_reports_error_without_output_folder(self) -> None:
        archive = self.root / "broken.zip"
        archive.write_bytes(b"not a zip file")

        result = self.process(archive)

        self.assertEqual(result.converted, 0)
        self.assertIsNone(result.output_dir)
        self.assertTrue(result.errors)
        self.assertIn("ZIP", result.errors[0])

    def test_corrupt_image_does_not_leave_partial_output(self) -> None:
        source = self.root / "broken.png"
        source.write_bytes(b"not an image")

        result = self.process(source)

        self.assertEqual(result.converted, 0)
        self.assertIsNone(result.output_dir)
        self.assertTrue(result.errors)
        self.assertEqual(list(self.output.glob("*")), [])

    def test_good_and_corrupt_images_keep_successful_output_and_report_error(self) -> None:
        folder = self.root / "mixed"
        self.make_image(folder / "good.png")
        (folder / "broken.png").write_bytes(b"not an image")

        result = self.process(folder)

        self.assertEqual(result.converted, 1)
        self.assertEqual(len(result.errors), 1)
        self.assertIsNotNone(result.output_dir)
        self.assertEqual(len(list(result.output_dir.glob("*.jpg"))), 1)

    def test_zip_path_traversal_is_rejected(self) -> None:
        archive = self.root / "unsafe.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("../escape.png", b"not an image")

        result = self.process(archive)

        self.assertEqual(result.converted, 0)
        self.assertTrue(result.errors)
        self.assertIn("unsafe file path", result.errors[0])
        self.assertFalse((self.root / "escape.png").exists())


    def test_zip_case_insensitive_duplicate_paths_are_rejected(self) -> None:
        archive = self.root / "duplicates.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("Photo.png", b"first")
            zip_file.writestr("photo.png", b"second")

        result = self.process(archive)

        self.assertEqual(result.converted, 0)
        self.assertTrue(result.errors)
        self.assertIn("duplicate file paths", result.errors[0])

    def test_zip_windows_invalid_filename_is_rejected(self) -> None:
        archive = self.root / "invalid-name.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("case/photo.png:stream", b"not an image")

        result = self.process(archive)

        self.assertEqual(result.converted, 0)
        self.assertTrue(result.errors)
        self.assertIn("Windows cannot use safely", result.errors[0])

    def test_zip_windows_reserved_filename_is_rejected(self) -> None:
        archive = self.root / "reserved-name.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("case/CON .png", b"not an image")

        result = self.process(archive)

        self.assertEqual(result.converted, 0)
        self.assertTrue(result.errors)
        self.assertIn("reserved by Windows", result.errors[0])

    def test_zip_file_and_folder_conflict_is_rejected(self) -> None:
        archive = self.root / "conflict.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("case", b"file")
            zip_file.writestr("case/photo.png", b"not an image")

        result = self.process(archive)

        self.assertEqual(result.converted, 0)
        self.assertTrue(result.errors)
        self.assertIn("conflicting file and folder paths", result.errors[0])

    def test_exif_orientation_is_applied(self) -> None:
        source = self.root / "rotated.jpg"
        exif = Image.Exif()
        exif[274] = 6
        Image.new("RGB", (10, 20), (20, 40, 60)).save(source, format="JPEG", exif=exif)

        result = self.process(source)

        with Image.open(next(result.output_dir.glob("*.jpg"))) as converted:
            self.assertEqual(converted.size, (20, 10))
            self.assertNotEqual(converted.getexif().get(274), 6)

    def test_unsupported_file_does_not_leave_empty_finished_folder(self) -> None:
        source = self.root / "notes.txt"
        source.write_text("not a picture", encoding="utf-8")

        result = self.process(source)

        self.assertEqual(result.converted, 0)
        self.assertIsNone(result.output_dir)
        self.assertTrue(result.errors)
        self.assertEqual(list(self.output.glob("*")), [])

    def test_reserved_windows_filename_is_made_safe(self) -> None:
        self.assertEqual(app.sanitize_filename("CON"), "_CON")
        self.assertEqual(app.sanitize_filename("LPT1.photo"), "_LPT1.photo")
        self.assertEqual(app.sanitize_filename("CON .photo"), "_CON .photo")

    def test_linked_folder_is_rejected(self) -> None:
        target = self.root / "outside"
        target.mkdir()
        self.make_image(target / "outside.png")
        link = self.root / "linked"
        try:
            os.symlink(target, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Directory links are not available on this system")

        result = self.process(link)

        self.assertEqual(result.converted, 0)
        self.assertTrue(result.errors)
        self.assertIn("linked folder", result.errors[0])

    def test_decompression_bomb_warning_stops_conversion(self) -> None:
        source = self.root / "huge.png"
        source.write_bytes(b"placeholder")

        with mock.patch.object(app.Image, "open", side_effect=Image.DecompressionBombWarning("too large")):
            result = self.process(source)

        self.assertEqual(result.converted, 0)
        self.assertIsNone(result.output_dir)
        self.assertIn("too large to process safely", result.errors[0])

    def test_large_image_warning_has_plain_language_error(self) -> None:
        warning = Image.DecompressionBombWarning("large")
        self.assertEqual(app.friendly_error(warning), "the picture is too large to process safely")

    def test_archive_budget_rejects_oversized_declared_content(self) -> None:
        archive = self.root / "large.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("large.bin", b"12345")

        with mock.patch.object(app, "MAX_EXTRACTED_BYTES", 4):
            result = self.process(archive)

        self.assertEqual(result.converted, 0)
        self.assertTrue(result.errors)
        self.assertIn("too large", result.errors[0])
