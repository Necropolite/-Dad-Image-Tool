from __future__ import annotations

import sys

from ui_assets import set_windows_app_identity
from zip_support import enable_extended_zip_support


def main() -> None:
    set_windows_app_identity()
    enable_extended_zip_support()

    if "--self-test" in sys.argv:
        import app  # noqa: F401
        import drag_drop
        import updater  # noqa: F401
        import watcher_support  # noqa: F401

        drag_drop.verify_runtime()
        return

    file_args = [argument for argument in sys.argv[1:] if argument and not argument.startswith("--")]
    if file_args:
        import drop_intake

        drop_intake.queue_paths(file_args)

    from watcher import main as watcher_main

    # Dropping a file onto an application shortcut can launch a helper instance.
    # The helper has already queued the paths above, so it should exit quietly if
    # the normal watcher instance is already running.
    watcher_main(quiet_if_running=bool(file_args))


if __name__ == "__main__":
    main()
