from __future__ import annotations

import sys

from ui_assets import set_windows_app_identity
from zip_support import enable_extended_zip_support


def run_self_test() -> None:
    """Import the approved converter runtime surface without network access."""
    import app  # noqa: F401
    import history_window  # noqa: F401
    import ui_layout  # noqa: F401
    import update_ui  # noqa: F401
    import updater  # noqa: F401
    import watcher  # noqa: F401
    import watcher_processing  # noqa: F401
    import watcher_support  # noqa: F401


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
