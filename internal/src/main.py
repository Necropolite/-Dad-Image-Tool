from __future__ import annotations

import sys

from ui_assets import set_windows_app_identity
from zip_support import enable_extended_zip_support


def run_self_test() -> None:
    """Import the approved runtime surface and verify bundled local assets without network access."""
    import app  # noqa: F401
    import assistant_launcher
    import history_window  # noqa: F401
    import learning_lab_launcher
    import ui_layout  # noqa: F401
    import update_ui  # noqa: F401
    import updater  # noqa: F401
    import watcher  # noqa: F401
    import watcher_processing  # noqa: F401
    import watcher_support  # noqa: F401

    lab_page = learning_lab_launcher.learning_lab_path()
    if not lab_page.is_file():
        raise RuntimeError(f"Learning Lab bundle is missing: {lab_page}")

    assistant = assistant_launcher.assistant_url()
    if not assistant.startswith(("https://", "http://127.0.0.1", "http://localhost", "http://[::1]")):
        raise RuntimeError("Ask Pete resolved to an unsafe assistant URL.")


def main() -> None:
    set_windows_app_identity()
    enable_extended_zip_support()

    if "--self-test" in sys.argv:
        run_self_test()
        return

    from watcher import main as watcher_main

    watcher_main()


if __name__ == "__main__":
    main()
