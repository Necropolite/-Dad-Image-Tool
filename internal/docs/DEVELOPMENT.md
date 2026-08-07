# Dad Image Tool Development Notes

## Product boundary

Dad Image Tool is a Windows watched-folder image converter. The user saves source material locally and places it in **Drop Client Pictures Here**. Email retrieval, cloud-provider integrations, horse/case management, and automatic filing of the finished JPEGs are outside the product scope.

User-facing identity rules live in [BRANDING.md](BRANDING.md). Release procedure lives in [RELEASING.md](RELEASING.md). End-user acceptance checks live in [TESTING.md](TESTING.md).

## Repository layout

- `README.md`: concise user-facing landing page.
- `USER_GUIDE.md`: installation, daily use, updates, and troubleshooting.
- `internal/src/`: application and build Python source.
- `internal/scripts/`: maintainer convenience scripts.
- `internal/docs/`: maintainer documentation.
- `internal/requirements.txt`: build/runtime Python dependencies used for packaging.
- `tests/`: automated tests.
- `installer/`: Inno Setup source.
- `.github/workflows/`: automated testing, installer builds, and releases.

## Runtime data

User data is stored separately from the installed application:

```text
Pictures\Dad Image Tool\
├── Drop Client Pictures Here\
├── Finished\
├── Originals Archive\
├── Needs Attention\
└── job-history.jsonl
```

The application itself is installed under `%LocalAppData%\Dad Image Tool`.

This separation is intentional: repair installs, upgrades, and uninstall must never delete the Pictures data tree.

## Processing model

The watcher waits for incoming items to remain unchanged across repeated scans before processing them. Known partial-download suffixes are ignored.

Items that become ready together share one dated Finished batch, while each top-level source is still routed independently:

1. discover supported pictures within the source;
2. extract supported containers as needed;
3. convert discovered pictures to JPEG;
4. preserve source/container structure in the batch where practical;
5. archive the original source only when that source completes without errors;
6. otherwise move the original source to `Needs Attention`;
7. record the result in history;
8. open the successful Finished batch.

Existing Finished or archive files are never overwritten.

### Supported images

JPG, JPEG, PNG, HEIC, HEIF, WebP, TIFF, and BMP.

Conversion applies EXIF orientation, preserves available EXIF/ICC/DPI metadata, flattens transparency onto white, and writes JPEG at quality 95. Output is written through a temporary file before the final rename.

### Containers

Folders are inspected recursively.

ZIP files may contain folders, additional ZIPs, DOCX files, PDFs, and supported images. Standard ZIP compression and Deflate64 are supported. ZIP nesting depth, extracted file count, and declared uncompressed size are bounded.

DOCX files are photo containers. `document_support.py` follows document image relationships so embedded pictures are extracted in document order when possible.

PDF files are photo containers. Embedded raster pictures are extracted directly when possible rather than rendering whole pages. Password-protected or unreadable documents fail safely.

## Safety rules

- Never delete a source as part of processing.
- Never overwrite Finished or archived files.
- Never let one top-level source failure invalidate unrelated sources in the same batch.
- Never process files that are still changing.
- Reject unsafe ZIP paths, encrypted ZIP members, and symbolic links.
- Bound container extraction by nesting depth, file count, and total extracted size.
- Keep failed or unsupported originals in `Needs Attention`.
- Never store client image contents in job history.
- Never remove user data during install, upgrade, repair, or uninstall.

## Main modules

- `main.py`: packaged entry point and CI self-test entry point.
- `watcher.py`: UI lifecycle, scan loop, queue, and orchestration.
- `watcher_support.py`: runtime paths, stability checks, safe moves, partial-download detection, and single-instance protection.
- `watcher_processing.py`: batch creation, per-source processing, routing, and history recording.
- `app.py`: recursive discovery, ZIP handling, image conversion, output structure, and safe filenames.
- `document_support.py`: DOCX and PDF image extraction.
- `zip_support.py`: extended ZIP/Deflate64 support.
- `history.py` and `history_window.py`: JSON Lines history and history UI.
- `ui_layout.py` and `update_ui.py`: main UI and update prompts.
- `updater.py`: GitHub release lookup, setup/checksum download, verification, and installer launch.
- `version.py`: application version and product/repository constants.
- `build_version_info.py`: Windows executable metadata generation.
- `build_installer_config.py`: Inno Setup version/branding generation.
- `installer/DAD.iss`: per-user Windows installer.

## Packaging and updates

PyInstaller builds Dad Image Tool in **onedir** mode. Inno Setup installs the complete runtime folder while presenting a normal single application shortcut to the user. Onedir packaging avoids the temporary `_MEI...` extraction path used by PyInstaller onefile builds.

The in-app updater does not replace `Dad Image Tool.exe` directly. It downloads the released `Dad-Image-Tool-Setup.exe` plus its SHA-256 checksum, verifies the installer, closes the application, and runs setup silently.

Before copying the replacement runtime, setup removes only known obsolete application-runtime paths such as the previous executable, `_internal`, and legacy updater backup files. User data lives outside the install directory and is not part of that cleanup.

CI smoke-tests both the packaged executable and an installed copy. The installer workflow also performs an upgrade-cleanup/data-preservation test before publishing the root setup executable.
