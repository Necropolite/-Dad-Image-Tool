from __future__ import annotations

import json
from dataclasses import asdict, dataclass
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


def history_file(app_root: Path) -> Path:
    return app_root / "job-history.jsonl"


def record_job(
    app_root: Path,
    source_names: list[str],
    converted: int,
    errors: int,
    output_folder: Path | None,
) -> HistoryEntry:
    status = "Completed" if converted > 0 and errors == 0 else "Needs attention"
    entry = HistoryEntry(
        completed_at=datetime.now().isoformat(timespec="seconds"),
        source_names=source_names,
        converted=converted,
        errors=errors,
        status=status,
        output_folder=str(output_folder) if output_folder else None,
    )
    app_root.mkdir(parents=True, exist_ok=True)
    with history_file(app_root).open("a", encoding="utf-8") as file:
        file.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
    return entry


def load_history(app_root: Path, limit: int = 100) -> list[HistoryEntry]:
    path = history_file(app_root)
    if not path.exists():
        return []

    entries: list[HistoryEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            data = json.loads(line)
            entries.append(HistoryEntry(**data))
        except (json.JSONDecodeError, TypeError):
            continue
    return entries[-limit:][::-1]


def display_name(entry: HistoryEntry) -> str:
    names = [Path(name).name for name in entry.source_names if name]
    if not names:
        return "Unnamed job"
    if len(names) == 1:
        return names[0]
    return f"{names[0]} and {len(names) - 1} more"
