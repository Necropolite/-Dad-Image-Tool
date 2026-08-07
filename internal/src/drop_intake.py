from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import app
from watcher_support import IGNORED_SUFFIXES, INCOMING, move_target


@dataclass
class IntakeResult:
    queued: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def queue_paths(paths: Iterable[str | Path]) -> IntakeResult:
    """Move local files/folders into the watched drop folder safely."""
    result = IntakeResult()
    INCOMING.mkdir(parents=True, exist_ok=True)
    incoming_root = INCOMING.resolve()

    for raw_path in paths:
        source = Path(str(raw_path).strip().strip('"'))
        if not str(source):
            continue

        try:
            if not source.exists():
                result.errors.append(f"Could not find {source.name or 'one dropped item'}.")
                continue

            resolved = source.resolve()
            if resolved == incoming_root or incoming_root in resolved.parents:
                result.queued.append(source)
                continue

            if source.is_file() and source.suffix.lower() in IGNORED_SUFFIXES:
                result.errors.append(f"{source.name} is still downloading. Wait for it to finish and try again.")
                continue

            result.queued.append(move_target(source, INCOMING))
        except Exception as exc:
            result.errors.append(f"Could not add {source.name or 'one dropped item'}: {app.friendly_error(exc)}")

    return result
