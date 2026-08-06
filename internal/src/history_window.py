from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tkinter import BOTH, Toplevel, messagebox, ttk

import app
import history


def show_history(parent, app_root: Path) -> None:
    window = Toplevel(parent)
    window.title("Dad Image Tool History")
    window.geometry("800x390")
    window.minsize(690, 330)

    frame = ttk.Frame(window, padding=14)
    frame.pack(fill=BOTH, expand=True)
    ttk.Label(frame, text="Recent Jobs", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

    tree = ttk.Treeview(frame, columns=("time", "job", "pictures", "errors", "status"), show="headings", height=12)
    for column, text in (
        ("time", "Completed"),
        ("job", "Source"),
        ("pictures", "JPEGs"),
        ("errors", "Errors"),
        ("status", "Status"),
    ):
        tree.heading(column, text=text)
    tree.column("time", width=155, anchor="w")
    tree.column("job", width=295, anchor="w")
    tree.column("pictures", width=65, anchor="center")
    tree.column("errors", width=60, anchor="center")
    tree.column("status", width=125, anchor="w")
    tree.pack(fill=BOTH, expand=True)

    row_entries: dict[str, history.HistoryEntry] = {}
    entries = history.load_history(app_root)
    for entry in entries:
        try:
            completed = datetime.fromisoformat(entry.completed_at).strftime("%b %d, %Y %I:%M %p")
        except ValueError:
            completed = entry.completed_at
        row_id = tree.insert(
            "",
            "end",
            values=(completed, history.display_name(entry), entry.converted, entry.errors, entry.status),
        )
        row_entries[row_id] = entry

    if not entries:
        tree.insert("", "end", values=("", "No jobs have been processed yet.", "", "", ""))

    def open_selected(_event=None) -> None:
        selected = tree.selection()
        if not selected:
            return
        entry = row_entries.get(selected[0])
        if entry is None:
            return
        if entry.output_folder:
            path = Path(entry.output_folder)
            if path.exists():
                app.open_path(path)
                return
        if entry.error_messages:
            messagebox.showinfo("Dad Image Tool", "\n".join(entry.error_messages[:5]), parent=window)

    tree.bind("<Double-1>", open_selected)
    ttk.Label(frame, text="Double-click a completed job to open its finished folder.").pack(anchor="w", pady=(8, 0))
