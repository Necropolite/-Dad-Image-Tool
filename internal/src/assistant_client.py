from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable


DEFAULT_ASSISTANT_URL = "http://127.0.0.1:8787"


@dataclass(frozen=True)
class AssistantReply:
    answer: str
    citations: list[dict[str, object]]


def ask_assistant(
    endpoint: str,
    token: str,
    question: str,
    history: list[dict[str, str]] | None = None,
    *,
    opener: Callable[..., object] = urllib.request.urlopen,
) -> AssistantReply:
    """Ask the private Pete assistant without persisting credentials or conversation data."""
    endpoint = endpoint.strip().rstrip("/")
    token = token.strip()
    question = question.strip()
    if not endpoint.startswith(("http://", "https://")):
        raise ValueError("Assistant address must begin with http:// or https://.")
    parsed_endpoint = urllib.parse.urlsplit(endpoint)
    if parsed_endpoint.scheme == "http" and parsed_endpoint.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("A remote assistant address must use https:// to protect the private token.")
    if not token:
        raise ValueError("Enter the private access token.")
    if not question:
        raise ValueError("Enter a question for Pete's assistant.")

    payload = json.dumps({"message": question, "history": history or []}).encode("utf-8")
    request = urllib.request.Request(
        f"{endpoint}/api/chat",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with opener(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            raise RuntimeError("The private access token was not accepted.") from exc
        raise RuntimeError(f"The assistant returned an error ({exc.code}).") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Could not reach the private assistant. Check that its address is correct and it is running."
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("The assistant returned an unreadable response.") from exc

    if not isinstance(data, dict):
        raise RuntimeError("The assistant returned an unexpected response.")
    if data.get("error"):
        raise RuntimeError(str(data["error"]))
    answer = data.get("answer")
    citations = data.get("citations", [])
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("The assistant did not return an answer.")
    if not isinstance(citations, list):
        citations = []
    return AssistantReply(answer=answer.strip(), citations=[item for item in citations if isinstance(item, dict)])
