from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SRC_DIR = Path(__file__).resolve().parents[1] / "internal" / "src"
sys.path.insert(0, str(SRC_DIR))

import assistant_launcher


class AssistantLauncherTests(unittest.TestCase):
    def test_opens_hosted_browser_assistant_by_default(self) -> None:
        opened = []
        with patch.dict(os.environ, {}, clear=True):
            url = assistant_launcher.open_assistant(opener=opened.append)
        self.assertEqual(url, "https://pete-ramey-assistant-api.cramey254.workers.dev/")
        self.assertEqual(opened, [url])

    def test_allows_configured_https_assistant(self) -> None:
        with patch.dict(os.environ, {"DAD_ASSISTANT_URL": "https://assistant.example.com/"}):
            self.assertEqual(assistant_launcher.assistant_url(), "https://assistant.example.com/")

    def test_rejects_insecure_remote_assistant(self) -> None:
        with patch.dict(os.environ, {"DAD_ASSISTANT_URL": "http://assistant.example.com/"}):
            self.assertEqual(assistant_launcher.assistant_url(), assistant_launcher.DEFAULT_ASSISTANT_URL)


if __name__ == "__main__":
    unittest.main()
