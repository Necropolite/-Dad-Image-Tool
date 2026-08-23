from __future__ import annotations

import unittest
from pathlib import Path


UI_LAYOUT = Path(__file__).resolve().parents[1] / "internal" / "src" / "ui_layout.py"


class UiLayoutFeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = UI_LAYOUT.read_text(encoding="utf-8")

    def test_approved_main_controls_remain_present(self) -> None:
        for label in (
            "Open Drop Folder",
            "Open Finished Pictures",
            "View History",
            "Check for Updates",
        ):
            with self.subTest(label=label):
                self.assertIn(f'text="{label}"', self.source)

    def test_unapproved_auxiliary_features_are_not_present(self) -> None:
        for value in (
            "feedback_window",
            'text="Feedback"',
            "assistant_launcher",
            'text="Ask Pete (Experimental)"',
            "learning_lab_launcher",
            'text="Learning Lab (Experimental)"',
        ):
            with self.subTest(value=value):
                self.assertNotIn(value, self.source)


if __name__ == "__main__":
    unittest.main()
