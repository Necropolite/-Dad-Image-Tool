from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "internal" / "src"
sys.path.insert(0, str(SRC_DIR))

import feedback_window


class FeedbackSubmissionTests(unittest.TestCase):
    def test_feedback_is_disabled_without_network_access(self) -> None:
        network_called = False

        def opener(*_args, **_kwargs):
            nonlocal network_called
            network_called = True

        with self.assertRaisesRegex(RuntimeError, "temporarily unavailable"):
            feedback_window.submit_feedback("Please change this", opener=opener)
        self.assertFalse(network_called)

    def test_blank_feedback_is_rejected_before_network(self) -> None:
        with self.assertRaisesRegex(ValueError, "Type some feedback"):
            feedback_window.submit_feedback("   ", opener=lambda *_args, **_kwargs: None)

    def test_disabled_message_confirms_nothing_was_sent(self) -> None:
        self.assertIn("No feedback or account information has been sent", feedback_window.FEEDBACK_DISABLED_MESSAGE)


if __name__ == "__main__":
    unittest.main()
