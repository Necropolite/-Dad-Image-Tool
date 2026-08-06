from __future__ import annotations

import sys
from pathlib import Path

from version import APP_NAME, APP_VERSION, BRAND_FULL_NAME, BRAND_NAME, TAGLINE


def _version_tuple(version: str) -> tuple[int, int, int, int]:
    parts = version.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError("APP_VERSION must contain exactly three numeric parts")
    return int(parts[0]), int(parts[1]), int(parts[2]), 0


def render_version_info() -> str:
    file_version = _version_tuple(APP_VERSION)
    return f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={file_version},
    prodvers={file_version},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', '{BRAND_NAME}'),
          StringStruct('FileDescription', '{BRAND_NAME} — {BRAND_FULL_NAME}'),
          StringStruct('FileVersion', '{APP_VERSION}'),
          StringStruct('InternalName', '{APP_NAME}'),
          StringStruct('OriginalFilename', '{APP_NAME}.exe'),
          StringStruct('ProductName', '{APP_NAME}'),
          StringStruct('ProductVersion', '{APP_VERSION}'),
          StringStruct('Comments', '{TAGLINE}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def main() -> None:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "version_info.txt")
    output.write_text(render_version_info(), encoding="utf-8")


if __name__ == "__main__":
    main()
