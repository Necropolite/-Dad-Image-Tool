# D.A.D. — Dad Image Tool User Guide

**D.A.D.** means **Dad's Automated Dropzone**.

**Drop • Archive • Deliver**

The application itself is called **Dad Image Tool**.

## Install

1. Download **DAD-Setup.exe**.
2. Double-click **DAD-Setup.exe**.
3. If Windows displays a protection message, choose **More info**, then **Run anyway**.
4. Follow the setup window and choose **Install**.
5. Leave **Open D.A.D. now** checked and choose **Finish**.

No Python, GitHub software, command line, PowerShell, or technical setup is required.

Setup creates:

- A desktop shortcut named **Dad Image Tool**.
- A desktop shortcut named **Drop Client Pictures Here**.
- A normal Windows uninstall entry.
- Automatic startup when the user signs in to Windows.

## Daily use

1. Download or save the client pictures, folder, or ZIP file normally.
2. Put the downloaded item into **Drop Client Pictures Here** on the desktop.
3. Wait while Dad Image Tool works.
4. The finished JPEG folder opens automatically.

Use the same steps for Outlook, Dropbox, Google Drive, Google Photos, OneDrive, SharePoint, iCloud, Box, or any other source.

D.A.D. does not download files itself. It watches the drop folder and begins after the copied or downloaded item stops changing.

## Main window

The main window displays:

- **D.A.D.**
- **Dad's Automated Dropzone**
- **Drop • Archive • Deliver**
- The current Dad Image Tool version

Click **About D.A.D.** to confirm the installed identity and version.

## Where files go

Dad Image Tool uses four folders inside the Windows Pictures folder under `Dad Image Tool`.

### Drop Client Pictures Here

Save new client pictures, folders, and ZIP files here.

### Finished

Converted JPEG files are stored here in dated folders.

### Originals Archive

Successful original files are moved here. Keep them until the finished JPEG files have been checked.

### Needs Attention

Anything that could not be completed is moved here instead of being deleted.

## Job history

Open Dad Image Tool and click **View History** to see recent jobs.

A completed entry shows when it finished, the source name, how many JPEG files were made, and whether it needs attention. Double-click a completed entry to open its finished folder.

## Updates

Dad Image Tool checks for a newer released version after it starts.

When an update is available:

1. Choose **Yes** when asked whether to install it.
2. Wait while it downloads.
3. Dad Image Tool closes, updates itself, and opens again.

Updates do not remove client pictures, finished pictures, archived originals, items needing attention, or job history.

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

The item may be damaged, password protected, incomplete, unsupported, or may not contain a supported picture. The original was kept so it can be checked or saved again.

### No finished folder opened

Open **Needs Attention** and check the most recent item. Also confirm the download or copy finished before closing Outlook or the browser.

### Dad Image Tool is not running

Double-click the **Dad Image Tool** desktop shortcut. Only one copy can run at a time.

### An update will not install

The installed version should continue working. Check the internet connection and try **Check for Updates** later.

### A desktop shortcut is missing

Run **DAD-Setup.exe** again. Reinstalling repairs the program and shortcuts without deleting client files.

## Remove the program

Open **Windows Settings**, go to **Apps**, find **Dad Image Tool**, and choose **Uninstall**.

Uninstalling removes the program and shortcuts. It does not delete client folders under the Windows Pictures folder.
