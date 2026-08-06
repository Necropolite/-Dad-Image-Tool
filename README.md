# D.A.D. — Dad Image Tool

**D.A.D.** stands for **Dad's Automated Dropzone**.

**Drop • Archive • Deliver**

Dad Image Tool is the Windows application behind D.A.D. It watches one drop folder, converts supported client pictures into standard JPEG files, archives successful originals, and preserves anything unsuccessful for review.

D.A.D. does **not** download files from Outlook, email, or cloud services. The user downloads or saves the source item normally, then places it into **Drop Client Pictures Here**.

## Intended experience

1. Install by double-clicking **DAD-Setup.exe**.
2. Download or save pictures, folders, or ZIP files normally.
3. Place them into the desktop shortcut **Drop Client Pictures Here**.
4. Dad Image Tool waits until the item has finished copying or downloading.
5. Supported pictures are converted into JPEG files.
6. The finished folder opens automatically.
7. Successful originals are retained in **Originals Archive**.
8. Incomplete or failed items are retained in **Needs Attention**.

The end user does not need Python, Git, PowerShell, Command Prompt, source code, or a GitHub account.

## Official identity

- **Brand:** D.A.D.
- **Meaning:** Dad's Automated Dropzone
- **Application:** Dad Image Tool
- **Tagline:** Drop • Archive • Deliver
- **Setup program:** `DAD-Setup.exe`
- **Executable:** `Dad Image Tool.exe`
- **Desktop shortcuts:** `Dad Image Tool` and `Drop Client Pictures Here`

See [BRANDING.md](BRANDING.md) for the permanent branding contract.

## Runtime folders

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
- Original files are never deleted by processing, updating, repair installation, or uninstall.
- Existing files are never overwritten.
- Failed or uncertain items are kept for review.
- Updates must not touch user folders.

## Documentation

- [USER_GUIDE.md](USER_GUIDE.md): installation, daily use, and simple troubleshooting.
- [DEVELOPMENT.md](DEVELOPMENT.md): architecture, safety rules, and build details.
- [RELEASING.md](RELEASING.md): versioning and release procedure.
- [TESTING.md](TESTING.md): automated and nontechnical acceptance testing.

## Current state

Version 0.3.0 is a pre-release build. The repository now builds a normal Windows setup program and a separate raw executable for in-app updates. Real Windows testing is still required for setup, SmartScreen behavior, startup, packaged image formats, forwarded-client samples, repair installation, uninstall safety, and self-updating before Dad receives it.
