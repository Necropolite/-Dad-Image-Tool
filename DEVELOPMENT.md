# Development Notes

## Purpose

Dad Image Tool is a Windows desktop utility for normalizing client image batches into JPEG files. The primary interface is a watched folder rather than provider-specific integrations.

## Entry points

- `main.py`: patches the provider-aware collector into the conversion engine and starts the watched-folder application.
- `watcher.py`: watched-folder user interface, stability checks, automatic batch processing, archive movement, and failure routing.
- `app.py`: conversion engine, ZIP extraction, filename handling, image conversion, and legacy manual interface components.
- `providers.py`: optional shared-link handling for major cloud services and generic pages.

## Folder model

At runtime the application uses:

```text
Pictures/Dad Image Tool/
├── Drop Client Pictures Here/
├── Finished/
├── Originals Archive/
└── Needs Attention/
```

Top-level items in the incoming folder are treated as jobs. The watcher checks file sizes on repeated scans so partially downloaded files are not processed prematurely.

After processing:

- A completely successful item moves to `Originals Archive`.
- An item with no converted pictures or reported errors moves to `Needs Attention`.
- JPEG output is written to a dated folder under `Finished`.

## Design boundaries

The processing engine must remain independent of Outlook and individual cloud services. Optional feeders may place files or links into the incoming folder, but the watched folder is the durable interface.

An Outlook add-in may be developed later. It should only collect attachments or links and hand them to the core workflow. It should not duplicate conversion logic.

## Build

`Install.bat` creates a local virtual environment, installs `requirements.txt`, and builds a single-file Windows executable with PyInstaller.

The installer must tolerate:

- Missing Python.
- A stale Windows Python launcher.
- A virtual environment whose base interpreter was removed.
- Reinstallation over an existing app.

## Testing priorities

1. PNG, JPEG, HEIC, WebP, TIFF, and BMP conversion.
2. EXIF rotation.
3. ZIP archives with nested folders.
4. Files still being downloaded into the incoming folder.
5. Duplicate names.
6. Corrupt and password-protected ZIP files.
7. Successful archive movement and failure routing.
8. Startup behavior after reboot.
9. Reinstallation after Python upgrades.
10. Large batches and multiple queued items.

## Safety rules

- Never delete source files during processing.
- Move originals only after processing finishes.
- Route uncertain or failed items to `Needs Attention`.
- Prevent ZIP path traversal.
- Never overwrite an existing output or archived original.
- Use plain-language errors in the user interface and preserve technical details for logs.
