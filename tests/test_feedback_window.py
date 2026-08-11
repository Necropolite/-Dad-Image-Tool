from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "internal" / "src"
sys.path.insert(0, str(SRC_DIR))

import feedback_window


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class FeedbackSubmissionTests(unittest.TestCase):
    def test_feedback_posts_plain_message_to_private_service(self) -> None:
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["payload"] = json.loads(request.data)
            captured["timeout"] = timeout
            return FakeResponse({"ok": True, "issue": 123})

        result = feedback_window.submit_feedback("Please change this", opener=opener)
        self.assertTrue(result["ok"])
        self.assertEqual(captured["url"], feedback_window.FEEDBACK_ENDPOINT)
        self.assertEqual(captured["payload"]["message"], "Please change this")
        self.assertEqual(captured["payload"]["source"], "Dad Image Tool")
        self.assertEqual(captured["payload"]["appVersion"], feedback_window.APP_VERSION)
        self.assertEqual(captured["timeout"], 30)

    def test_feedback_wording_is_not_trimmed_or_rewritten(self) -> None:
        captured = {}

        def opener(request, timeout):
            captured["payload"] = json.loads(request.data)
            return FakeResponse({"ok": True, "issue": 123})

        feedback_window.submit_feedback("  Keep my spacing.\nSecond line.  ", opener=opener)
        self.assertEqual(captured["payload"]["message"], "  Keep my spacing.\nSecond line.  ")

    def test_blank_feedback_is_rejected_before_network(self) -> None:
        with self.assertRaisesRegex(ValueError, "Type some feedback"):
            feedback_window.submit_feedback("   ", opener=lambda *_args, **_kwargs: None)


if __name__ == "__main__":
    unittest.main()
