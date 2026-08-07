from __future__ import annotations


def enable_extended_zip_support() -> None:
    """Add Deflate64 support to Python's standard zipfile module when available."""
    try:
        from zipfile64 import patch
    except ImportError:
        return
    patch()
