from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import app
import history
from watcher_support import (
    APP_ROOT,
    ARCHIVE,
    FINISHED,
    NEEDS_ATTENTION,
    ItemFingerprint,
    item_fingerprint,
    move_target,
)


class Worker(Protocol):
    blocked_items: dict[Path, ItemFingerprint]

    def _send_status(self, text: str) -> None: ...


@dataclass
class ProcessingSummary:
    converted: int = 0
    attention_items: int = 0
    outputs: list[Path] = field(default_factory=list)


def process_sources(worker: Worker, items: list[Path]) -> ProcessingSummary:
    summary = ProcessingSummary()
    if not items:
        return summary

    batch_output_dir = app.create_output_dir(FINISHED)

    for index, source in enumerate(items, start=1):
        worker._send_status(f"Processing item {index} of {len(items)}: {source.name}")
        try:
            result = app.process_items(
                [str(source)],
                FINISHED,
                worker._send_status,
                output_dir=batch_output_dir,
            )
        except Exception as exc:
            result = app.JobResult(errors=[f"Unexpected processing error: {app.friendly_error(exc)}"])

        destination = ARCHIVE if result.converted > 0 and not result.errors else NEEDS_ATTENTION
        try:
            move_target(source, destination)
        except Exception as exc:
            result.errors.append(f"Could not move the original file: {app.friendly_error(exc)}")
            if source.exists() and destination != NEEDS_ATTENTION:
                try:
                    move_target(source, NEEDS_ATTENTION)
                except Exception:
                    _block_source(worker, source)
            elif source.exists():
                _block_source(worker, source)

        try:
            history.record_job(
                APP_ROOT,
                source_names=[source.name],
                converted=result.converted,
                errors=result.errors,
                output_folder=result.output_dir,
            )
        except Exception:
            worker._send_status("The job finished, but its history could not be saved.")

        summary.converted += result.converted
        if result.errors or result.converted == 0:
            summary.attention_items += 1

    if summary.converted > 0:
        summary.outputs.append(batch_output_dir)
    else:
        shutil.rmtree(batch_output_dir, ignore_errors=True)

    return summary


def _block_source(worker: Worker, source: Path) -> None:
    try:
        worker.blocked_items[source] = item_fingerprint(source) or ItemFingerprint(0, 0, 0)
    except OSError:
        pass
