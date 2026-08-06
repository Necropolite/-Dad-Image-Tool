# Dad Image Tool

A simple Windows utility that turns client photo links, image files, folders, and ZIP archives into ordinary JPEG files.

## Primary goal

The end user is an equine specialist who wants one simple process regardless of where clients sent their pictures. The program must hide differences between Dropbox, Google Drive, ZIP files, image formats, and other supported sources.

The core design rule is:

> Never make the user think about where the pictures came from.

The normal experience should be:

1. Click or send the link to Dad Image Tool.
2. Wait while the program handles the source automatically.
3. Open the finished folder of JPEG files.

No email access, account management, technical settings, or source-specific modes should be required.

## Starting methods

The tool should support:

1. Right-click a hyperlink in Chrome or Edge and choose **Send to Dad Image Tool**.
2. Open a supported link through Dad Image Tool using the browser integration.
3. Paste one or more links into the app as a fallback.
4. Drag in local images, folders, or ZIP archives.
5. Select files, folders, or ZIP archives through a normal file picker.

## Link choice experience

When a supported link is sent to the app, the user should have three clear choices:

- **Use Dad Image Tool this time**
- **Always use Dad Image Tool for this source**
- **Open in the original browser**

The remembered choice should be stored by source, such as Dropbox or Google Drive, rather than affecting every web link. The app must provide a simple way to reset remembered choices.

Because normal `https://` links belong to the browser, source-specific handling should be implemented through the browser extension and the installed desktop app rather than attempting to replace the system browser for all web links.

## Automatic processing

After a job starts, the app should automatically:

1. Detect the source.
2. Download available files.
3. Extract ZIP archives when needed.
4. Search subfolders for supported images.
5. Correct image orientation.
6. Convert supported images to JPEG.
7. Preserve original resolution where practical.
8. Rename duplicate filenames safely.
9. Remove temporary files.
10. Open the completed output folder.

The program should not ask unnecessary questions during processing.

## Simple interface

The main window should stay minimal. It should show only:

- What the app is currently doing
- Basic progress
- A plain-language result
- **Open Folder**
- **Done**

Advanced options should be hidden from the normal workflow.

Example completion summary:

```text
42 pictures saved as JPEG
2 duplicate names were renamed
1 unsupported file was skipped
```

## Output folders

Each batch should be kept together automatically.

Preferred naming:

```text
2026-08-05 - Smith Horse
```

When no client or horse name is available:

```text
2026-08-05 14-37
```

The app may offer a simple name field, but it should not block processing if left empty.

## Queue behavior

If another link or file is sent while a job is running, it should be added to a queue rather than interrupting the current job. The queue should process automatically in order without requiring management from the user.

## Initial source support

- Public Dropbox file links
- Public Dropbox folder links
- Public Google Drive file links
- Public Google Drive folder links
- Direct image URLs
- Direct ZIP URLs
- Downloaded ZIP archives
- Local image files
- Local folders
- Reasonable fallback handling for unknown public links

## Supported image formats

Planned support includes:

- JPEG
- PNG
- WebP
- HEIC and HEIF
- TIFF
- BMP
- Other formats supported by Pillow and optional plugins

## ZIP handling

ZIP archives may be added directly or downloaded from a link. The tool should:

- Extract them into temporary storage
- Search recursively through subfolders
- Convert supported images
- Ignore unrelated files
- Clean up temporary files afterward

Password-protected, damaged, or unsupported archives should fail gracefully without stopping other queued jobs.

## Browser integration

A small Chromium extension should support Google Chrome and Microsoft Edge.

It should:

- Add **Send to Dad Image Tool** when right-clicking a hyperlink
- Pass only the selected link to the installed Windows application
- Allow the app to offer one-time, always-use, and original-browser choices
- Avoid reading email contents, browsing history, passwords, or unrelated page data

The Windows installer should install the desktop app and its native messaging registration. The browser extension may be installed manually during development and packaged more cleanly later.

## Plain-language errors

The user should never see raw technical errors, HTTP codes, or stack traces.

Examples:

- **This link requires you to sign in.**
- **This link has expired.**
- **No pictures were found.**
- **This ZIP file is damaged or password protected.**
- **Dad Image Tool could not download this link. Open it in your browser instead.**

Technical details may be written to a log for troubleshooting, but they should stay hidden from the normal interface.

## Important limits

Some links may require login, expire, block automated downloads, or use an unsupported sharing service. When automatic handling fails, the app should offer **Open in Browser** and allow the user to download the files manually and drag them into the app.

## Target platform

Windows desktop application packaged as a standalone `.exe`, so the end user does not need Python or a command prompt.

## Status

Project definition and initial architecture.