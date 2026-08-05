# Dad Image Tool

A simple Windows desktop utility for downloading client photos from shared links and converting them into standard JPEG files.

## Primary use case

The user receives groups of equine client photos from services such as Dropbox and Google Drive. The tool should make those sources feel the same by downloading supported images, converting them to `.jpg`, and placing them in a clearly named local folder.

## Planned workflow

1. Paste one or more shared links.
2. Choose a destination folder and optional client or horse name.
3. Click **Download and Convert**.
4. Review the completed files and any failures.

## Initial scope

- Public Dropbox file and folder links
- Public Google Drive file and folder links
- Direct image URLs
- ZIP archives containing images
- Local files and folders as a fallback
- JPEG output with original resolution and corrected orientation
- Safe duplicate filenames
- Clear progress and failure reporting

## Supported input formats

Planned support includes JPEG, PNG, WebP, HEIC, TIFF, BMP, and other formats supported by Pillow and optional plugins.

## Important limits

Links that require account login, have expired, or block automated downloads may not work. The program should report these clearly and allow the user to download the files manually and then drag them into the converter.

## Target platform

Windows desktop application packaged as a standalone `.exe`, so the end user does not need Python or a command prompt.

## Status

Project definition and initial architecture.
