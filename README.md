# Dad Image Tool

Dad Image Tool is a Windows utility that automatically converts client pictures into standard JPEG files.

It does not download files from email or cloud services. Download or save the client item normally, then put it into the **Drop Client Pictures Here** desktop shortcut. Dad Image Tool handles the conversion, keeps the original, and opens the finished pictures automatically.

## Install

1. Download **Dad-Image-Tool-Setup.exe** from the latest release.
2. Double-click it.
3. Follow the setup window and choose **Install**.
4. Leave **Open Dad Image Tool now** checked and choose **Finish**.

No Python, Git, PowerShell, Command Prompt, or other technical setup is required.

See [USER_GUIDE.md](USER_GUIDE.md) for daily use and troubleshooting.

## What it does

- Watches the **Drop Client Pictures Here** folder.
- Converts JPG, JPEG, PNG, HEIC, HEIF, WebP, TIFF, and BMP pictures to JPEG.
- Processes folders and ZIP files, including nested folders and ZIPs.
- Moves successful originals to **Originals Archive**.
- Moves unsuccessful or unsupported items to **Needs Attention** instead of deleting them.
- Keeps a job history.
- Checks for application updates.

## About the name

The application name is **Dad Image Tool**. D.A.D. is only a secondary nickname for **Dad's Automated Dropzone**; it is not intended to be the main product name.

## Current state

Version 0.3.0 is a pre-release build undergoing real Windows acceptance testing before it is given to the end user.

Developer source, build tools, and maintenance documentation are kept under `internal/` so the repository root stays focused on the files an end user may actually need.