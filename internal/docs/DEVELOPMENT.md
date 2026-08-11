# Dad Image Tool Development Notes

## Product boundary

Dad Image Tool is a Windows watched-folder image converter. The user saves source material locally and places it in **Drop Client Pictures Here**. Email retrieval, cloud-provider integrations, horse/case management, and automatic filing of the finished JPEGs are outside the product scope. Saved `.eml` and Outlook `.msg` files are supported as local photo containers; the application does not connect to an email account.

Experimental teaching tools are deliberately isolated from the converter. They must not receive client images or become dependencies of the watched-folder processing path.

User-facing identity rules live in [BRANDING.md](BRANDING.md). Release procedure lives in [RELEASING.md](RELEASING.md). End-user acceptance checks live in [TESTING.md](TESTING.md).

## Repository layout

- `README.md`: concise user-facing landing page.
- `USER_GUIDE.md`: installation, daily use, updates, and troubleshooting.
- `internal/src/`: application and build Python source.
- `internal/learning_lab/`: bundled snapshot of the experimental Pete Ramey Learning Lab browser interface.
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

ZIP files may contain folders, additional ZIPs, DOCX files, PDFs, EML files, MSG files, and supported images. Standard ZIP compression and Deflate64 are supported. ZIP nesting depth, extracted file count, and declared uncompressed size are bounded.

DOCX files are photo containers. `document_support.py` follows document image relationships so embedded pictures are extracted in document order when possible.

PDF files are photo containers. Embedded raster pictures are extracted directly when possible rather than rendering whole pages. Password-protected or unreadable documents fail safely.

EML files are email photo containers. `email_support.py` uses Python's standard MIME parser, walks message parts in order, and extracts supported `image/*` parts whether they are marked `inline` or `attachment`.

MSG files are Outlook email photo containers. `msg_support.py` uses `extract-msg` to read attachment byte streams without automating Outlook. Supported image attachments are accepted whether they are normal attachments or inline/hidden body images.

No email credentials or network access are involved in EML/MSG extraction.

## UI contract

The main window is deliberately plain. It presents the application name, short description, drop-folder path, current status, progress indicator, and only the controls needed for normal use plus explicitly labeled experiments:

- Open Drop Folder
- Open Finished Pictures
- View History
- Check for Updates
- Ask Pete (Experimental)
- Learning Lab (Experimental)

There is no About button or decorative logo inside the window.

### Ask Pete

`assistant_launcher.py` opens the hosted private browser assistant using Python's standard `webbrowser` integration. The default endpoint is `https://pete-ramey-assistant-api.cramey254.workers.dev/`; `DAD_ASSISTANT_URL` may provide an alternate private HTTPS address. Remote HTTP endpoints are rejected. Credentials, conversations, citations, and client images never pass through Dad Image Tool.

### Learning Lab

`learning_lab_launcher.py` opens `internal/learning_lab/index.html` during source development and the PyInstaller-bundled `learning_lab/index.html` in packaged builds. It uses a `file://` browser URI and requires no local Python server, command prompt, or additional install.

The authoritative Learning Lab project is `Necropolite/Pete-Ramey-Learning-Lab`. The files under `internal/learning_lab/` are a release snapshot so Pete receives the same prototype through Dad Image Tool's normal updater. When the Learning Lab changes, intentionally sync the approved `index.html`, `app.js`, and `styles.css` before the next Dad Image Tool release.

The browser interface talks directly to the separately operated private Knowledge Core Worker over HTTPS. Dad Image Tool itself never receives the Learning Lab bearer token, questions, answers, citations, or client images. The Lite interface is restricted by product policy to public HoofRehab teaching material and must not silently gain book/private content.

The supplied horse artwork is represented as a compact embedded grayscale mask in `ui_assets.py`. At runtime it supplies the Tk window/taskbar icon. During Windows packaging, `build_icon.py` generates `Dad-Image-Tool.ico`, which is used by both PyInstaller and Inno Setup.

