from __future__ import annotations

import os
import urllib.parse
import webbrowser
from typing import Callable


DEFAULT_ASSISTANT_URL = "https://pete-ramey-assistant-api.cramey254.workers.dev/"


def assistant_url() -> str:
    value = os.environ.get("DAD_ASSISTANT_URL", DEFAULT_ASSISTANT_URL).strip()
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return DEFAULT_ASSISTANT_URL
    if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        return DEFAULT_ASSISTANT_URL
    return value


def open_assistant(*, opener: Callable[[str], object] = webbrowser.open) -> str:
    """Open the private browser assistant and return the address used."""
    url = assistant_url()
    opener(url)
    return url
