# Dad Image Tool User Guide

Dad Image Tool converts client photos to JPEG after they are placed in the **Drop Client Pictures Here** folder. It can also extract photos from folders, ZIP files, DOCX files, PDFs, EML email files, and Outlook MSG files.

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

- **Dad Image Tool** opens the application.
- **Drop Client Pictures Here** opens the watched input folder.

Dad Image Tool also starts automatically when you sign in to Windows.

## Daily workflow

1. Save or download the client's files normally.
2. Drag the original picture, folder, ZIP, DOCX, PDF, EML, or MSG file into **Drop Client Pictures Here**.
3. Wait for processing to finish.
4. The Finished batch opens automatically.
5. Move the resulting JPEGs into whatever folder you use for that horse or trim.

There is no Start button and there are no conversion settings to choose.

Do not manually unpack ZIP files or copy pictures out of DOCX, PDF, EML, or MSG files first. Drop the original item and let Dad Image Tool handle it.

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

Folders are searched recursively. ZIP files are extracted internally and may contain folders, additional ZIP files, DOCX files, PDFs, EML files, MSG files, and supported images.

The original folder/ZIP organization is preserved in the Finished batch where practical. ZIP files using Deflate64 compression are supported.

### DOCX files

DOCX files are treated as containers for embedded pictures. Dad Image Tool extracts supported pictures in document order, converts them to JPEG, and groups them under a folder named after the document.

This includes DOCX files exported from Google Docs.

### PDF files

PDF files are also treated as photo containers. Dad Image Tool extracts embedded raster pictures at their embedded resolution when possible and groups them under a folder named after the PDF.

It does not normally turn entire PDF pages into screenshots. If several photos have already been flattened into one page image, only that combined image may be recoverable.

### EML email files

EML files are treated as email photo containers. Dad Image Tool extracts supported pictures stored as MIME image parts whether they are marked as normal attachments or displayed inline in the email body.

In Gmail, an email can be saved as an EML with **More → Download message**. Drop that downloaded `.eml` file into **Drop Client Pictures Here**. The email itself is not sent anywhere and Dad Image Tool does not connect to the email account.

### Outlook MSG files

Classic Outlook commonly saves messages as `.msg` files. Dad Image Tool treats MSG files as email photo containers and extracts supported image attachments, including pictures displayed inline in the message body when Outlook stores them as attachment data.

Save the message locally, then place the `.msg` file in **Drop Client Pictures Here**. Outlook does not need to remain open while Dad Image Tool processes the saved message.

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

The application window stays intentionally simple. It shows the current status and provides buttons to:

- open the drop folder;
- open Finished;
- view job history;
- open **Ask Pete (Experimental)**;
- open **Learning Lab (Experimental)**;
- check for updates.

Only one copy of Dad Image Tool runs at a time.

## Ask Pete (Experimental)

Click **Ask Pete (Experimental)** to open Pete's private Knowledge Core assistant in the default web browser.

The browser handles the private token, conversation, answers, and citations. Dad Image Tool does not receive or save that information and does not send client pictures to the assistant.

## Learning Lab (Experimental)

Click **Learning Lab (Experimental)** beside Ask Pete to open the interactive Learning Lab in the default web browser.

The Learning Lab is included with Dad Image Tool, so it does not require Python, Command Prompt, a local server, or a separate download. It has two main sections:

- **Learn** lets you browse prototype hoof-care topics, related subjects, suggested questions, and original HoofRehab source links.
- **Ask** lets you ask the teaching material questions and receive grounded answers with citations.

The Learning Lab will ask for the private access token when needed. The token and conversation remain in the browser rather than in Dad Image Tool. This Lite experiment uses public HoofRehab teaching material and does not include Pete's book or other private/paid teaching material.

## Updates

Dad Image Tool checks GitHub for a newer released version after startup. You can also click **Check for Updates**.

When an update is available, approve it and wait. Dad Image Tool downloads the verified setup program, closes, installs the new version, and opens again.

Current releases have a second GitHub release path available if the normal GitHub API check is unavailable. The installer checksum is still verified before setup is started.

Updates clean obsolete application-runtime files when necessary but do not remove anything under `Pictures\Dad Image Tool`.

## Troubleshooting

### The installer was blocked by Edge

Open Edge's Downloads panel, use the menu beside `Dad-Image-Tool-Setup.exe`, and choose **Keep**.

### Windows says "Windows protected your PC"

Click **More info**, verify the installer filename, then choose **Run anyway**.

### An item went to Needs Attention

The source may be damaged, password protected, incomplete, unsupported, or may not contain a usable supported picture. The original is retained so it can be inspected or tried again later.

### A DOCX, PDF, EML, or MSG did not produce the expected pictures

Keep the original. Some documents and emails store pictures in unusual ways. The source file is the best material for diagnosing or improving support later.

### No Finished folder opened

Check **Needs Attention** and confirm the original download or file copy had finished before Dad Image Tool began processing it.

### Ask Pete or Learning Lab will not answer

Confirm the computer has internet access and that the private access token entered in the browser is correct. Learning Lab's topic pages and source links can still open locally, but grounded AI answers require the private backend connection.

### Dad Image Tool will not open

Run `Dad-Image-Tool-Setup.exe` again over the existing installation. A repair installation replaces the application files and shortcuts without deleting the Pictures data folders or job history.

### A desktop shortcut is missing

Run the installer again. Setup recreates the shortcuts without removing client data.

## Uninstall

Open **Windows Settings → Apps**, find **Dad Image Tool**, and choose **Uninstall**.

Uninstalling removes the application, bundled Learning Lab files, and shortcuts. It does not delete `Pictures\Dad Image Tool` or the files stored there.
