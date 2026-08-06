from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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

    def process(self, *items: Path) -> app.JobResult:
        return app.process_items([str(item) for item in items], self.output, lambda _text: None)
