from __future__ import annotations

import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.parse
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import gdown
import requests
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from tkinter import BOTH, END, LEFT, RIGHT, X, filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

register_heif_opener()

APP_NAME = "Dad Image Tool"
PROTOCOL = "dadimage"
SUPPORTED_IMAGE_SUFFIXES = {
    ".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp"
}


@dataclass
class JobResult:
    converted: int = 0
    skipped: int = 0
    errors: list[str] | None = None
    output_dir: Path | None = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


class DadImageTool(TkinterDnD.Tk):
    def __init__(self, initial_items: list[str] | None = None) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("640x430")
        self.minsize(560, 380)

        default_output = Path.home() / "Pictures" / "Dad Image Tool"
        self.output_root = default_output
        self.pending_items: list[str] = initial_items or []
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.busy = False

        self._build_ui()
        self.after(150, self._drain_events)

        if self.pending_items:
            self.after(300, self.start_processing)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=18)
        outer.pack(fill=BOTH, expand=True)

        ttk.Label(outer, text=APP_NAME, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="Add a link, ZIP folder, picture, or folder. Everything is saved as JPEG.",
            wraplength=590,
        ).pack(anchor="w", pady=(4, 14))

        entry_row = ttk.Frame(outer)
        entry_row.pack(fill=X)
        self.url_entry = ttk.Entry(entry_row)
        self.url_entry.pack(side=LEFT, fill=X, expand=True)
        ttk.Button(entry_row, text="Add Link", command=self.add_link).pack(side=RIGHT, padx=(8, 0))

        button_row = ttk.Frame(outer)
        button_row.pack(fill=X, pady=10)
        ttk.Button(button_row, text="Add Files or ZIP", command=self.add_files).pack(side=LEFT)
        ttk.Button(button_row, text="Add Folder", command=self.add_folder).pack(side=LEFT, padx=(8, 0))
        ttk.Button(button_row, text="Choose Save Folder", command=self.choose_output).pack(side=LEFT, padx=(8, 0))

        self.drop_area = ttk.Label(
            outer,
            text="Drop files, ZIP folders, or folders here",
            anchor="center",
            relief="groove",
            padding=20,
        )
        self.drop_area.pack(fill=X, pady=(2, 10))
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self._on_drop)

        self.status = ttk.Label(outer, text="Ready")
        self.status.pack(anchor="w", pady=(3, 4))

        self.progress = ttk.Progressbar(outer, mode="indeterminate")
        self.progress.pack(fill=X)

        self.log = ttk.Treeview(outer, columns=("item",), show="headings", height=7)
        self.log.heading("item", text="Items waiting")
        self.log.column("item", width=560)
        self.log.pack(fill=BOTH, expand=True, pady=(10, 10))

        footer = ttk.Frame(outer)
        footer.pack(fill=X)
        self.start_button = ttk.Button(footer, text="Start", command=self.start_processing)
        self.start_button.pack(side=RIGHT)
        ttk.Button(footer, text="Open Saved Pictures", command=self.open_output_root).pack(side=RIGHT, padx=(0, 8))

        for item in self.pending_items:
            self._append_to_list(item)

    def add_link(self) -> None:
        value = self.url_entry.get().strip()
        if not value:
            return
        self.pending_items.append(value)
        self._append_to_list(value)
        self.url_entry.delete(0, END)

    def add_files(self) -> None:
        files = filedialog.askopenfilenames(title="Choose pictures or ZIP folders")
        for value in files:
            self.pending_items.append(value)
            self._append_to_list(value)

    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Choose a folder")
        if folder:
            self.pending_items.append(folder)
            self._append_to_list(folder)

    def choose_output(self) -> None:
        folder = filedialog.askdirectory(title="Choose where pictures should be saved")
        if folder:
            self.output_root = Path(folder)
            self.status.config(text=f"Pictures will be saved in: {self.output_root}")

    def _on_drop(self, event: object) -> None:
        data = getattr(event, "data", "")
        for item in self.tk.splitlist(data):
            self.pending_items.append(item)
            self._append_to_list(item)

    def _append_to_list(self, item: str) -> None:
        self.log.insert("", END, values=(item,))

    def start_processing(self) -> None:
        if self.busy:
            return
        self.add_link()
        if not self.pending_items:
            messagebox.showinfo(APP_NAME, "Add a link, ZIP folder, picture, or folder first.")
            return

        items = self.pending_items[:]
        self.pending_items.clear()
        for row in self.log.get_children():
            self.log.delete(row)

        self.busy = True
        self.start_button.config(state="disabled")
        self.progress.start(12)
        self.status.config(text="Working...")
        threading.Thread(target=self._worker, args=(items,), daemon=True).start()

    def _worker(self, items: list[str]) -> None:
        try:
            result = process_items(items, self.output_root, self._send_status)
            self.events.put(("done", result))
        except Exception as exc:  # final safety net for a friendly message
            self.events.put(("fatal", str(exc)))

    def _send_status(self, text: str) -> None:
        self.events.put(("status", text))

    def _drain_events(self) -> None:
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "status":
                    self.status.config(text=str(value))
                elif kind == "done":
                    self._finish(value)
                elif kind == "fatal":
                    self._finish_fatal(str(value))
        except queue.Empty:
            pass
        self.after(150, self._drain_events)

    def _finish(self, result: JobResult) -> None:
        self.busy = False
        self.progress.stop()
        self.start_button.config(state="normal")
        self.status.config(text=f"Done. {result.converted} JPEG picture(s) saved.")

        details = [f"{result.converted} picture(s) saved as JPEG."]
        if result.skipped:
            details.append(f"{result.skipped} unsupported file(s) skipped.")
        if result.errors:
            details.append(f"{len(result.errors)} item(s) could not be processed.")
            details.extend(result.errors[:5])
        messagebox.showinfo(APP_NAME, "\n".join(details))

        if result.output_dir and result.converted:
            open_path(result.output_dir)

    def _finish_fatal(self, text: str) -> None:
        self.busy = False
        self.progress.stop()
        self.start_button.config(state="normal")
        self.status.config(text="Something went wrong.")
        messagebox.showerror(APP_NAME, f"The pictures could not be processed.\n\n{text}")

    def open_output_root(self) -> None:
        self.output_root.mkdir(parents=True, exist_ok=True)
        open_path(self.output_root)


