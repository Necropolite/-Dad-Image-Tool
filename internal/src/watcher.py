from __future__ import annotations

import queue
import threading
from pathlib import Path
from tkinter import Tk, messagebox

import app
import history_window
import ui_layout
import updater
from update_ui import UpdateMixin
from version import APP_DISPLAY_NAME, APP_NAME, APP_VERSION, BRAND_FULL_NAME, BRAND_NAME, PRODUCT_DESCRIPTION, TAGLINE
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
    item_fingerprint,
)


class FolderWatcher(UpdateMixin, Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("590x390")
        self.minsize(540, 370)
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.observations: dict[Path, Observation] = {}
        self.blocked_items: dict[Path, ItemFingerprint] = {}
        self.busy = False
        self.update_check_running = False
        self._make_folders()
        ui_layout.build_ui(self)
        self.after(1000, self._scan)
        self.after(200, self._drain_events)
        self.after(3000, lambda: self.check_for_updates(silent=True))

    def _make_folders(self) -> None:
        for folder in (INCOMING, FINISHED, ARCHIVE, NEEDS_ATTENTION):
            folder.mkdir(parents=True, exist_ok=True)

    def _scan(self) -> None:
        if not self.busy:
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
            if previous.unchanged_checks >= STABLE_CHECKS_REQUIRED:
                ready.append(path)
                self.observations.pop(path, None)
        return ready

    def _process(self, items: list[Path]) -> None:
        self.events.put(("done", process_sources(self, items)))

    def _send_status(self, text: str) -> None:
        self.events.put(("status", text))

    def show_history(self) -> None:
        history_window.show_history(self, APP_ROOT)

    def show_about(self) -> None:
        messagebox.showinfo(
            f"About {APP_NAME}",
            f"{APP_NAME} version {APP_VERSION}\n{PRODUCT_DESCRIPTION}\n\n"
            f"D.A.D. is a secondary nickname:\n{BRAND_FULL_NAME}\n{TAGLINE}",
            parent=self,
        )

    def _drain_events(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "status":
                    self.status.config(text=str(value))
                elif kind == "done":
                    self._finish(value)
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
            if len(summary.outputs) == 1:
                app.open_path(summary.outputs[0])
            elif summary.outputs:
                app.open_path(FINISHED)
        else:
            self.status.config(text="No pictures were converted. Check Needs Attention.")

        if summary.attention_items:
            messagebox.showwarning(
                APP_DISPLAY_NAME,
                f"{summary.attention_items} item(s) need attention. The originals were kept in the Needs Attention folder.",
            )


def show_already_running_message() -> None:
    root = Tk()
    root.withdraw()
    messagebox.showinfo(APP_DISPLAY_NAME, f"{APP_NAME} is already running.", parent=root)
    root.destroy()


def main() -> None:
    if not acquire_single_instance():
        show_already_running_message()
        return
    updater.cleanup_stale_update_files()
    FolderWatcher().mainloop()


if __name__ == "__main__":
    main()
