from __future__ import annotations

import queue
import threading
from pathlib import Path
from tkinter import Tk, messagebox, ttk

import app
import history_window
import ui_layout
import updater
from update_ui import UpdateMixin
from version import APP_BRAND_TITLE, APP_NAME, APP_VERSION, BRAND_ACRONYM
from watcher_processing import ProcessingSummary, process_sources
from watcher_support import (
    APP_ROOT,
    ARCHIVE,
    FINISHED,
    IGNORED_SUFFIXES,
    INCOMING,
    NEEDS_ATTENTION,
    STABLE_CHECKS_REQUIRED,
    ItemFingerprint,
    Observation,
    acquire_single_instance,
    is_old_enough,
    item_fingerprint,
)


class FolderWatcher(UpdateMixin, Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_BRAND_TITLE} {APP_VERSION}")
        self.geometry("620x415")
        self.minsize(570, 390)
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.observations: dict[Path, Observation] = {}
        self.blocked_items: dict[Path, ItemFingerprint] = {}
        self.busy = False
        self.close_when_idle = False
        self.update_check_running = False
        self.update_install_running = False
        self.pending_update: updater.UpdateInfo | None = None
        self._make_folders()
        widgets = ui_layout.build_ui(self)
        self.status: ttk.Label = widgets.status
        self.progress: ttk.Progressbar = widgets.progress
        self.protocol("WM_DELETE_WINDOW", self.request_close)
        self.after(1000, self._scan)
        self.after(200, self._drain_events)
        self.after(3000, lambda: self.check_for_updates(silent=True))

    def _make_folders(self) -> None:
        for folder in (INCOMING, FINISHED, ARCHIVE, NEEDS_ATTENTION):
            folder.mkdir(parents=True, exist_ok=True)

    def request_close(self) -> None:
        if self.update_install_running:
            messagebox.showinfo(
                APP_BRAND_TITLE,
                f"{APP_NAME} is installing an update. It will close automatically when the update is ready.",
            )
            return
        if self.busy:
            self.close_when_idle = True
            self.status.config(text="Finishing the current pictures before closing...")
            return
        self.destroy()

    def _scan(self) -> None:
        try:
            self._make_folders()
        except OSError:
            self.status.config(text=f"The {APP_NAME} folders could not be opened.")
            self.after(2500, self._scan)
            return

        if not self.busy and not self.update_install_running and not self.close_when_idle:
            ready = self._stable_items()
            if ready:
                self.busy = True
                self.progress.start(12)
                self.status.config(text=f"Processing {len(ready)} item(s)...")
                threading.Thread(target=self._process, args=(ready,), daemon=True).start()
        self.after(2500, self._scan)

    def _stable_items(self) -> list[Path]:
        try:
            present = {
                path
                for path in INCOMING.iterdir()
                if not path.name.startswith(".") and path.suffix.lower() not in IGNORED_SUFFIXES
            }
        except OSError:
            return []

        for missing in set(self.observations) - present:
            self.observations.pop(missing, None)
        for missing in set(self.blocked_items) - present:
            self.blocked_items.pop(missing, None)

        ready: list[Path] = []
        for path in sorted(present, key=lambda item: item.name.casefold()):
            try:
                fingerprint = item_fingerprint(path)
            except OSError:
                self.observations.pop(path, None)
                continue
            if fingerprint is None:
                self.observations.pop(path, None)
                continue

            blocked = self.blocked_items.get(path)
            if blocked is not None:
                if blocked == fingerprint:
                    continue
                self.blocked_items.pop(path, None)

            previous = self.observations.get(path)
            if previous is None or previous.fingerprint != fingerprint:
                self.observations[path] = Observation(fingerprint=fingerprint)
                continue

            previous.unchanged_checks += 1
            if previous.unchanged_checks >= STABLE_CHECKS_REQUIRED and is_old_enough(fingerprint):
                ready.append(path)
                self.observations.pop(path, None)
        return ready

    def _process(self, items: list[Path]) -> None:
        try:
            summary = process_sources(self, items)
        except Exception as exc:
            self.events.put(("processing-error", (items, app.friendly_error(exc))))
        else:
            self.events.put(("done", summary))

    def _send_status(self, text: str) -> None:
        self.events.put(("status", text))

    def show_history(self) -> None:
        history_window.show_history(self, APP_ROOT)

    def _drain_events(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "status":
                    self.status.config(text=str(value))
                elif kind == "done":
                    self._finish(value)
                elif kind == "processing-error":
                    items, error = value
                    self._finish_processing_error(items, str(error))
                elif kind == "update-result":
                    info, silent, error = value
                    self._finish_update_check(info, silent, error)
                elif kind == "update-install-started":
                    self.destroy()
                    return
                elif kind == "update-install-error":
                    self._handle_update_install_error()
        except queue.Empty:
            pass
        self.after(200, self._drain_events)

    def _finish(self, summary: ProcessingSummary) -> None:
        self.busy = False
        self.progress.stop()
        if summary.converted > 0:
            self.status.config(text=f"Done. {summary.converted} JPEG picture(s) saved.")
        else:
            self.status.config(text="No pictures were converted. Check Needs Attention.")

        if self.close_when_idle:
            self.after(100, self.destroy)
            return

        if summary.converted > 0:
            try:
                if len(summary.outputs) == 1:
                    app.open_path(summary.outputs[0])
                elif summary.outputs:
                    app.open_path(FINISHED)
            except OSError:
                messagebox.showinfo(
                    APP_BRAND_TITLE,
                    "The pictures were finished, but Windows could not open the folder automatically.",
                )

        if summary.attention_items:
            messagebox.showwarning(
                APP_BRAND_TITLE,
                f"{summary.attention_items} item(s) need attention. "
                "The originals were kept in the Needs Attention folder.",
            )

        self.offer_pending_update()

    def _finish_processing_error(self, items: list[Path], error: str) -> None:
        self.busy = False
        self.progress.stop()
        for source in items:
            self.observations.pop(source, None)
            try:
                fingerprint = item_fingerprint(source)
            except OSError:
                fingerprint = None
            if fingerprint is not None:
                self.blocked_items[source] = fingerprint

        self.status.config(text="Processing stopped unexpectedly. The originals were left in the drop folder.")
        if self.close_when_idle:
            self.after(100, self.destroy)
            return
        messagebox.showerror(
            APP_BRAND_TITLE,
            f"{APP_NAME} could not finish the current job. No originals were deleted.\n\n{error}",
        )


def show_already_running_message() -> None:
    root = Tk()
    root.withdraw()
    messagebox.showinfo(
        APP_BRAND_TITLE,
        f"{APP_NAME} ({BRAND_ACRONYM}) is already running.",
        parent=root,
    )
    root.destroy()


def main() -> None:
    if not acquire_single_instance():
        show_already_running_message()
        return
    window = FolderWatcher()
    if not updater.confirm_startup():
        window.destroy()
        return
    window.mainloop()


if __name__ == "__main__":
    main()