def process_items(items: list[str], output_root: Path, status_cb) -> JobResult:
    output_root.mkdir(parents=True, exist_ok=True)
    batch_name = datetime.now().strftime("%Y-%m-%d %I-%M-%S %p")
    output_dir = unique_path(output_root / batch_name, is_dir=True)
    output_dir.mkdir(parents=True)
    result = JobResult(output_dir=output_dir)

    with tempfile.TemporaryDirectory(prefix="dad-image-tool-") as temp_name:
        temp_dir = Path(temp_name)
        collected: list[Path] = []

        for index, item in enumerate(items, start=1):
            status_cb(f"Collecting item {index} of {len(items)}...")
            try:
                collected.extend(collect_item(item, temp_dir / f"item-{index}"))
            except Exception as exc:
                result.errors.append(f"Could not use one item: {friendly_error(exc)}")

        image_files: list[Path] = []
        for path in collected:
            if path.is_dir():
                image_files.extend(find_images(path))
            elif path.suffix.lower() == ".zip":
                try:
                    extracted = safe_extract_zip(path, temp_dir / f"unzipped-{len(image_files)}")
                    image_files.extend(find_images(extracted))
                except Exception as exc:
                    result.errors.append(f"Could not open ZIP folder: {friendly_error(exc)}")
            elif path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES:
                image_files.append(path)
            else:
                result.skipped += 1

        total = len(image_files)
        for index, image_path in enumerate(image_files, start=1):
            status_cb(f"Converting picture {index} of {total}...")
            try:
                convert_to_jpeg(image_path, output_dir)
                result.converted += 1
            except Exception as exc:
                result.errors.append(f"Could not convert {image_path.name}: {friendly_error(exc)}")

    return result


def collect_item(item: str, destination: Path) -> list[Path]:
    parsed = parse_protocol_url(item)
    if parsed:
        item = parsed

    local = Path(item.strip().strip('"'))
    if local.exists():
        return [local]

    if not item.lower().startswith(("http://", "https://")):
        raise ValueError("This does not appear to be a working link or file.")

    destination.mkdir(parents=True, exist_ok=True)
    host = urllib.parse.urlparse(item).netloc.lower()

    if "drive.google.com" in host:
        return download_google_drive(item, destination)
    if "dropbox.com" in host or "dropboxusercontent.com" in host:
        return [download_dropbox(item, destination)]
    return [download_generic(item, destination)]


