from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tkinter import BOTH, Misc, Toplevel, messagebox, ttk

import app
import history


def _completed_text(entry: history.HistoryEntry) -> str:
    try:
        return datetime.fromisoformat(entry.completed_at).strftime("%b %d, %Y %I:%M %p")
    except ValueError:
        return entry.completed_at


def _populate_tree(
    tree: ttk.Treeview,
    entries: list[history.HistoryEntry],
) -> dict[str, history.HistoryEntry]:
    row_entries: dict[str, history.HistoryEntry] = {}
    for entry in entries:
        row_id = tree.insert(
            "",
            "end",
            values=(
                _completed_text(entry),
                history.display_name(entry),
                entry.converted,
                entry.errors,
                entry.status,
            ),
        )
        row_entries[row_id] = entry
    if not entries:
        tree.insert("", "end", values=("", "No jobs have been processed yet.", "", "", ""))
    return row_entries


def _open_entry(entry: history.HistoryEntry, window: Toplevel) -> None:
    if entry.output_folder:
        path = Path(entry.output_folder)
        if path.exists():
            try:
                app.open_path(path)
                return
            except OSError:
                messagebox.showinfo(
                    "Dad Image Tool",
                    "Windows could not open the finished folder. The files were not changed.",
                    parent=window,
                )
                return
    if entry.error_messages:
        messagebox.showinfo("Dad Image Tool", "\n".join(entry.error_messages[:5]), parent=window)


def show_history(parent: Misc, app_root: Path) -> None:
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

    row_entries = _populate_tree(tree, history.load_history(app_root))

    def open_selected(_event=None) -> None:
        selected = tree.selection()
        if not selected:
            return
        entry = row_entries.get(selected[0])
        if entry is not None:
            _open_entry(entry, window)

    tree.bind("<Double-1>", open_selected)
    ttk.Label(
        frame,
        text="Double-click a job to open its finished folder or view the problem.",
    ).pack(anchor="w", pady=(8, 0))
