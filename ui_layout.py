from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tkinter import BOTH, LEFT, RIGHT, X, Misc, messagebox, ttk

import app
from version import APP_VERSION
from watcher_support import FINISHED, INCOMING


@dataclass(frozen=True)
class MainWidgets:
    status: ttk.Label
    progress: ttk.Progressbar


def open_folder(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        app.open_path(path)
    except OSError:
        messagebox.showerror(
            "Dad Image Tool",
            "Windows could not open that folder. The files were not changed.",
        )


def build_ui(window: Misc) -> MainWidgets:
    frame = ttk.Frame(window, padding=20)
    frame.pack(fill=BOTH, expand=True)
    ttk.Label(frame, text="Dad Image Tool", font=("Segoe UI", 20, "bold")).pack(anchor="w")
    ttk.Label(
        frame,
        text="Save client pictures, folders, or ZIP files in the drop folder. Everything else is automatic.",
        wraplength=540,
    ).pack(anchor="w", pady=(5, 14))

    folder_box = ttk.LabelFrame(frame, text="Watched folder", padding=12)
    folder_box.pack(fill=X)
    ttk.Label(folder_box, text=str(INCOMING), wraplength=510).pack(anchor="w")

    status = ttk.Label(frame, text="Watching for new pictures...")
    status.pack(anchor="w", pady=(14, 5))
    progress = ttk.Progressbar(frame, mode="indeterminate")
    progress.pack(fill=X)

    first_row = ttk.Frame(frame)
    first_row.pack(fill=X, pady=(16, 0))
    ttk.Button(first_row, text="Open Drop Folder", command=lambda: open_folder(INCOMING)).pack(side=LEFT)
    ttk.Button(first_row, text="Open Finished Pictures", command=lambda: open_folder(FINISHED)).pack(
        side=LEFT, padx=(8, 0)
    )

    second_row = ttk.Frame(frame)
    second_row.pack(fill=X, pady=(8, 0))
    ttk.Button(second_row, text="View History", command=window.show_history).pack(side=LEFT)
    ttk.Button(
        second_row,
        text="Check for Updates",
        command=lambda: window.check_for_updates(silent=False),
    ).pack(side=RIGHT)
    ttk.Label(frame, text=f"Version {APP_VERSION}").pack(anchor="e", pady=(10, 0))
    return MainWidgets(status=status, progress=progress)
