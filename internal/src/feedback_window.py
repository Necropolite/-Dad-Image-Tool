from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from tkinter import BOTH, LEFT, RIGHT, X, StringVar, Toplevel, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from version import APP_VERSION


FEEDBACK_ENDPOINT = "https://pete-ramey-assistant-api.cramey254.workers.dev/api/feedback"


def submit_feedback(message: str, *, opener=urllib.request.urlopen) -> dict[str, object]:
    if not message.strip():
        raise ValueError("Type some feedback first.")
    payload = json.dumps({"message": message, "appVersion": APP_VERSION, "source": "Dad Image Tool"}).encode("utf-8")
    request = urllib.request.Request(
        FEEDBACK_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with opener(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Feedback could not be recorded right now.") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("Feedback could not be recorded. Check the internet connection.") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Feedback could not be recorded right now.") from exc
    if not isinstance(data, dict) or not data.get("ok"):
        raise RuntimeError("Feedback could not be recorded right now.")
    return data


class FeedbackWindow(Toplevel):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.title("Feedback")
        self.geometry("520x360")
        self.minsize(460, 320)
        self.transient(parent)
        self.status = StringVar(value="Write anything you want us to know. It will be recorded exactly as feedback.")

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Feedback", font=("Segoe UI", 17, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text="Report a problem, suggest an idea, correct something, or just leave a note.",
            wraplength=475,
        ).pack(anchor="w", pady=(3, 10))
        self.message = ScrolledText(frame, height=10, wrap="word", font=("Segoe UI", 10))
        self.message.pack(fill=BOTH, expand=True)
        ttk.Label(frame, textvariable=self.status, wraplength=475).pack(anchor="w", pady=(8, 8))
        actions = ttk.Frame(frame)
        actions.pack(fill=X)
        self.submit_button = ttk.Button(actions, text="Submit Feedback", command=self.submit)
        self.submit_button.pack(side=LEFT)
        ttk.Button(actions, text="Cancel", command=self.destroy).pack(side=RIGHT)
        self.message.focus_set()

    def submit(self) -> None:
        text = self.message.get("1.0", "end-1c")
        if not text.strip():
            self.status.set("Type some feedback first.")
            return
        self.submit_button.configure(state="disabled")
        self.status.set("Recording feedback...")
        threading.Thread(target=self._send, args=(text,), daemon=True).start()

    def _send(self, text: str) -> None:
        try:
            submit_feedback(text)
        except Exception as exc:
            self.after(0, self._failed, str(exc))
        else:
            self.after(0, self._succeeded)

    def _failed(self, message: str) -> None:
        self.submit_button.configure(state="normal")
        self.status.set(message)

    def _succeeded(self) -> None:
        messagebox.showinfo("Feedback", "Feedback recorded. Thank you.", parent=self)
        self.destroy()


def show_feedback(parent) -> None:
    existing = getattr(parent, "feedback_window", None)
    if existing is not None and existing.winfo_exists():
        existing.lift()
        existing.focus_force()
        return
    parent.feedback_window = FeedbackWindow(parent)
