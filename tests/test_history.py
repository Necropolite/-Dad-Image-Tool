from __future__ import annotations

import json

import history
from tests.common import DadImageToolTestCase


class HistoryTests(DadImageToolTestCase):
    def test_round_trip_includes_error_details(self) -> None:
        output = self.root / "Finished" / "job"
        output.mkdir(parents=True)
        history.record_job(
            self.root,
            source_names=["Smith Horse.zip"],
            converted=12,
            errors=["One image was damaged."],
            output_folder=output,
        )

        entry = history.load_history(self.root)[0]
        self.assertEqual(entry.converted, 12)
        self.assertEqual(entry.errors, 1)
        self.assertEqual(entry.status, "Needs attention")
        self.assertEqual(entry.error_messages, ["One image was damaged."])
        self.assertEqual(history.display_name(entry), "Smith Horse.zip")

    def test_old_entries_still_load(self) -> None:
        old_entry = {
            "completed_at": "2026-08-06T12:00:00",
            "source_names": ["old.zip"],
            "converted": 3,
            "errors": 0,
            "status": "Completed",
            "output_folder": None,
        }
        history.history_file(self.root).write_text(json.dumps(old_entry) + "\n", encoding="utf-8")

        entry = history.load_history(self.root)[0]
        self.assertEqual(entry.errors, 0)
        self.assertEqual(entry.error_messages, [])
