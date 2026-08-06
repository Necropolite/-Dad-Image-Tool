# Development Notes

## Architecture

Dad Image Tool is a Windows watched-folder application for a nontechnical user. The watched folder is the only input interface. Browser extensions, custom URL protocols, direct cloud downloads, and provider-specific integrations are outside the design.

The dependency flow is intentionally one-directional:

```text
main.py
└── watcher.py
    ├── ui_layout.py
    ├── history_window.py
    ├── update_ui.py ── updater.py
    └── watcher_processing.py
        ├── app.py
        ├── history.py
        └── watcher_support.py ── app.py
```

There are no application-module import cycles.

### Module responsibilities

- `main.py`: packaged entry point only.
- `watcher.py`: window lifecycle, scan scheduling, event queue, and orchestration.
- `watcher_support.py`: Windows known folders, stability fingerprints, safe moves, partial-download detection, and single-instance protection.
- `watcher_processing.py`: processes top-level sources independently, routes originals, records history, and summarizes results.
- `ui_layout.py`: constructs the small main window and returns its widgets explicitly.
- `history_window.py`: displays job history and opens completed output folders.
- `update_ui.py`: update prompts and background update coordination.
- `app.py`: local file discovery, nested ZIP handling, image conversion, metadata handling, and safe filenames. It has no UI or network dependency.
- `history.py`: backward-compatible JSON Lines history.
- `updater.py`: the only application module that uses the network. It handles release lookup, checksum verification, replacement, startup confirmation, and rollback.
- `tests/`: processing, ZIP safety, routing, lifecycle, history, stability, UI helpers, installer-facing startup behavior, and updater tests.

### Boundaries

- Tkinter calls stay on the main thread.
- Worker threads report through `FolderWatcher.events`.
- Image processing does not know about UI widgets or GitHub.
- Routing originals is centralized in `watcher_processing.py`.
- Runtime paths and file-move helpers are centralized in `watcher_support.py`.
- The updater never touches the user-data folders.
- New cloud-provider code must not be added to the processing engine.

## Runtime folders

```text
Pictures/Dad Image Tool/
├── Drop Client Pictures Here/
├── Finished/
├── Originals Archive/
├── Needs Attention/
└── job-history.jsonl
```

Each top-level incoming item is one job. Jobs run sequentially. New items remain queued in the watched folder.

## Lifecycle and concurrency

The watcher takes three unchanged fingerprints and requires the newest file to be at least ten seconds old before processing. Known partial-download suffixes block the whole top-level item. Symbolic links and Windows junctions are not followed.

The window cannot close in the middle of a job. A close request is remembered, the current job finishes safely, and the window then closes without opening new folders or dialogs. Update installation is also blocked while processing is active.

Runtime folders are recreated if they are removed while the app is running. An unexpected orchestration failure leaves originals in the drop folder and blocks unchanged items from entering a rapid retry loop.

## Processing rules

1. Process top-level sources independently.
2. Recursively inspect ordinary folders and ZIP files.
3. Convert supported images into a unique dated output folder.
4. Move a fully successful source to `Originals Archive`.
5. Move a failed or partly failed source to `Needs Attention`.
6. Record history after routing.
7. Open successful output automatically unless the app is closing.

Supported images are JPG, JPEG, PNG, HEIC, HEIF, TIFF, BMP, and WebP. Conversion applies EXIF orientation, preserves available EXIF, ICC, and DPI metadata, flattens transparency onto white, and writes JPEG at quality 95. Output is first written to a temporary file and renamed only after a successful save. Existing output and archived files are never overwritten.

Pillow decompression-bomb warnings are treated as failures with a plain-language message instead of allowing an unusually large image to consume unbounded memory.

## ZIP safety

ZIP extraction rejects:

- Absolute paths and parent traversal.
- Password-protected entries.
- Symbolic links.
- Windows-invalid and reserved filenames.
- Case-insensitive duplicate paths.
- File and directory path conflicts.
- Excessive nesting, file counts, or declared uncompressed size.

Members are validated before extraction, extracted individually, and created with exclusive file creation rather than `extractall`.

## History

History is append-only JSON Lines. New entries include plain-English errors. Older entries containing only an error count remain readable. Client image contents are never stored in history.

## Installation and updates

`Install.bat` accepts supported Python 3.12 or 3.13 installations or attempts to install Python 3.12. It repairs stale `.venv` folders, installs dependencies, compiles source, runs tests, builds the executable, asks a running app to finish safely, stages replacement, repairs shortcuts, verifies that the new executable initializes, and restores the previous executable if installation fails.

A valid newer GitHub Release must contain `Dad-Image-Tool.exe` and `Dad-Image-Tool.exe.sha256`. The updater verifies SHA-256, keeps the prior executable as a temporary backup, starts the new version with a one-time startup marker, waits for initialization, and restores the backup if startup is not confirmed.

Anonymous updates cannot work while the release repository is private. Never embed a GitHub token in the application.

## Testing and review tooling

Run `Run-Tests.bat`. It installs `requirements-dev.txt`, compiles the source, runs Ruff, executes the automated suite under Coverage.py, and enforces the core-module coverage floor configured in `pyproject.toml`.

The coverage floor applies to conversion, history, updater, routing, and filesystem-support logic. Tkinter layout modules are intentionally excluded from the numeric floor because their meaningful behavior is validated through focused tests and manual Windows acceptance checks.

GitHub Actions repeats the checks on Windows, builds the PyInstaller executable, records the exact resolved dependencies, generates non-client review fixtures, and uploads the evidence as a workflow artifact. The release workflow repeats lint, coverage, and tests before building release assets.

Use `python tools/generate_review_fixtures.py review-fixtures` to create repeatable success and failure inputs without using client images. See `REVIEW_GUIDE.md` for the architecture, threat model, safety invariants, and requested third-party review focus.

Automated tests do not prove the desktop shortcuts, startup entry, packaged HEIC support, SmartScreen behavior, or self-update path works on a real Windows computer. Complete `TESTING.md` before release.

Dependencies are bounded by major version. Each Windows workflow records the exact resolved dependency set as an artifact, but a release should not be called reproducible until that snapshot has been retained and validated.

## Safety rules

- Never delete source items during processing.
- Never overwrite finished or archived files.
- Never let one source failure affect another source.
- Never process changing, too-new, or partial downloads.
- Never follow shortcuts, symbolic links, or linked folders.
- Never trust ZIP member paths.
- Never stop an active job for installation or uninstallation.
- Never update user-data folders.
- Keep the interface small and plain.
- Do not restore browser or direct-link behavior without an explicit design decision.
