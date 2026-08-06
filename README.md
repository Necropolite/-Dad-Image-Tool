# Dad Image Tool

Dad Image Tool turns pictures from Dropbox, Google Drive, ZIP folders, and other common sources into ordinary JPEG files on a Windows computer.

It is designed to be simple:

1. Click the picture link in the email.
2. Choose Dad Image Tool or the normal browser.
3. Wait for the finished JPEG folder to open.

The app does not read email, passwords, or account information.

## Install it

### 1. Download the project

On this GitHub page, click the green **Code** button, then click **Download ZIP**.

Open the Downloads folder, right-click the downloaded ZIP, and choose **Extract All**.

### 2. Run the installer

Open the extracted folder and double-click:

**`Install.bat`**

Windows may show a warning because this is a personal app and is not digitally signed. Choose **More info**, then **Run anyway**.

Follow the instructions shown by the installer. When installation finishes, Dad Image Tool opens automatically.

## Use it

### From an email link

Click a supported picture link normally.

The first time for that source, choose whether to:

- Use Dad Image Tool this time
- Always use Dad Image Tool
- Open the link normally in the browser

Dad Image Tool downloads the pictures, extracts ZIP folders when needed, converts the pictures to JPEG, and opens the finished folder.

### From downloaded files

Open Dad Image Tool from the desktop shortcut. Then:

- Drag pictures or ZIP folders onto the window
- Click **Add Files or ZIP**
- Click **Add Folder**
- Paste a link and click **Add Link**

Click **Start**. Finished pictures are normally stored in:

`Pictures\Dad Image Tool`

Each job gets its own dated folder.

## What it handles

- Public Dropbox file and folder links
- Public Google Drive file and folder links
- Direct picture links
- ZIP folders containing pictures
- Local pictures and folders
- JPEG, PNG, WebP, HEIC, HEIF, TIFF, and BMP pictures
- Pictures stored inside subfolders
- Duplicate filenames
- Phone-photo rotation

## Simple error messages

The program reports problems in plain language, such as:

- The link requires permission or sign-in
- The link no longer exists
- The ZIP folder is damaged
- No supported pictures were found

Private, expired, or login-protected links may need to be downloaded normally first and then dragged into Dad Image Tool.

## Remove it

Run **`Uninstall.bat`** from the downloaded project folder.

## Current status

This repository contains the first working MVP. It has not yet been fully tested across every version of Windows or every type of Dropbox and Google Drive link. Test it with non-critical copies before relying on it for the only copy of client pictures.
