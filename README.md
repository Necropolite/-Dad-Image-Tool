# D.A.D. — Dad's Automated Downloader

**Download • Archive • Deliver**

**D.A.D.** is the official project identity for **Dad Image Tool**, a Windows application that turns client pictures into standard JPEG files through one watched folder.

The Windows application, executable, shortcuts, repository, and data folders remain named **Dad Image Tool**. D.A.D. provides the professional identity around that familiar application name:

- **Download:** save a downloaded picture, folder, or ZIP file into the drop folder.
- **Archive:** retain successful originals in `Originals Archive`.
- **Deliver:** open a finished folder containing standardized JPEG files.

The current version does not sign in to Outlook or cloud services and does not download from them directly. The user downloads normally, saves the item into the watched folder, and D.A.D. automates the remaining workflow.

## Vision

The program should require almost no computer knowledge and very few decisions. Reliability, safety, and a consistent routine matter more than advanced controls.

The intended experience is:

1. Save pictures, folders, or ZIP files into **Drop Client Pictures Here**.
2. Dad Image Tool waits until the item has finished downloading.
3. Supported pictures are converted into JPEG files.
4. The finished folder opens automatically.
5. Successful originals are retained in **Originals Archive**.
6. Incomplete or failed items are retained in **Needs Attention**.

## Architecture

The watched folder is the only durable input interface. Outlook, Dropbox, Google Drive, Google Photos, OneDrive, SharePoint, iCloud, Box, and other services remain outside the application. The user downloads from those services normally and saves the result into the watched folder.

At runtime the application manages:

```text
Pictures/Dad Image Tool/
├── Drop Client Pictures Here/
├── Finished/
├── Originals Archive/
└── Needs Attention/
```

Each top-level item is processed independently. One failed item must not cause an unrelated successful original to be treated as failed.

## Design principles

- One workflow for every source.
- Automatic processing with plain-English status messages.
- No browser extension or provider-specific integration.
- No conversion settings for the end user.
- Original files are never deleted by processing or updating.
- Existing files are never overwritten.
- Failed or uncertain items are kept for review.
- Updates must not touch user folders.
- Branding must not rename or break established technical paths.

## Supported inputs

Images:

- JPG and JPEG
- PNG
- HEIC and HEIF
- TIFF
- BMP
- WebP

Containers:

- ZIP files, including nested ZIP files
- Folders and nested folders

All successful output is saved as JPEG with orientation corrected from EXIF data.

## Documentation

- [USER_GUIDE.md](USER_GUIDE.md): installation, daily use, and simple troubleshooting.
- [DEVELOPMENT.md](DEVELOPMENT.md): architecture, branding boundaries, safety rules, and build details.
- [RELEASING.md](RELEASING.md): versioning and release procedure.
- [TESTING.md](TESTING.md): automated and manual acceptance testing.
- [REVIEW_GUIDE.md](REVIEW_GUIDE.md): architecture, threat model, safety invariants, and third-party review priorities.

## Long-term direction

D.A.D. should eventually be distributed like ordinary commercial Windows software. Future work should reduce first-install complexity without changing the Dad Image Tool executable, shortcut names, or watched-folder workflow unless a deliberate migration plan is created.
