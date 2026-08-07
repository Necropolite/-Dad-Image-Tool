from __future__ import annotations


def enable_extended_zip_support() -> None:
    """Add Deflate64 support to Python's standard zipfile module when available."""
    try:
        # Importing this compatibility module patches Python's standard zipfile
        # module as a documented side effect.
        import zipfile64.zipfile  # noqa: F401
    except ImportError:
        return
