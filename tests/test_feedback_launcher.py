from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SRC_DIR = Path(__file__).resolve().parents[1] / "internal" / "src"
sys.path.insert(0, str(SRC_DIR))

import feedback_launcher


class FeedbackLauncherTests(unittest.TestCase):
    def test_opens_project_feedback_form_by_default(self) -> None:
        opened = []
        with patch.dict(os.environ, {}, clear=True):
            url = feedback_launcher.open_feedback(opener=opened.append)
        self.assertEqual(url, feedback_launcher.DEFAULT_FEEDBACK_URL)
        self.assertIn("template=dad-feedback.yml", url)
        self.assertEqual(opened, [url])

    def test_allows_configured_https_feedback_form(self) -> None:
        with patch.dict(os.environ, {"DAD_FEEDBACK_URL": "https://feedback.example.com/form"}):
            self.assertEqual(feedback_launcher.feedback_url(), "https://feedback.example.com/form")

    def test_rejects_insecure_feedback_address(self) -> None:
        with patch.dict(os.environ, {"DAD_FEEDBACK_URL": "http://feedback.example.com/form"}):
            self.assertEqual(feedback_launcher.feedback_url(), feedback_launcher.DEFAULT_FEEDBACK_URL)


if __name__ == "__main__":
    unittest.main()
