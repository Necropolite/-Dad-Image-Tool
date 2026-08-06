# Dad Image Tool User Guide

## Install

1. On the GitHub page, click the green **Code** button.
2. Click **Download ZIP**.
3. Open the Downloads folder.
4. Right-click the downloaded ZIP and choose **Extract All**.
5. Open the extracted folder.
6. Double-click **Install.bat**.

Windows may show a warning because this is a private personal app. Choose **More info**, then **Run anyway**.

The installer creates:

- A desktop shortcut named **Dad Image Tool**.
- A desktop shortcut named **Drop Client Pictures Here**.
- The folders used for finished pictures, archived originals, and files needing attention.
- An automatic startup entry so Dad Image Tool starts when Windows starts.

## Daily use

### Email attachments

1. In Outlook, save the picture, pictures, ZIP file, or folder.
2. Choose the desktop folder **Drop Client Pictures Here** as the save location.
3. Wait for Dad Image Tool to finish.
4. The finished JPEG folder opens automatically.

### Dropbox, Google Drive, OneDrive, iCloud, Box, or another website

1. Open the client link normally.
2. Use the website's **Download** button.
3. Save the download into **Drop Client Pictures Here**.
4. Dad Image Tool handles the downloaded file, folder, or ZIP automatically.

### Files already on the computer

Drag the picture, folder, or ZIP file onto the **Dad Image Tool** window, or copy it into **Drop Client Pictures Here**.

## Where files go

Dad Image Tool uses four folders inside:

`Pictures\Dad Image Tool`

### Drop Client Pictures Here

Put new client pictures, folders, and ZIP files here.

### Finished

Completed JPEG files are stored here in dated folders.

### Originals Archive

Original files are moved here after successful conversion. Keep them until the finished JPEG files have been checked.

### Needs Attention

Anything that could not be processed is moved here instead of being deleted.

## What happens automatically

Dad Image Tool will:

- Wait until a download has finished.
- Open ZIP files.
- Search through folders and subfolders.
- Convert supported pictures to JPEG.
- Correct phone-picture rotation.
- Prevent duplicate filenames from overwriting each other.
- Keep the original files.
- Open the completed folder.

## Supported picture types

- JPG and JPEG
- PNG
- HEIC and HEIF
- WebP
- TIFF
- BMP

## If something does not work

### The file went to Needs Attention

Open **Needs Attention** and check the original file. It may be damaged, password protected, incomplete, or an unsupported type.

### No finished pictures appeared

Make sure the download is complete and that the item contains a supported picture. Dad Image Tool ignores unrelated documents.

### A cloud website will not download

The client link may require permission or may have expired. Ask the client for a new public link.

### Dad Image Tool is not running

Double-click the **Dad Image Tool** shortcut on the desktop. It normally starts automatically with Windows.

## Remove the program

Open the extracted project folder and double-click **Uninstall.bat**.

The uninstall process removes the installed program and shortcuts. It does not automatically delete the client pictures stored under `Pictures\Dad Image Tool`.
