# D.A.D. — Dad Image Tool Development Notes

## Branding contract

- **Brand:** D.A.D.
- **Meaning:** Dad's Automated Downloader
- **Application name:** Dad Image Tool
- **Tagline:** Download • Archive • Deliver
- **Executable:** `Dad Image Tool.exe`
- **Release asset:** `Dad-Image-Tool.exe`
- **Shortcuts:** `Dad Image Tool` and `Drop Client Pictures Here`

Do not rename the repository, executable, shortcuts, installation directory, or data directory without a compelling technical reason. Reuse the constants in `version.py` for visible branding. `build_version_info.py` generates the Windows executable metadata from the same constants and application version.

## Architecture

Dad Image Tool is a Windows watched-folder application for a nontechnical user. The watched folder is the only input interface. Browser extensions, custom URL protocols, direct cloud downloads, and provider-specific integrations are outside the design.

Main modules:

- `main.py`: packaged entry point.
- `watcher.py`: window, scan loop, queue, and orchestration.
- `watcher_support.py`: Windows folders, stability checks, safe moves, partial-download detection, and single-instance protection.
- `watcher_processing.py`: independent source processing and routing.
- `ui_layout.py`, `history_window.py`, `update_ui.py`: user interface.
- `app.py`: discovery, nested ZIP handling, conversion, and safe filenames.
- `history.py`: backward-compatible JSON Lines history.
- `updater.py`: release lookup, checksum verification, replacement, restart, and rollback.
- `version.py`: version, official identity, repository, and release asset constants.
- `build_version_info.py`: generated Windows Properties metadata for the packaged executable.
- `tests/`: processing, history, archive, stability, routing, updater, and branding tests.

## Runtime folders

```text
Pictures/Dad Image Tool/
├── Drop Client Pictures Here/
├── Finished/
├── Originals Archive/
├── Needs Attention/
└── job-history.jsonl
```

Each top-level incoming item is one job. Jobs run sequentially. New items wait for the next scan.

## Processing rules

1. Ignore known partial-download suffixes.
2. Require three unchanged scans.
3. Process top-level sources independently.
4. Recursively inspect folders and ZIP files.
5. Convert supported images into a unique dated output folder.
6. Move a fully successful source to `Originals Archive`.
7. Move a failed or partly failed source to `Needs Attention`.
8. Record history after routing.
9. Open successful output automatically.

Supported images are JPG, JPEG, PNG, HEIC, HEIF, TIFF, BMP, and WebP. Conversion applies EXIF orientation, preserves available EXIF, ICC, and DPI metadata, flattens transparency onto white, and writes JPEG at quality 95. Output is first written to a temporary file and renamed only after a successful save. Existing files are never overwritten.

## ZIP safety

ZIP extraction rejects absolute paths, parent traversal, encrypted entries, and symbolic links. It limits nesting depth, file count, and declared uncompressed size. Members are extracted individually instead of with `extractall`.

## History

History is append-only JSON Lines. New entries include plain-English errors. Older entries containing only an error count remain readable. Never store client image contents in history.

## Installation and updates

`Install.bat` finds Python or attempts to install Python 3.12, repairs stale `.venv` folders, installs dependencies, compiles source, runs tests, generates Windows version metadata, builds the executable, stages replacement, repairs shortcuts, and starts the app. User data under Pictures is never replaced or deleted.

A valid newer GitHub Release must contain `Dad-Image-Tool.exe` and `Dad-Image-Tool.exe.sha256`. The updater verifies SHA-256, keeps the prior executable as a temporary backup, starts the new version, and restores the backup if replacement or startup fails.

Anonymous updates cannot work while the release repository is private. Never embed a GitHub token in the application.

## Testing

Run `Run-Tests.bat`. GitHub Actions compiles and runs the suite on Windows for pushes to `main` and pull requests. The release workflow repeats the checks before building.

Automated tests do not prove the installer, startup shortcut, packaged HEIC support, SmartScreen behavior, Windows Properties metadata, or self-update works on a real Windows computer. Complete `TESTING.md` before release.

## Safety rules

- Never delete source items during processing.
- Never overwrite finished or archived files.
- Never let one source failure affect another source.
- Never process changing or partial downloads.
- Never trust ZIP member paths.
- Never update user-data folders.
- Keep the interface small and plain.
- Do not restore browser or direct-link behavior without an explicit design decision.
