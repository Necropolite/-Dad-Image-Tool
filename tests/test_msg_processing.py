from __future__ import annotations

from unittest.mock import patch

from PIL import Image

import msg_support
from tests.common import DadImageToolTestCase


class _FakeAttachment:
    def __init__(
        self,
        data: bytes,
        *,
        name: str | None = None,
        mimetype: str | None = None,
        content_id: str | None = None,
        extension: str | None = None,
    ) -> None:
        self.data = data
        self.name = name
        self.longFilename = name
        self.shortFilename = None
        self.mimetype = mimetype
        self.contentId = content_id
        self.cid = content_id
        self.extension = extension
        self.hidden = True


class _FakeMessage:
    def __init__(self, attachments: list[_FakeAttachment]) -> None:
        self.attachments = attachments
        self.closed = False

    def close(self) -> None:
        self.closed = True


class MsgProcessingTests(DadImageToolTestCase):
    def test_msg_inline_images_are_converted(self) -> None:
        first = self.make_image(self.root / "source" / "front.jpg", image_format="JPEG", size=(31, 21))
        second = self.make_image(self.root / "source" / "side.png", size=(28, 18))
        source = self.root / "consultation.msg"
        source.write_bytes(b"synthetic-msg-placeholder")

        message = _FakeMessage(
            [
                _FakeAttachment(
                    first.read_bytes(),
                    name="image001.jpg",
                    mimetype="image/jpeg",
                    content_id="image001@example",
                ),
                _FakeAttachment(
                    second.read_bytes(),
                    name=None,
                    mimetype="image/png",
                    content_id="IMG_1234@example",
                ),
            ]
        )

        with patch.object(msg_support.extract_msg, "openMsg", return_value=message):
            result = self.process(source)

        self.assertEqual(result.converted, 2)
        self.assertEqual(result.errors, [])
        self.assertTrue(message.closed)
        outputs = sorted((result.output_dir / "consultation").glob("*.jpg"))
        self.assertEqual(len(outputs), 2)
        with Image.open(outputs[0]) as converted:
            self.assertEqual(converted.size, (31, 21))
        with Image.open(outputs[1]) as converted:
            self.assertEqual(converted.size, (28, 18))

    def test_msg_unnamed_image_can_be_identified_from_bytes(self) -> None:
        image = self.make_image(self.root / "source" / "hoof.jpg", image_format="JPEG", size=(36, 24))
        source = self.root / "inline.msg"
        source.write_bytes(b"synthetic-msg-placeholder")
        message = _FakeMessage([_FakeAttachment(image.read_bytes())])

        with patch.object(msg_support.extract_msg, "openMsg", return_value=message):
            result = self.process(source)

        self.assertEqual(result.converted, 1)
        self.assertEqual(result.errors, [])
        output = next((result.output_dir / "inline").glob("*.jpg"))
        self.assertTrue(output.name.startswith("001-image1"))

    def test_msg_non_image_attachment_is_ignored(self) -> None:
        source = self.root / "notes.msg"
        source.write_bytes(b"synthetic-msg-placeholder")
        message = _FakeMessage([_FakeAttachment(b"plain text", name="notes.txt", mimetype="text/plain")])

        with patch.object(msg_support.extract_msg, "openMsg", return_value=message):
            result = self.process(source)

        self.assertEqual(result.converted, 0)
        self.assertIsNone(result.output_dir)
        self.assertTrue(result.errors)


if __name__ == "__main__":
    import unittest

    unittest.main()