def download_google_drive(url: str, destination: Path) -> list[Path]:
    if "/folders/" in url:
        output = destination / "google-drive-folder"
        output.mkdir(parents=True, exist_ok=True)
        files = gdown.download_folder(url=url, output=str(output), quiet=True, use_cookies=False)
        if not files:
            raise ValueError("Google Drive did not provide any downloadable files. The link may require sign-in.")
        return [Path(file) for file in files]

    output = destination / "google-drive-download"
    downloaded = gdown.download(url=url, output=str(output), quiet=True, fuzzy=True)
    if not downloaded:
        raise ValueError("Google Drive did not provide the file. The link may require sign-in.")
    return [Path(downloaded)]


def download_dropbox(url: str, destination: Path) -> Path:
    parts = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qs(parts.query)
    query["dl"] = ["1"]
    direct = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query, doseq=True), parts.fragment))
    return download_generic(direct, destination)


def download_generic(url: str, destination: Path) -> Path:
    with requests.get(url, timeout=60, stream=True, allow_redirects=True) as response:
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
        filename = filename_from_response(response.url, response.headers.get("content-disposition"))
        suffix = Path(filename).suffix
        if not suffix:
            suffix = extension_from_content_type(content_type)
            filename += suffix
        target = unique_path(destination / sanitize_filename(filename))
        with target.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if chunk:
                    file.write(chunk)
        return target


def filename_from_response(url: str, disposition: str | None) -> str:
    if disposition:
        match = re.search(r"filename\*?=(?:UTF-8''|\")?([^\";]+)", disposition, flags=re.IGNORECASE)
        if match:
            return urllib.parse.unquote(match.group(1).strip())
    path_name = Path(urllib.parse.urlparse(url).path).name
    return urllib.parse.unquote(path_name) or "download"


def extension_from_content_type(content_type: str) -> str:
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/heic": ".heic",
        "image/tiff": ".tiff",
        "application/zip": ".zip",
    }.get(content_type, "")


def find_images(folder: Path) -> list[Path]:
    return [path for path in folder.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES]


def safe_extract_zip(archive: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive) as zip_file:
        for member in zip_file.infolist():
            target = (destination / member.filename).resolve()
            if root not in target.parents and target != root:
                raise ValueError("The ZIP folder contains an unsafe file path.")
        zip_file.extractall(destination)
    return destination


def convert_to_jpeg(source: Path, output_dir: Path) -> Path:
    base = sanitize_filename(source.stem) or "picture"
    target = unique_path(output_dir / f"{base}.jpg")
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, "white")
            background.paste(rgba, mask=rgba.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")
        image.save(target, format="JPEG", quality=95, optimize=True)
    return target


def unique_path(path: Path, is_dir: bool = False) -> Path:
    if not path.exists():
        return path
    parent = path.parent
    stem = path.name if is_dir else path.stem
    suffix = "" if is_dir else path.suffix
    counter = 2
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def sanitize_filename(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", value).strip(" .")
    return value[:180] or "file"


def parse_protocol_url(value: str) -> str | None:
    if not value.lower().startswith(f"{PROTOCOL}:"):
        return None
    parsed = urllib.parse.urlparse(value)
    query = urllib.parse.parse_qs(parsed.query)
    return query.get("url", [None])[0]


def friendly_error(exc: Exception) -> str:
    text = str(exc).strip()
    if isinstance(exc, requests.HTTPError):
        code = exc.response.status_code if exc.response is not None else "unknown"
        if code in (401, 403):
            return "the link requires permission or sign-in"
        if code == 404:
            return "the link no longer exists"
    if isinstance(exc, zipfile.BadZipFile):
        return "the ZIP folder is damaged or not a real ZIP file"
    return text or exc.__class__.__name__


def open_path(path: Path) -> None:
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def command_line_items(arguments: Iterable[str]) -> list[str]:
    return [arg for arg in arguments if arg and not arg.startswith("--")]


def main() -> None:
    items = command_line_items(sys.argv[1:])
    app = DadImageTool(items)
    app.mainloop()


if __name__ == "__main__":
    main()
