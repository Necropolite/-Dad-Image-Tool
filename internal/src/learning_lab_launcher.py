from __future__ import annotations

import sys
import webbrowser
from pathlib import Path
from typing import Callable


def learning_lab_path() -> Path:
    """Return the bundled Learning Lab entry page for source or packaged runs."""
    if getattr(sys, "frozen", False):
        root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        return root / "learning_lab" / "index.html"
    return Path(__file__).resolve().parents[1] / "learning_lab" / "index.html"


def open_learning_lab(*, opener: Callable[[str], object] = webbrowser.open) -> str:
    """Open the bundled experimental Learning Lab and return the URI used."""
    page = learning_lab_path()
    if not page.is_file():
        raise FileNotFoundError(f"Learning Lab files were not found at {page}")
    uri = page.resolve().as_uri()
    opener(uri)
    return uri
