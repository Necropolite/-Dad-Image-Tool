from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

UPDATE_TEMP_PREFIX = "dad-image-tool-update-"


def cleanup_update_temp_dirs() -> None:
    """Remove updater scratch directories left behind before installer handoff."""
    temp_root = Path(tempfile.gettempdir())
    try:
        candidates = list(temp_root.glob(f"{UPDATE_TEMP_PREFIX}*"))
    except OSError:
        return

    for candidate in candidates:
        try:
            if candidate.is_dir() and not candidate.is_symlink():
                shutil.rmtree(candidate)
        except OSError:
            # Temp cleanup must never prevent Dad Image Tool from starting or
            # reporting the original update error.
            pass
