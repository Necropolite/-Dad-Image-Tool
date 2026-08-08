from __future__ import annotations

import zipfile
from email.message import EmailMessage

from PIL import Image

from tests.common import DadImageToolTestCase


class EmailProcessingTests(DadImageToolTestCase):
    def test_eml_inline_and_attached_images_are_converted(self) -> None:
        front = self.make_image(self.root / "source" / "front.jpg", image_format="JPEG", size=(31, 21))
        side = self.make_image(self.root / "source" / "side.png", size=(28, 18))
        sole = self.make_image(self.root / "source" / "sole.jpg", image_format="JPEG", size=(35, 23))
        message = self.make_eml_with_images(
            self.root / "consultation.eml",
            [front, side],
            [sole],
        )

        result = self.process(message)

        self.assertEqual(result.converted, 3)
        self.assertEqual(result.errors, [])
        outputs = sorted((result.output_dir / "consultation").glob("*.jpg"))
        self.assertEqual(len(outputs), 3)
        sizes = []
        for output in outputs:
            with Image.open(output) as converted:
                sizes.append(converted.size)
        self.assertEqual(sizes, [(31, 21), (28, 18), (35, 23)])

    def test_inline_image_without_filename_uses_content_id(self) -> None:
        image = self.make_image(self.root / "source" / "hoof.jpg", image_format="JPEG")
        message = EmailMessage()
        message["Subject"] = "Inline Apple-style image"
        message.set_content("Embedded picture", subtype="html")
        message.add_related(
            image.read_bytes(),
            maintype="image",
            subtype="jpeg",
            cid="<IMG_1234@example>",
            disposition="inline",
        )
        source = self.root / "inline.eml"
        source.write_bytes(message.as_bytes())

        result = self.process(source)

        self.assertEqual(result.converted, 1)
        self.assertEqual(result.errors, [])
        outputs = list((result.output_dir / "inline").glob("*.jpg"))
        self.assertEqual(len(outputs), 1)
        self.assertTrue(outputs[0].name.startswith("001-IMG_1234"))

    def test_eml_inside_zip_is_processed(self) -> None:
        image = self.make_image(self.root / "source" / "hoof.jpg", image_format="JPEG")
        message = self.make_eml_with_images(self.root / "case.eml", [image])
        archive = self.root / "client-email.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(message, arcname="mail/case.eml")

        result = self.process(archive)

        self.assertEqual(result.converted, 1)
        self.assertEqual(result.errors, [])
        self.assertTrue(
            (result.output_dir / "client-email" / "mail" / "case" / "001-hoof.jpg").exists()
        )

    def test_eml_without_supported_images_does_not_create_finished_folder(self) -> None:
        message = EmailMessage()
        message["Subject"] = "No pictures"
        message.set_content("Text only")
        source = self.root / "text-only.eml"
        source.write_bytes(message.as_bytes())

        result = self.process(source)

        self.assertEqual(result.converted, 0)
        self.assertIsNone(result.output_dir)
        self.assertTrue(result.errors)


if __name__ == "__main__":
    import unittest

    unittest.main()
