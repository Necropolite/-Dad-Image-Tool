from __future__ import annotations

import zipfile
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

    def test_folder_structure_is_preserved(self) -> None:
        source = self.root / "client-folder"
        self.make_image(source / "front.jpg", image_format="JPEG")
        self.make_image(source / "nested" / "side.png")

        result = self.process(source)

        self.assertEqual(result.converted, 2)
        self.assertEqual(result.errors, [])
        self.assertTrue((result.output_dir / "client-folder" / "front.jpg").exists())
        self.assertTrue((result.output_dir / "client-folder" / "nested" / "side.jpg").exists())

    def test_docx_embedded_images_are_extracted_in_document_order(self) -> None:
        first = self.make_image(self.root / "source" / "front.png", size=(30, 20))
        second = self.make_image(self.root / "source" / "side.jpg", image_format="JPEG", size=(40, 25))
        document = self.make_docx_with_images(self.root / "consultant-case.docx", [first, second])

        result = self.process(document)

        self.assertEqual(result.converted, 2)
        self.assertEqual(result.errors, [])
        first_output = result.output_dir / "consultant-case" / "001-image1.jpg"
        second_output = result.output_dir / "consultant-case" / "002-image2.jpg"
        self.assertTrue(first_output.exists())
        self.assertTrue(second_output.exists())
        with Image.open(first_output) as converted:
            self.assertEqual(converted.size, (30, 20))
        with Image.open(second_output) as converted:
            self.assertEqual(converted.size, (40, 25))

    def test_pdf_embedded_images_are_extracted_without_rendering_pages(self) -> None:
        first = self.make_image(self.root / "source" / "front.jpg", image_format="JPEG", size=(32, 24))
        second = self.make_image(self.root / "source" / "side.png", size=(28, 18))
        document = self.make_pdf_with_images(self.root / "consultant-case.pdf", [first, second])

        result = self.process(document)

        self.assertEqual(result.converted, 2)
        self.assertEqual(result.errors, [])
        first_output = result.output_dir / "consultant-case" / "001-page-1.jpg"
        second_output = result.output_dir / "consultant-case" / "002-page-1.jpg"
        self.assertTrue(first_output.exists())
        self.assertTrue(second_output.exists())
        with Image.open(first_output) as converted:
            self.assertEqual(converted.size, (32, 24))
        with Image.open(second_output) as converted:
            self.assertEqual(converted.size, (28, 18))

    def test_docx_inside_zip_is_processed_without_manual_extraction(self) -> None:
        image = self.make_image(self.root / "source" / "hoof.jpg", image_format="JPEG")
        document = self.make_docx_with_images(self.root / "questions.docx", [image])
        archive = self.root / "client-bundle.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(document, arcname="case/questions.docx")

        result = self.process(archive)

        self.assertEqual(result.converted, 1)
        self.assertEqual(result.errors, [])
        self.assertTrue(
            (result.output_dir / "client-bundle" / "case" / "questions" / "001-image1.jpg").exists()
        )

    def test_zip_can_be_processed_without_manual_extraction(self) -> None:
        first = self.make_image(self.root / "source" / "front.jpg", image_format="JPEG")
        second = self.make_image(self.root / "source" / "side.jpg", image_format="JPEG")
        archive = self.root / "client-pictures.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(first, arcname="front.jpg")
            zip_file.write(second, arcname="side.jpg")

        result = self.process(archive)

        self.assertEqual(result.converted, 2)
        self.assertEqual(result.errors, [])
        self.assertTrue((result.output_dir / "client-pictures" / "front.jpg").exists())
        self.assertTrue((result.output_dir / "client-pictures" / "side.jpg").exists())

    def test_deflate64_zip_can_be_processed_without_manual_extraction(self) -> None:
        from zipfile64 import ZIP_DEFLATE64, patch

        patch()
        first = self.make_image(self.root / "source" / "front.jpg", image_format="JPEG")
        second = self.make_image(self.root / "source" / "side.jpg", image_format="JPEG")
        archive = self.root / "client-deflate64.zip"
        with zipfile.ZipFile(archive, "w", compression=ZIP_DEFLATE64) as zip_file:
            zip_file.write(first, arcname="front.jpg")
            zip_file.write(second, arcname="side.jpg")

        result = self.process(archive)

        self.assertEqual(result.converted, 2)
        self.assertEqual(result.errors, [])
        self.assertTrue((result.output_dir / "client-deflate64" / "front.jpg").exists())
        self.assertTrue((result.output_dir / "client-deflate64" / "side.jpg").exists())

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
        self.assertTrue(
            (result.output_dir / "client-pictures" / "nested" / "inner" / "case" / "hoof.jpg").exists()
        )

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
        self.assertTrue((result.output_dir / "client-folder" / "more-pictures" / "leg.jpg").exists())

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
        self.assertTrue("damaged" in result.errors[0].lower() or "ZIP" in result.errors[0])

    def test_corrupt_image_does_not_leave_partial_output(self) -> None:
        source = self.root / "broken.png"
        source.write_bytes(b"not an image")

        result = self.process(source)

        self.assertEqual(result.converted, 0)
        self.assertIsNone(result.output_dir)
        self.assertTrue(result.errors)
        self.assertEqual(list(self.output.glob("*")), [])

    def test_zip_path_traversal_is_rejected(self) -> None:
        archive = self.root / "unsafe.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("../escape.png", b"not an image")

        result = self.process(archive)

        self.assertEqual(result.converted, 0)
        self.assertTrue(result.errors)
        self.assertIn("unsafe file path", result.errors[0])
        self.assertFalse((self.root / "escape.png").exists())

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
