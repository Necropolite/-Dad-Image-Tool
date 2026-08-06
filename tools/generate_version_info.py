from __future__ import annotations

import argparse
from pathlib import Path

from version import APP_BRAND_TITLE, APP_NAME, APP_VERSION, BRAND_ACRONYM, BRAND_EXPANSION, BRAND_TAGLINE


def _version_tuple() -> tuple[int, int, int, int]:
    parts = tuple(int(part) for part in APP_VERSION.split("."))
    if len(parts) != 3:
        raise ValueError("APP_VERSION must contain three numeric parts.")
    return (*parts, 0)


def render_version_info() -> str:
    version = _version_tuple()
    product_name = f"{BRAND_ACRONYM} — {BRAND_EXPANSION}"
    strings = (
        ("CompanyName", BRAND_ACRONYM),
        ("FileDescription", APP_BRAND_TITLE),
        ("FileVersion", APP_VERSION),
        ("InternalName", APP_NAME),
        ("OriginalFilename", f"{APP_NAME}.exe"),
        ("ProductName", product_name),
        ("ProductVersion", APP_VERSION),
        ("Comments", BRAND_TAGLINE),
    )
    string_rows = ",\n".join(
        f"          StringStruct({key!r}, {value!r})" for key, value in strings
    )
    return f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version!r},
    prodvers={version!r},
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
{string_rows}
        ]
      )
    ]),
    VarFileInfo([
      VarStruct('Translation', [1033, 1200])
    ])
  ]
)
"""


def write_version_info(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_version_info(), encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Windows version metadata for Dad Image Tool.")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    write_version_info(args.destination)


if __name__ == "__main__":
    main()
