from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

import app
import history


class DadImageToolCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.output = self.root / "output"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_image(self, path: Path, image_format: str = "PNG") -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (24, 16), (120, 80, 40)).save(path, format=image_format)
        return path

    def test_png_converts_to_jpeg(self) -> None:
        source = self.make_image(self.root / "horse.png")
        result = app.process_items([str(source)], self.output, lambda _text: None)

        self.assertEqual(result.converted, 1)
        self.assertEqual(result.errors, [])
        outputs = list(result.output_dir.glob("*.jpg"))
        self.assertEqual(len(outputs), 1)
        with Image.open(outputs[0]) as converted:
            self.assertEqual(converted.format, "JPEG")
            self.assertEqual(converted.size, (24, 16))

    def test_nested_zip_is_processed(self) -> None:
        image = self.make_image(self.root / "source" / "nested" / "hoof.png")
        archive = self.root / "client-pictures.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.write(image, arcname="case/nested/hoof.png")

        result = app.process_items([str(archive)], self.output, lambda _text: None)

        self.assertEqual(result.converted, 1)
        self.assertEqual(len(list(result.output_dir.glob("*.jpg"))), 1)

    def test_duplicate_names_do_not_overwrite(self) -> None:
        first = self.make_image(self.root / "one" / "same.png")
        second = self.make_image(self.root / "two" / "same.png")

        result = app.process_items([str(first), str(second)], self.output, lambda _text: None)

        names = sorted(path.name for path in result.output_dir.glob("*.jpg"))
        self.assertEqual(result.converted, 2)
        self.assertEqual(names, ["same (2).jpg", "same.jpg"])

    def test_corrupt_zip_reports_error(self) -> None:
        archive = self.root / "broken.zip"
        archive.write_bytes(b"not a zip file")

        result = app.process_items([str(archive)], self.output, lambda _text: None)

        self.assertEqual(result.converted, 0)
        self.assertTrue(result.errors)
        self.assertIn("ZIP", result.errors[0])

    def test_job_history_round_trip(self) -> None:
        output_folder = self.root / "Finished" / "job"
        output_folder.mkdir(parents=True)
        history.record_job(
            self.root,
            source_names=["Smith Horse.zip"],
            converted=12,
            errors=0,
            output_folder=output_folder,
        )

        entries = history.load_history(self.root)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].converted, 12)
        self.assertEqual(entries[0].status, "Completed")
        self.assertEqual(history.display_name(entries[0]), "Smith Horse.zip")


if __name__ == "__main__":
    unittest.main()
