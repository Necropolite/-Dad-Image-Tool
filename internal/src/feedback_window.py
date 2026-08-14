from __future__ import annotations

from tkinter import BOTH, RIGHT, X, StringVar, Toplevel, ttk


FEEDBACK_DISABLED_MESSAGE = (
    "Feedback is temporarily unavailable while its secure delivery system is being updated. "
    "No feedback or account information has been sent."
)


def submit_feedback(message: str, *, opener=None) -> dict[str, object]:
    if not message.strip():
        raise ValueError("Type some feedback first.")
    raise RuntimeError(FEEDBACK_DISABLED_MESSAGE)


class FeedbackWindow(Toplevel):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.title("Feedback")
        self.geometry("520x220")
        self.minsize(460, 200)
        self.transient(parent)
        self.status = StringVar(value=FEEDBACK_DISABLED_MESSAGE)

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Feedback", font=("Segoe UI", 17, "bold")).pack(anchor="w")
        ttk.Label(frame, textvariable=self.status, wraplength=475).pack(anchor="w", pady=(10, 16))
        actions = ttk.Frame(frame)
        actions.pack(fill=X)
        ttk.Button(actions, text="Close", command=self.destroy).pack(side=RIGHT)

    def submit(self) -> None:
        self.status.set(FEEDBACK_DISABLED_MESSAGE)

    def _send(self, text: str) -> None:
        self.after(0, self._failed, FEEDBACK_DISABLED_MESSAGE)

    def _failed(self, message: str) -> None:
        self.status.set(message)

    def _succeeded(self) -> None:
        self.status.set(FEEDBACK_DISABLED_MESSAGE)


def show_feedback(parent) -> None:
    existing = getattr(parent, "feedback_window", None)
    if existing is not None and existing.winfo_exists():
        existing.lift()
        existing.focus_force()
        return
    parent.feedback_window = FeedbackWindow(parent)
