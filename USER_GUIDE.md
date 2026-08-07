# Dad Image Tool User Guide

Dad Image Tool converts client photos to JPEG after they are placed in the **Drop Client Pictures Here** folder. It can also extract photos from folders, ZIP files, DOCX files, and PDFs.

## Install Dad Image Tool

Download the current installer here:

[**Download Dad Image Tool for Windows**](https://github.com/Necropolite/-Dad-Image-Tool/releases/latest/download/Dad-Image-Tool-Setup.exe)

The downloaded file is named `Dad-Image-Tool-Setup.exe`.

### Browser warning

Microsoft Edge may say that the installer "isn't commonly downloaded." This is a reputation warning for a small unsigned application, not an indication that the download failed.

If Edge pauses the download, open the Downloads panel, use the menu beside `Dad-Image-Tool-Setup.exe`, and choose **Keep**.

### Windows SmartScreen

Windows may show **Windows protected your PC** when the installer opens. If it does:

1. Click **More info**.
2. Confirm the filename is `Dad-Image-Tool-Setup.exe`.
3. Click **Run anyway**.

### Setup

Run the installer and click **Install**. When setup finishes, leave **Open Dad Image Tool now** checked and click **Finish**.

Setup creates two desktop shortcuts:

- **Dad Image Tool** — opens the application.
- **Drop Client Pictures Here** — opens the watched input folder.

Dad Image Tool also starts automatically when you sign in to Windows.

## Daily workflow

1. Save or download the client's files normally.
2. Drag the original picture, folder, ZIP, DOCX, or PDF into **Drop Client Pictures Here**.
3. Wait for processing to finish.
4. The Finished batch opens automatically.
5. Move the resulting JPEGs into whatever folder you use for that horse or trim.

There is no Start button and there are no conversion settings to choose.

Do not manually unpack ZIP files or copy pictures out of DOCX or PDF files first. Drop the original item and let Dad Image Tool handle it.

## Supported inputs

### Image files

- JPG and JPEG
- PNG
- HEIC and HEIF
- WebP
- TIFF
- BMP

All supported images are written as JPEG files. Phone-photo orientation is corrected when the source contains orientation information.

### Folders and ZIP files

Folders are searched recursively. ZIP files are extracted internally and may contain folders, additional ZIP files, DOCX files, PDFs, and supported images.

The original folder/ZIP organization is preserved in the Finished batch where practical. ZIP files using Deflate64 compression are supported.

### DOCX files

DOCX files are treated as containers for embedded pictures. Dad Image Tool extracts supported pictures in document order, converts them to JPEG, and groups them under a folder named after the document.

This includes DOCX files exported from Google Docs.

### PDF files

PDF files are also treated as photo containers. Dad Image Tool extracts embedded raster pictures at their embedded resolution when possible and groups them under a folder named after the PDF.

It does not normally turn entire PDF pages into screenshots. If several photos have already been flattened into one page image, only that combined image may be recoverable.

### Unsupported items

Videos, older `.doc` files, and other unsupported formats are moved to **Needs Attention** rather than deleted.

## File locations

Dad Image Tool stores its working files under your Windows Pictures folder:

```text
Pictures\Dad Image Tool\
├── Drop Client Pictures Here\
├── Finished\
├── Originals Archive\
├── Needs Attention\
└── job-history.jsonl
```

**Finished** contains dated conversion batches. Items dropped together are kept in the same batch.

**Originals Archive** contains unchanged source items after a fully successful conversion.

**Needs Attention** contains source items that could not be completed safely or did not contain usable supported pictures.

## Main window

The application window shows the current status and provides buttons to:

- open the drop folder;
- open Finished;
- view job history;
- check for updates;
- view About information.

Only one copy of Dad Image Tool runs at a time.

## Updates

Dad Image Tool checks GitHub for a newer released version after startup. You can also click **Check for Updates**.

When an update is available, approve it and wait. Dad Image Tool downloads the verified setup program, closes, installs the new version, and opens again.

Updates clean obsolete application-runtime files when necessary but do not remove anything under `Pictures\Dad Image Tool`.

## Troubleshooting

### The installer was blocked by Edge

Open Edge's Downloads panel, use the menu beside `Dad-Image-Tool-Setup.exe`, and choose **Keep**.

### Windows says "Windows protected your PC"

Click **More info**, verify the installer filename, then choose **Run anyway**.

### An item went to Needs Attention

The source may be damaged, password protected, incomplete, unsupported, or may not contain a usable supported picture. The original is retained so it can be inspected or tried again later.

### A DOCX or PDF did not produce the expected pictures

Keep the original. Some documents store pictures in unusual ways or flatten several photos into a single page image. The source file is the best material for diagnosing or improving support later.

### No Finished folder opened

Check **Needs Attention** and confirm the original download or file copy had finished before Dad Image Tool began processing it.

### Dad Image Tool will not open

Run `Dad-Image-Tool-Setup.exe` again over the existing installation. A repair installation replaces the application files and shortcuts without deleting the Pictures data folders or job history.

### A desktop shortcut is missing

Run the installer again. Setup recreates the shortcuts without removing client data.

## Uninstall

Open **Windows Settings → Apps**, find **Dad Image Tool**, and choose **Uninstall**.

Uninstalling removes the application and its shortcuts. It does not delete `Pictures\Dad Image Tool` or the files stored there.
