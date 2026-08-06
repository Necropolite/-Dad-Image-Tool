from __future__ import annotations

import threading
from tkinter import messagebox

import updater
from version import APP_VERSION


class UpdateMixin:
    busy: bool
    update_check_running: bool
    update_install_running: bool
    pending_update: updater.UpdateInfo | None

    def check_for_updates(self, silent: bool) -> None:
        if self.update_check_running or self.update_install_running:
            return
        if self.busy:
            if silent:
                self.after(15_000, lambda: self.check_for_updates(silent=True))
            else:
                messagebox.showinfo(
                    "Dad Image Tool",
                    "Dad Image Tool is processing pictures. Check for updates after it finishes.",
                )
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
                    "Dad Image Tool",
                    "The update check could not be completed. The program will keep working normally.",
                )
            if not self.busy:
                self.status.config(text="Watching for new pictures...")
            return

        if info is None:
            if not silent:
                messagebox.showinfo("Dad Image Tool", "Dad Image Tool is already up to date.")
            if not self.busy:
                self.status.config(text="Watching for new pictures...")
            return

        if self.busy:
            self.pending_update = info
            self.status.config(text="An update is ready. It will be offered after the current pictures finish.")
            return

        self._offer_update(info)

    def offer_pending_update(self) -> None:
        if self.busy or self.update_install_running or self.pending_update is None:
            return
        info = self.pending_update
        self.pending_update = None
        self.after(250, lambda: self._offer_update(info))

    def _offer_update(self, info: updater.UpdateInfo) -> None:
        if self.busy:
            self.pending_update = info
            return
        if self.update_install_running:
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

        self.update_install_running = True
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
        self.update_install_running = False
        self.progress.stop()
        self.status.config(text="Update could not be installed.")
        messagebox.showerror(
            "Dad Image Tool",
            "The update could not be installed. The current version will keep working.",
        )
