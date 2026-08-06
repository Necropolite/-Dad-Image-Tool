from __future__ import annotations

from pathlib import Path

from version import APP_NAME, APP_VERSION, PRODUCT_DESCRIPTION

OUTPUT_PATH = Path("installer/generated.iss")


def render_installer_config() -> str:
    return (
        f'#define MyAppVersion "{APP_VERSION}"\n'
        f'#define MyAppName "{APP_NAME}"\n'
        f'#define MyProductDescription "{PRODUCT_DESCRIPTION}"\n'
    )


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render_installer_config(), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
