# D.A.D. — Dad Image Tool

**D.A.D.** stands for **Dad's Automated Downloader**.

**Download • Archive • Deliver**

Dad Image Tool is the Windows application behind D.A.D. It turns downloaded client pictures into standard JPEG files through one watched folder. The official application name, executable, Windows shortcuts, data folders, and repository name remain unchanged.

## Intended experience

1. Save pictures, folders, or ZIP files into **Drop Client Pictures Here**.
2. Dad Image Tool waits until the item has finished downloading.
3. Supported pictures are converted into JPEG files.
4. The finished folder opens automatically.
5. Successful originals are retained in **Originals Archive**.
6. Incomplete or failed items are retained in **Needs Attention**.

## Official identity

- **Brand:** D.A.D.
- **Meaning:** Dad's Automated Downloader
- **Application:** Dad Image Tool
- **Tagline:** Download • Archive • Deliver
- **Executable:** `Dad Image Tool.exe`
- **Desktop shortcuts:** `Dad Image Tool` and `Drop Client Pictures Here`

## Architecture

The watched folder is the only durable input interface. Outlook, Dropbox, Google Drive, Google Photos, OneDrive, SharePoint, iCloud, Box, and other services remain outside the application. The user downloads from those services normally and saves the result into the watched folder.

At runtime the application manages:

```text
Pictures/Dad Image Tool/
├── Drop Client Pictures Here/
├── Finished/
├── Originals Archive/
├── Needs Attention/
└── job-history.jsonl
```

Each top-level item is processed independently. One failed item must not cause an unrelated successful original to be treated as failed.

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

## Safety principles

- One workflow for every source.
- Automatic processing with plain-English status messages.
- No browser extension or provider-specific integration.
- No conversion settings for the end user.
- Original files are never deleted by processing or updating.
- Existing files are never overwritten.
- Failed or uncertain items are kept for review.
- Updates must not touch user folders.

## Documentation

- [USER_GUIDE.md](USER_GUIDE.md): installation, daily use, and simple troubleshooting.
- [DEVELOPMENT.md](DEVELOPMENT.md): architecture, branding contract, safety rules, and build details.
- [RELEASING.md](RELEASING.md): versioning and release procedure.
- [TESTING.md](TESTING.md): automated and manual acceptance testing.

## Current state

Version 0.2.2 is a pre-release build. Automated tests and the Windows build pipeline exist, but the installer, packaged formats, forwarded-client samples, startup behavior, and update path still require real Windows acceptance testing before Dad receives it.
