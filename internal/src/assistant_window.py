from __future__ import annotations

import os
import threading
from tkinter import BOTH, END, LEFT, RIGHT, X, StringVar, Toplevel, ttk
from tkinter.scrolledtext import ScrolledText

from assistant_client import DEFAULT_ASSISTANT_URL, AssistantReply, ask_assistant


def _citation_label(citation: dict[str, object]) -> str:
    metadata = citation.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    source_id = citation.get("id", "?")
    title = metadata.get("knowledge_id") or citation.get("source") or "Knowledge Core source"
    details = [metadata.get("original_date"), metadata.get("status"), metadata.get("currency")]
    suffix = " · ".join(str(value) for value in details if value)
    return f"[{source_id}] {title}" + (f" — {suffix}" if suffix else "")


class AssistantWindow(Toplevel):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.title("Ask Pete (Experimental)")
        self.geometry("720x650")
        self.minsize(600, 520)
        self.transient(parent)
        self.history: list[dict[str, str]] = []
        self.endpoint = StringVar(value=os.environ.get("DAD_ASSISTANT_URL", DEFAULT_ASSISTANT_URL))
        self.token = StringVar(value=os.environ.get("DAD_ASSISTANT_TOKEN", ""))
        self.status_text = StringVar(value="Ready. Questions and answers are not saved by Dad Image Tool.")
        self._build()
        self.question.focus_set()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="Ask Pete", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text="Experimental private assistant. Verify important details against the cited Knowledge Core sources.",
            wraplength=660,
        ).pack(anchor="w", pady=(2, 10))

        connection = ttk.LabelFrame(frame, text="Private connection", padding=10)
        connection.pack(fill=X)
        ttk.Label(connection, text="Assistant address").grid(row=0, column=0, sticky="w")
        ttk.Entry(connection, textvariable=self.endpoint).grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ttk.Label(connection, text="Access token").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(connection, textvariable=self.token, show="•").grid(
            row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0)
        )
        connection.columnconfigure(1, weight=1)

        self.conversation = ScrolledText(frame, height=15, wrap="word", state="disabled", font=("Segoe UI", 10))
        self.conversation.pack(fill=BOTH, expand=True, pady=(12, 8))

        ttk.Label(frame, text="Question").pack(anchor="w")
        self.question = ScrolledText(frame, height=4, wrap="word", font=("Segoe UI", 10))
        self.question.pack(fill=X, pady=(3, 8))
        self.question.bind("<Control-Return>", lambda _event: self.ask())

        actions = ttk.Frame(frame)
        actions.pack(fill=X)
        self.ask_button = ttk.Button(actions, text="Ask", command=self.ask)
        self.ask_button.pack(side=LEFT)
        ttk.Button(actions, text="Clear Conversation", command=self.clear).pack(side=LEFT, padx=(8, 0))
        ttk.Button(actions, text="Close", command=self.destroy).pack(side=RIGHT)
        ttk.Label(frame, textvariable=self.status_text, wraplength=660).pack(anchor="w", pady=(9, 0))

    def _append(self, speaker: str, text: str) -> None:
        self.conversation.configure(state="normal")
        self.conversation.insert(END, f"{speaker}\n{text.strip()}\n\n")
        self.conversation.configure(state="disabled")
        self.conversation.see(END)

    def ask(self) -> None:
        question = self.question.get("1.0", END).strip()
        if not question:
            self.status_text.set("Enter a question first.")
            return
        endpoint = self.endpoint.get()
        token = self.token.get()
        self.question.delete("1.0", END)
        self._append("You", question)
        self.ask_button.configure(state="disabled")
        self.status_text.set("Searching Pete's private Knowledge Core...")
        history = list(self.history[-8:])
        threading.Thread(
            target=self._request,
            args=(endpoint, token, question, history),
            daemon=True,
        ).start()

    def _request(
        self,
        endpoint: str,
        token: str,
        question: str,
        history: list[dict[str, str]],
    ) -> None:
        try:
            reply = ask_assistant(endpoint, token, question, history)
        except Exception as exc:
            self.after(0, self._finish_error, str(exc))
            return
        self.after(0, self._finish_reply, question, reply)

    def _finish_reply(self, question: str, reply: AssistantReply) -> None:
        citation_text = "\n".join(_citation_label(item) for item in reply.citations)
        display = reply.answer
        if citation_text:
            display += f"\n\nSources\n{citation_text}"
        self._append("Pete Assistant", display)
        self.history.extend(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": reply.answer},
            ]
        )
        self.history = self.history[-8:]
        self.ask_button.configure(state="normal")
        self.status_text.set(f"Answered with {len(reply.citations)} cited source passage(s).")

    def _finish_error(self, message: str) -> None:
        self._append("Assistant error", message)
        self.ask_button.configure(state="normal")
        self.status_text.set(message)

    def clear(self) -> None:
        self.history.clear()
        self.conversation.configure(state="normal")
        self.conversation.delete("1.0", END)
        self.conversation.configure(state="disabled")
        self.status_text.set("Conversation cleared. Nothing was saved.")


def show_assistant(parent) -> None:
    existing = getattr(parent, "assistant_window", None)
    if existing is not None and existing.winfo_exists():
        existing.lift()
        existing.focus_force()
        return
    parent.assistant_window = AssistantWindow(parent)

