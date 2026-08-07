from __future__ import annotations

import sys

from ui_assets import set_windows_app_identity
from zip_support import enable_extended_zip_support


def main() -> None:
    set_windows_app_identity()
    enable_extended_zip_support()

    if "--self-test" in sys.argv:
        import app  # noqa: F401
        import updater  # noqa: F401
        import watcher_support  # noqa: F401
        return

    from watcher import main as watcher_main

    watcher_main()


if __name__ == "__main__":
    main()
