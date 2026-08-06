# Dad Image Tool

A simple Windows desktop utility for downloading client photos from shared links and converting them into standard JPEG files.

## Primary use case

The user receives groups of equine client photos through emailed Dropbox, Google Drive, and other sharing links. The tool does not connect to or read email. The user copies links from an email or drags downloaded files into the program.

The tool should make different sources feel the same by collecting supported images, converting them to `.jpg`, and placing them in a clearly named local folder.

## Planned workflow

1. Paste one or more shared links, or add local files, folders, and ZIP archives.
2. Choose a destination folder and optional client or horse name.
3. Click **Download and Convert**.
4. Review the completed files and any failures.

## Initial scope

- Public Dropbox file and folder links
- Public Google Drive file and folder links
- Direct image URLs
- Downloaded ZIP archives containing images
- Local files and folders through file selection or drag and drop
- Recursive ZIP extraction, including images stored inside subfolders
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

## Target platform

Windows desktop application packaged as a standalone `.exe`, so the end user does not need Python or a command prompt.

## Status

Project definition and initial architecture.
