from __future__ import annotations

import sys


def main() -> None:
    if "--self-test" in sys.argv:
        import app  # noqa: F401
        import updater  # noqa: F401
        import watcher_support  # noqa: F401
        return

    from watcher import main as watcher_main

    watcher_main()


if __name__ == "__main__":
    main()
