from __future__ import annotations

import threading
from tkinter import messagebox

import updater
from version import APP_DISPLAY_NAME, APP_NAME, APP_VERSION


class UpdateMixin:
    update_check_running: bool

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

    def _finish_update_check(self, info: updater.UpdateInfo | None, silent: bool, error: str | None) -> None:
        self.update_check_running = False
        if error:
            if not silent:
                messagebox.showinfo(
                    APP_DISPLAY_NAME,
                    "The update check could not be completed. The program will keep working normally.",
                )
            self.status.config(text="Watching for new pictures...")
            return

        if info is None:
            if not silent:
                messagebox.showinfo(APP_DISPLAY_NAME, f"{APP_NAME} is already up to date.")
            self.status.config(text="Watching for new pictures...")
            return

        install = messagebox.askyesno(
            f"{APP_DISPLAY_NAME} Update",
            f"A new version of {APP_NAME} is available.\n\n"
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

    def _install_update_worker(self, info: updater.UpdateInfo) -> None:
        try:
            updater.install_update(info)
            self.events.put(("update-install-started", None))
        except Exception:
            self.events.put(("update-install-error", None))

    def _handle_update_install_error(self) -> None:
        self.progress.stop()
        self.status.config(text="Update could not be installed.")
        messagebox.showerror(
            APP_DISPLAY_NAME,
            "The update could not be installed. The current version will keep working.",
        )
