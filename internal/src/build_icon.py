from __future__ import annotations

import sys
from pathlib import Path

from ui_assets import write_windows_icon


def main() -> None:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Dad-Image-Tool.ico")
    write_windows_icon(destination)


if __name__ == "__main__":
    main()
