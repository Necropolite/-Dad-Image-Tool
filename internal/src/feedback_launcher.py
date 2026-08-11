from __future__ import annotations

import os
import urllib.parse
import webbrowser
from typing import Callable


DEFAULT_FEEDBACK_URL = (
    "https://github.com/Necropolite/-Dad-Image-Tool/issues/new"
    "?template=dad-feedback.yml"
)


def feedback_url() -> str:
    """Return the configured feedback form URL, falling back to the project form."""
    value = os.environ.get("DAD_FEEDBACK_URL", DEFAULT_FEEDBACK_URL).strip()
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc:
        return DEFAULT_FEEDBACK_URL
    return value


def open_feedback(*, opener: Callable[[str], object] = webbrowser.open) -> str:
    """Open Dad's plain-language feedback form and return the address used."""
    url = feedback_url()
    opener(url)
    return url
