# Dad Image Tool

Dad Image Tool is a Windows utility that automatically converts client pictures into standard JPEG files.

## Install

The installer is kept right here in the top folder of the repository:

**Dad-Image-Tool-Setup.exe**

1. Double-click **Dad-Image-Tool-Setup.exe**.
2. Follow the setup window and choose **Install**.
3. Leave **Open Dad Image Tool now** checked and choose **Finish**.

No Python, Git, PowerShell, Command Prompt, or other technical setup is required.

See [USER_GUIDE.md](USER_GUIDE.md) for daily use and troubleshooting.

## Daily use

1. Download or save the client pictures, folder, or ZIP file normally.
2. Put the item into the desktop shortcut named **Drop Client Pictures Here**.
3. Wait while Dad Image Tool works.
4. The finished JPEG folder opens automatically.

Dad Image Tool does not download files from email or cloud services. It converts files after they have been saved to the computer.

## What it does

- Watches the **Drop Client Pictures Here** folder.
- Converts JPG, JPEG, PNG, HEIC, HEIF, WebP, TIFF, and BMP pictures to JPEG.
- Processes folders and ZIP files, including nested folders and ZIPs.
- Moves successful originals to **Originals Archive**.
- Moves unsuccessful or unsupported items to **Needs Attention** instead of deleting them.
- Keeps a job history.
- Checks for application updates.

## About the name

The application is **Dad Image Tool**. D.A.D. is only a secondary nickname meaning **Dad's Automated Dropzone**.

## Current state

Version 0.3.0 is a pre-release build undergoing real Windows acceptance testing before it is given to the end user.

Developer source, build tools, tests, and maintenance documentation are kept under `internal/` and other infrastructure folders so the repository root stays focused on the files an end user may actually need.
