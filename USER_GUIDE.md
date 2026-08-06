# D.A.D. — Dad Image Tool User Guide

**D.A.D.** means **Dad's Automated Downloader**.

**Download • Archive • Deliver**

The application itself is called **Dad Image Tool**. The executable, desktop shortcuts, and folders keep that name.

## Install

Dad Image Tool only needs a manual installation the first time.

1. Download the project ZIP from GitHub.
2. Open the Downloads folder.
3. Right-click the ZIP and choose **Extract All**.
4. Open the extracted folder.
5. Double-click **Install.bat**.
6. Leave the window open until it says the installation is finished.

Windows may show a warning because this is a private personal app. Choose **More info**, then **Run anyway**.

The installer creates two desktop shortcuts:

- **Dad Image Tool**
- **Drop Client Pictures Here**

Dad Image Tool also starts automatically with Windows.

## Daily use

1. Download or save the client pictures, folder, or ZIP file.
2. Save it into the desktop folder named **Drop Client Pictures Here**.
3. Wait while Dad Image Tool works.
4. The finished JPEG folder opens automatically.

Use the same steps for Outlook, Dropbox, Google Drive, Google Photos, OneDrive, SharePoint, iCloud, Box, or any other source.

Dad Image Tool waits for downloads to finish. There is no Start button and no conversion setting to choose.

## Main window

The main window displays:

- **D.A.D.**
- **Dad's Automated Downloader**
- **Download • Archive • Deliver**
- The current Dad Image Tool version

Click **About D.A.D.** to confirm the official identity and installed version.

## Where files go

Dad Image Tool uses four folders inside your Pictures folder:

`Pictures\Dad Image Tool`

### Drop Client Pictures Here

Save new client pictures, folders, and ZIP files here.

### Finished

The converted JPEG files are stored here in dated folders.

### Originals Archive

Successful original files are moved here. Keep them until the finished JPEG files have been checked.

### Needs Attention

An item that could not be completed is moved here instead of being deleted.

## Job history

Open Dad Image Tool and click **View History** to see recent jobs.

A completed history item shows when it finished, its source name, how many JPEG files were made, and whether it needs attention. Double-click a completed item to open its finished folder.

## Updates

Dad Image Tool checks for a newer released version after it starts.

When an update is available:

1. Choose **Yes** when asked whether to install it.
2. Wait while it downloads.
3. Dad Image Tool closes, updates itself, and opens again.

Updates do not remove client pictures, finished pictures, archived originals, or job history.

To check manually, open Dad Image Tool and click **Check for Updates**.

Automatic updates will not work until the release repository is public.

## Supported picture types

- JPG and JPEG
- PNG
- HEIC and HEIF
- WebP
- TIFF
- BMP

ZIP files and folders may contain more folders or ZIP files inside them.

Videos, Word documents, and other unsupported files are kept in **Needs Attention** rather than deleted.

## Troubleshooting

### The item went to Needs Attention

The item may be damaged, password protected, incomplete, or may not contain a supported picture. The original was kept so it can be checked or downloaded again.

### No finished folder opened

Open **Needs Attention** and check the most recent item. Also make sure the download finished before closing the browser or Outlook.

### Dad Image Tool is not running

Double-click the **Dad Image Tool** shortcut. Only one copy can run at a time.

### An update will not install

The current version should continue working. Check the internet connection and try **Check for Updates** later.

### The drop folder shortcut is missing

Open Dad Image Tool and click **Open Drop Folder**. Running **Install.bat** again also recreates the shortcuts without deleting client files.

## Remove the program

Open the extracted project folder and double-click **Uninstall.bat**.

The uninstaller removes the program and shortcuts. It does not delete the client folders under `Pictures\Dad Image Tool`.