## Safety rules

- Never delete a source as part of processing.
- Never overwrite Finished or archived files.
- Never let one top-level source failure invalidate unrelated sources in the same batch.
- Never process files that are still changing.
- Reject unsafe ZIP paths, encrypted ZIP members, and symbolic links.
- Bound container extraction by nesting depth, file count, and total extracted size.
- Sanitize filenames recovered from document and email containers before writing them to temporary storage.
- Keep failed or unsupported originals in `Needs Attention`.
- Never store client image contents in job history.
- Never remove user data during install, upgrade, repair, or uninstall.
- Never route client pictures, conversion history, or watched-folder data through Ask Pete or Learning Lab.

## Main modules

- `main.py`: packaged entry point and CI self-test entry point.
- `watcher.py`: UI lifecycle, scan loop, queue, and orchestration.
- `watcher_support.py`: runtime paths, stability checks, safe moves, partial-download detection, and single-instance protection.
- `watcher_processing.py`: batch creation, per-source processing, routing, and history recording.
- `app.py`: recursive discovery, container routing, ZIP handling, image conversion, output structure, and safe filenames.
- `document_support.py`: DOCX and PDF image extraction.
- `email_support.py`: EML MIME image extraction.
- `msg_support.py`: Outlook MSG image extraction.
- `zip_support.py`: extended ZIP/Deflate64 support.
- `history.py` and `history_window.py`: JSON Lines history and history UI.
- `ui_layout.py` and `update_ui.py`: main UI and update prompts.
- `assistant_launcher.py`: opens the hosted private Ask Pete browser app.
- `learning_lab_launcher.py`: opens the bundled experimental Learning Lab browser app.
- `ui_assets.py`: embedded horse icon asset and runtime/icon generation helpers.
- `updater.py`: primary GitHub API release lookup, fallback release-manifest lookup, setup/checksum download, verification, diagnostics, and installer launch.
- `version.py`: application version and product/repository constants.
- `build_icon.py`: generates the Windows `.ico` used by packaging.
- `build_version_info.py`: Windows executable metadata generation.
- `build_installer_config.py`: Inno Setup version/branding generation.
- `installer/DAD.iss`: per-user Windows installer.

## Packaging and updates

PyInstaller builds Dad Image Tool in **onedir** mode. Inno Setup installs the complete runtime folder while presenting a normal single application shortcut to the user. Onedir packaging avoids the temporary `_MEI...` extraction path used by PyInstaller onefile builds.

The release PyInstaller command adds `internal/learning_lab` as bundled data under `learning_lab`. In the installed onedir runtime this is expected at `_internal\learning_lab`. CI fails the release if the Learning Lab entry page is missing from either the packaged or installed application.

Before PyInstaller runs, the build generates `Dad-Image-Tool.ico` from the embedded horse asset. PyInstaller embeds it in `Dad Image Tool.exe`, and Inno Setup uses the same icon for the setup executable. Runtime dependencies that require package data or dynamic imports, including `extract-msg`, are explicitly collected in both test-installer and release builds.

The in-app updater does not replace `Dad Image Tool.exe` directly. It downloads the released `Dad-Image-Tool-Setup.exe` plus its SHA-256 checksum, verifies the installer, closes the application, and runs setup silently.

Update discovery has two independent GitHub paths. The primary path uses `api.github.com/.../releases/latest`. If that fails, the updater requests `Dad-Image-Tool-Update.json` through the ordinary `github.com/.../releases/latest/download/` path, then downloads version-pinned setup/checksum assets.

Before copying the replacement runtime, setup removes only known obsolete application-runtime paths such as the previous executable, `_internal`, and legacy updater backup files. User data lives outside the install directory and is not part of that cleanup.

CI smoke-tests both the packaged executable and an installed copy. The installer workflow also performs an upgrade-cleanup/data-preservation test and verifies the Learning Lab bundle before publishing the setup executable.
