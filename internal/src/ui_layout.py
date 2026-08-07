from __future__ import annotations

from tkinter import BOTH, LEFT, RIGHT, X, ttk

import app
from version import APP_NAME, APP_VERSION, PRODUCT_DESCRIPTION
from watcher_support import FINISHED, INCOMING


def build_ui(window) -> None:
    frame = ttk.Frame(window, padding=20)
    frame.pack(fill=BOTH, expand=True)

    ttk.Label(frame, text=APP_NAME, font=("Segoe UI", 20, "bold")).pack(anchor="w")
    ttk.Label(frame, text=PRODUCT_DESCRIPTION, font=("Segoe UI", 11)).pack(anchor="w", pady=(2, 10))
    ttk.Label(
        frame,
        text="Drop pictures, folders, ZIP, DOCX, or PDF files onto this window or into the folder below. Finished JPEGs open automatically.",
        wraplength=540,
    ).pack(anchor="w", pady=(0, 14))

    folder_box = ttk.LabelFrame(frame, text="Drop folder", padding=12)
    folder_box.pack(fill=X)
    ttk.Label(folder_box, text=str(INCOMING), wraplength=510).pack(anchor="w")

    window.status = ttk.Label(frame, text="Watching for new pictures...")
    window.status.pack(anchor="w", pady=(14, 5))
    window.progress = ttk.Progressbar(frame, mode="indeterminate")
    window.progress.pack(fill=X)

    first_row = ttk.Frame(frame)
    first_row.pack(fill=X, pady=(16, 0))
    ttk.Button(first_row, text="Open Drop Folder", command=lambda: app.open_path(INCOMING)).pack(side=LEFT)
    ttk.Button(first_row, text="Open Finished Pictures", command=lambda: app.open_path(FINISHED)).pack(
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
