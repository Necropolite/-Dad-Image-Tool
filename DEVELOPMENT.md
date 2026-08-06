# D.A.D. — Dad Image Tool Development Notes

## Branding contract

- **Brand:** D.A.D.
- **Meaning:** Dad's Automated Dropzone
- **Application name:** Dad Image Tool
- **Tagline:** Drop • Archive • Deliver
- **Setup program:** `DAD-Setup.exe`
- **Executable:** `Dad Image Tool.exe`
- **Update asset:** `Dad-Image-Tool.exe`
- **Shortcuts:** `Dad Image Tool` and `Drop Client Pictures Here`

D.A.D. is a conversion and watched-folder application. It does not download from email or cloud providers. The source item must already exist locally before Dad Image Tool processes it.

Do not rename the repository, executable, shortcuts, installation directory, or data directory without a compelling technical reason. Reuse the constants in `version.py` for visible branding.

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
- `version.py`: version, official identity, repository, and update-asset constants.
- `build_version_info.py`: generates Windows Properties metadata for the packaged executable.
- `build_installer_config.py`: generates Inno Setup branding and version constants.
- `installer/DAD.iss`: builds the per-user Windows setup program.
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

## End-user installation

The supported end-user path is `DAD-Setup.exe`.

The setup program:

- installs the prebuilt executable under `%LocalAppData%\Dad Image Tool`.
- creates the application and drop-folder desktop shortcuts.
- creates the startup shortcut.
- registers a normal Windows uninstaller.
- creates the four data folders using the user's configured Pictures location.
- launches the application after setup.
- leaves all Pictures data untouched during repair installation and uninstall.

It runs as a per-user install and should not require an administrator password.

`Install.bat`, `Run-Tests.bat`, and `Uninstall.bat` remain maintainer or compatibility tools. They are not part of Dad's workflow.

## Build workflows

`.github/workflows/build-test-installer.yml` runs for pushes to `main`. It compiles and tests the code, builds the executable, compiles `DAD-Setup.exe`, and uploads a temporary test artifact.

`.github/workflows/release.yml` runs for version tags. It publishes the setup program, setup checksum, raw update executable, and update checksum.

## Updates

A valid newer GitHub Release must contain `Dad-Image-Tool.exe` and `Dad-Image-Tool.exe.sha256`. The updater verifies SHA-256, keeps the prior executable as a temporary backup, starts the new version, and restores the backup if replacement or startup fails.

The repository is public, so anonymous release checks can work. Never embed a GitHub token in the application.

## Testing

Automated tests do not prove the setup wizard, startup shortcut, packaged HEIC support, SmartScreen behavior, Windows Properties metadata, repair installation, uninstall safety, or self-update behavior on a real Windows computer.

Complete `TESTING.md` beginning with `DAD-Setup.exe` and without using developer tools.

## Safety rules

- Never delete source items during processing.
- Never overwrite finished or archived files.
- Never let one source failure affect another source.
- Never process changing or partial downloads.
- Never trust ZIP member paths.
- Never update or uninstall user-data folders.
- Keep the interface small and plain.
- Do not restore browser or direct-link behavior without an explicit design decision.
