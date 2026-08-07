from __future__ import annotations

from tkinter import Tk, messagebox

from tkinterdnd2 import DND_FILES, TkinterDnD

import drop_intake
from version import APP_DISPLAY_NAME


def enable_window_file_drop(window) -> None:
    """Register the whole application window as a native Windows file-drop target."""
    TkinterDnD.require(window)
    window.drop_target_register(DND_FILES)
    window.dnd_bind("<<Drop>>", lambda event: _handle_drop(window, event))


def _handle_drop(window, event) -> None:
    paths = window.tk.splitlist(event.data)
    result = drop_intake.queue_paths(paths)

    if result.queued:
        count = len(result.queued)
        noun = "item" if count == 1 else "items"
        window.status.config(text=f"Added {count} {noun}. Processing will start automatically.")

    if result.errors:
        messagebox.showwarning(
            APP_DISPLAY_NAME,
            "\n".join(result.errors),
            parent=window,
        )


def verify_runtime() -> None:
    """Load TkDnD in a real Tk interpreter so packaged builds prove the native extension is present."""
    root = Tk()
    root.withdraw()
    try:
        TkinterDnD.require(root)
    finally:
        root.destroy()
