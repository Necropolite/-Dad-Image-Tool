from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class HistoryEntry:
    completed_at: str
    source_names: list[str]
    converted: int
    errors: int
    status: str
    output_folder: str | None
    error_messages: list[str] = field(default_factory=list)


def history_file(app_root: Path) -> Path:
    return app_root / "job-history.jsonl"


def record_job(
    app_root: Path,
    source_names: list[str],
    converted: int,
    errors: int | list[str],
    output_folder: Path | None,
) -> HistoryEntry:
    if isinstance(errors, int):
        error_count = errors
        error_messages: list[str] = []
    else:
        error_messages = [str(message) for message in errors if str(message).strip()]
        error_count = len(error_messages)

    status = "Completed" if converted > 0 and error_count == 0 else "Needs attention"
    entry = HistoryEntry(
        completed_at=datetime.now().isoformat(timespec="seconds"),
        source_names=[Path(name).name for name in source_names if name],
        converted=converted,
        errors=error_count,
        status=status,
        output_folder=str(output_folder) if output_folder else None,
        error_messages=error_messages,
    )
    app_root.mkdir(parents=True, exist_ok=True)
    with history_file(app_root).open("a", encoding="utf-8") as file:
        file.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
    return entry


def load_history(app_root: Path, limit: int = 100) -> list[HistoryEntry]:
    path = history_file(app_root)
    if not path.exists():
        return []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    entries: list[HistoryEntry] = []
    for line in lines:
        try:
            data = json.loads(line)
            raw_errors = data.get("errors", 0)
            if isinstance(raw_errors, list):
                messages = [str(message) for message in raw_errors]
                data["errors"] = len(messages)
                data.setdefault("error_messages", messages)
            else:
                data["errors"] = int(raw_errors or 0)
                data.setdefault("error_messages", [])
            entries.append(HistoryEntry(**data))
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
    return entries[-limit:][::-1]


def display_name(entry: HistoryEntry) -> str:
    names = [Path(name).name for name in entry.source_names if name]
    if not names:
        return "Unnamed job"
    if len(names) == 1:
        return names[0]
    return f"{names[0]} and {len(names) - 1} more"
