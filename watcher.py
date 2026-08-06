from __future__ import annotations

import queue
import shutil
import threading
from datetime import datetime
from pathlib import Path
from tkinter import BOTH, LEFT, RIGHT, X, messagebox, ttk

import app
import updater
from tkinterdnd2 import DND_FILES, TkinterDnD
from version import APP_VERSION

APP_ROOT = Path.home() / "Pictures" / "Dad Image Tool"
INCOMING = APP_ROOT / "Drop Client Pictures Here"
FINISHED = APP_ROOT / "Finished"
ARCHIVE = APP_ROOT / "Originals Archive"
NEEDS_ATTENTION = APP_ROOT / "Needs Attention"
IGNORED_SUFFIXES = {".crdownload", ".download", ".part", ".tmp"}


class FolderWatcher(TkinterDnD.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"Dad Image Tool {APP_VERSION}")
        self.geometry("560x350")
        self.minsize(500, 320)
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.known_sizes: dict[Path, int] = {}
        self.busy = False
        self.update_check_running = False
        self._make_folders()
        self._build_ui()
        self.after(1000, self._scan)
        self.after(200, self._drain_events)
        self.after(2500, lambda: self.check_for_updates(silent=True))

    def _make_folders(self) -> None:
        for folder in (INCOMING, FINISHED, ARCHIVE, NEEDS_ATTENTION):
            folder.mkdir(parents=True, exist_ok=True)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Dad Image Tool", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text="Save client pictures, folders, or ZIP files in the drop folder. They will be converted automatically.",
            wraplength=510,
        ).pack(anchor="w", pady=(5, 14))

        self.drop = ttk.Label(
            frame,
            text="Drop Client Pictures Here",
            anchor="center",
            relief="groove",
            padding=28,
        )
        self.drop.pack(fill=X)
        self.drop.drop_target_register(DND_FILES)
        self.drop.dnd_bind("<<Drop>>", self._on_drop)

        self.status = ttk.Label(frame, text="Watching for new pictures...")
        self.status.pack(anchor="w", pady=(14, 5))
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill=X)

        buttons = ttk.Frame(frame)
        buttons.pack(fill=X, pady=(16, 0))
        ttk.Button(buttons, text="Open Drop Folder", command=lambda: app.open_path(INCOMING)).pack(side=LEFT)
        ttk.Button(buttons, text="Open Finished Pictures", command=lambda: app.open_path(FINISHED)).pack(side=LEFT, padx=(8, 0))
        ttk.Button(buttons, text="Check for Updates", command=lambda: self.check_for_updates(silent=False)).pack(side=RIGHT)

        ttk.Label(frame, text=f"Version {APP_VERSION}").pack(anchor="e", pady=(10, 0))

    def _on_drop(self, event: object) -> None:
        for value in self.tk.splitlist(getattr(event, "data", "")):
            source = Path(value)
            if source.exists():
                copy_target(source, INCOMING)
        self._scan()

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
        ready: list[Path] = []
        present = {path for path in INCOMING.iterdir() if not path.name.startswith(".")}
        for missing in set(self.known_sizes) - present:
            self.known_sizes.pop(missing, None)

        for path in sorted(present):
            if path.suffix.lower() in IGNORED_SUFFIXES:
                continue
            try:
                size = item_size(path)
            except OSError:
                continue
            previous = self.known_sizes.get(path)
            self.known_sizes[path] = size
            if previous is not None and previous == size:
                ready.append(path)
        return ready

    def _process(self, items: list[Path]) -> None:
        result = app.process_items([str(path) for path in items], FINISHED, self._send_status)
        destination = ARCHIVE if result.converted and not result.errors else NEEDS_ATTENTION
        for path in items:
            self.known_sizes.pop(path, None)
            if path.exists():
                move_target(path, destination)
        self.events.put(("done", result))

    def _send_status(self, text: str) -> None:
        self.events.put(("status", text))

    def check_for_updates(self, silent: bool) -> None:
        if self.update_check_running:
            return
        self.update_check_running = True
        if not silent:
            self.status.config(text="Checking for updates...")
        threading.Thread(target=self._update_worker, args=(silent,), daemon=True).start()

    def _update_worker(self, silent: bool) -> None:
        try:
            info = updater.check_for_update()
            self.events.put(("update-result", (info, silent, None)))
        except Exception as exc:
            self.events.put(("update-result", (None, silent, str(exc))))

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
        except queue.Empty:
            pass
        self.after(200, self._drain_events)

    def _finish(self, result: app.JobResult) -> None:
        self.busy = False
        self.progress.stop()
        if result.converted:
            self.status.config(text=f"Done. {result.converted} JPEG picture(s) saved.")
            if result.output_dir:
                app.open_path(result.output_dir)
        else:
            self.status.config(text="No pictures were converted. Check Needs Attention.")
            messagebox.showwarning(
                "Dad Image Tool",
                "The item could not be converted. It was moved to the Needs Attention folder.",
            )

    def _finish_update_check(self, info, silent: bool, error: str | None) -> None:
        self.update_check_running = False
        if error:
            if not silent:
                messagebox.showinfo(
                    "Dad Image Tool",
                    "The update check could not be completed. The program will keep working normally.",
                )
            self.status.config(text="Watching for new pictures...")
            return

        if info is None:
            if not silent:
                messagebox.showinfo("Dad Image Tool", "Dad Image Tool is already up to date.")
            self.status.config(text="Watching for new pictures...")
            return

        install = messagebox.askyesno(
            "Dad Image Tool Update",
            f"A new version of Dad Image Tool is available.\n\n"
            f"Installed: {APP_VERSION}\n"
            f"Available: {info.version}\n\n"
            "Install it now?",
        )
        if not install:
            self.status.config(text="Update available. It can be installed later.")
            return

        self.status.config(text="Downloading update...")
        self.progress.start(12)
        threading.Thread(target=self._install_update_worker, args=(info,), daemon=True).start()

    def _install_update_worker(self, info) -> None:
        try:
            updater.install_update(info)
            self.events.put(("update-install-started", None))
        except Exception as exc:
            self.events.put(("update-install-error", str(exc)))

    def _handle_update_install_started(self) -> None:
        self.destroy()

    def _handle_update_install_error(self) -> None:
        self.progress.stop()
        self.status.config(text="Update could not be installed.")
        messagebox.showerror(
            "Dad Image Tool",
            "The update could not be installed. The current version will keep working.",
        )


def item_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def unique_destination(folder: Path, name: str) -> Path:
    target = folder / name
    if not target.exists():
        return target
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return folder / f"{Path(name).stem}-{stamp}{Path(name).suffix}"


def copy_target(source: Path, folder: Path) -> None:
    target = unique_destination(folder, source.name)
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)


def move_target(source: Path, folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(unique_destination(folder, source.name)))


def main() -> None:
    window = FolderWatcher()

    original_drain = window._drain_events

    def drain_with_update_events() -> None:
        try:
            while True:
                kind, value = window.events.get_nowait()
                if kind == "update-install-started":
                    window._handle_update_install_started()
                    return
                if kind == "update-install-error":
                    window._handle_update_install_error()
                    continue
                window.events.put((kind, value))
                break
        except queue.Empty:
            pass
        original_drain()

    window._drain_events = drain_with_update_events  # type: ignore[method-assign]
    window.mainloop()


if __name__ == "__main__":
    main()
