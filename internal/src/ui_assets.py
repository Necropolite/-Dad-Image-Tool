from __future__ import annotations

import base64
import ctypes
import io
import sys
import zlib
from pathlib import Path
from tkinter import PhotoImage

from PIL import Image

# Stable Windows application identity so the running taskbar button groups under
# Dad Image Tool instead of Tk/Python's generic process identity.
WINDOWS_APP_USER_MODEL_ID = "Necropolite.DadImageTool"

# Compact grayscale mask derived from the horse image supplied for Dad Image Tool.
# The olive background is sampled from the same source image. Keeping the asset as
# compressed data makes it available to both Tk and the Windows packaging build
# without adding a loose runtime image file.
ICON_SOURCE_SIZE = 128
ICON_BACKGROUND = (104, 104, 45, 255)
HORSE_MASK_ZLIB_BASE64 = """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"""


def set_windows_app_identity() -> None:
    """Give the process a stable Windows taskbar identity before Tk creates a window."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WINDOWS_APP_USER_MODEL_ID)
    except Exception:
        # Windows identity is cosmetic; failure must never prevent conversion.
        pass


def _horse_image(size: int) -> Image.Image:
    raw = zlib.decompress(base64.b64decode(HORSE_MASK_ZLIB_BASE64))
    mask = Image.frombytes("L", (ICON_SOURCE_SIZE, ICON_SOURCE_SIZE), raw)
    if size != ICON_SOURCE_SIZE:
        mask = mask.resize((size, size), Image.Resampling.LANCZOS)

    image = Image.new("RGBA", (size, size), ICON_BACKGROUND)
    image.paste((255, 255, 255, 255), (0, 0, size, size), mask)
    return image


def apply_window_icon(window) -> None:
    """Use the horse mark for the title bar and taskbar without affecting startup."""
    try:
        buffer = io.BytesIO()
        _horse_image(128).save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        icon = PhotoImage(data=encoded)
        window.iconphoto(True, icon)
        window._dad_image_tool_icon = icon
    except Exception:
        # Icon rendering is cosmetic and should never prevent the converter from opening.
        pass


def write_windows_icon(destination: str | Path) -> Path:
    """Generate the multi-size .ico used by PyInstaller and Inno Setup."""
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    _horse_image(256).save(
        target,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    return target
