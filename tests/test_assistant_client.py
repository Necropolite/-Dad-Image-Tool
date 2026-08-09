from __future__ import annotations

import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "internal" / "src"
sys.path.insert(0, str(SRC_DIR))
from assistant_client import ask_assistant


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class AssistantClientTests(unittest.TestCase):
    def test_sends_authenticated_chat_request_and_reads_citations(self) -> None:
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["authorization"] = request.headers["Authorization"]
            captured["payload"] = json.loads(request.data)
            captured["timeout"] = timeout
            return FakeResponse({"answer": "Use the cited source. [S1]", "citations": [{"id": "S1"}]})

        reply = ask_assistant(
            "http://127.0.0.1:8787/",
            "private-token",
            "What does Pete say?",
            [{"role": "user", "content": "Earlier question"}],
            opener=opener,
        )

        self.assertEqual(captured["url"], "http://127.0.0.1:8787/api/chat")
        self.assertEqual(captured["authorization"], "Bearer private-token")
        self.assertEqual(captured["payload"]["message"], "What does Pete say?")
        self.assertEqual(captured["timeout"], 90)
        self.assertEqual(reply.citations, [{"id": "S1"}])

    def test_rejects_missing_token_before_network_request(self) -> None:
        with self.assertRaisesRegex(ValueError, "private access token"):
            ask_assistant("http://127.0.0.1:8787", "", "Question")

    def test_rejects_insecure_remote_address(self) -> None:
        with self.assertRaisesRegex(ValueError, "must use https"):
            ask_assistant("http://example.com", "private-token", "Question")

    def test_turns_unauthorized_response_into_friendly_error(self) -> None:
        def opener(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 401, "Unauthorized", {}, io.BytesIO())

        with self.assertRaisesRegex(RuntimeError, "token was not accepted"):
            ask_assistant("http://127.0.0.1:8787", "wrong", "Question", opener=opener)


if __name__ == "__main__":
    unittest.main()
