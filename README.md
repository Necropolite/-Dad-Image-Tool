# Dad Image Tool

A simple Windows desktop utility for downloading client photos from shared links and converting them into standard JPEG files.

## Primary use case

The user receives groups of equine client photos through emailed Dropbox, Google Drive, and other sharing links. The tool does not connect to or read email. The user copies links from an email, right-clicks supported links in the browser, or drags downloaded files into the program.

The tool should make different sources feel the same by collecting supported images, converting them to `.jpg`, and placing them in a clearly named local folder.

## Planned workflow

The tool should support three starting methods:

1. Right-click a link in the web browser and choose **Send to Dad Image Tool**.
2. Paste one or more shared links into the desktop app.
3. Add local files, folders, or ZIP archives through file selection or drag and drop.

After input is received:

1. Choose or confirm the destination folder and optional client or horse name.
2. Start the download and conversion process.
3. Review the completed files and any failures.

## Browser integration

A small Chromium browser extension should add **Send to Dad Image Tool** to the right-click menu for hyperlinks. It should support Google Chrome and Microsoft Edge initially.

The extension should send only the clicked URL to the locally installed Windows application through the browser's native messaging interface. It should not read email messages, browsing history, page contents, passwords, or account data.

When a link is sent, the Windows app should open or come to the foreground, display the received URL, and allow the user to confirm the destination before processing. A later optional setting may allow trusted links to begin automatically.

The Windows installer should install both the desktop app and the native messaging host registration. The browser extension may initially be installed manually during development, then packaged for easier installation once stable.

## Initial scope

- Public Dropbox file and folder links
- Public Google Drive file and folder links
- Direct image URLs
- Downloaded ZIP archives containing images
- Local files and folders through file selection or drag and drop
- Recursive ZIP extraction, including images stored inside subfolders
- Chrome and Edge right-click link integration
- JPEG output with original resolution and corrected orientation
- Safe duplicate filenames
- Clear progress and failure reporting
- No direct email access or mailbox permissions

## Supported input formats

Planned support includes JPEG, PNG, WebP, HEIC, TIFF, BMP, and other formats supported by Pillow and optional plugins.

## ZIP handling

ZIP archives may be added directly to the program. The tool should extract them into temporary storage, find supported images throughout the archive, convert those images to JPEG, and ignore unrelated files. Temporary extracted files should be removed after processing.

Password-protected, damaged, or unsupported archives should be reported clearly rather than causing the entire job to fail.

## Important limits

Links that require account login, have expired, or block automated downloads may not work. The program should report these clearly and allow the user to download the files manually and then drag them into the converter.

The browser right-click option requires the browser extension and the Windows desktop application to both be installed. A normal Windows File Explorer context-menu entry cannot directly appear when right-clicking a hyperlink inside a browser.

## Target platform

Windows desktop application packaged as a standalone `.exe`, so the end user does not need Python or a command prompt.

## Status

Project definition and initial architecture.
