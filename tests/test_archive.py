from __future__ import annotations

import watcher_support
from tests.common import DadImageToolTestCase


class ArchiveTests(DadImageToolTestCase):
    def test_duplicate_archive_names_are_not_overwritten(self) -> None:
        archive = self.root / "archive"
        first = self.root / "first" / "same.txt"
        second = self.root / "second" / "same.txt"
        first.parent.mkdir()
        second.parent.mkdir()
        first.write_text("one", encoding="utf-8")
        second.write_text("two", encoding="utf-8")

        first_target = watcher_support.move_target(first, archive)
        second_target = watcher_support.move_target(second, archive)
        self.assertEqual(first_target.name, "same.txt")
        self.assertEqual(second_target.name, "same (2).txt")
        self.assertEqual(first_target.read_text(encoding="utf-8"), "one")
        self.assertEqual(second_target.read_text(encoding="utf-8"), "two")
