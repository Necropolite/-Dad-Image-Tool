# Dad Image Tool

Dad Image Tool is a simple Windows utility that turns client pictures into standard JPEG files without requiring the user to understand image formats, ZIP files, cloud services, or conversion software.

The project is being built for an equine specialist who receives pictures from clients through email attachments, ZIP folders, Dropbox, Google Drive, OneDrive, iCloud, Box, and other sources. The goal is to reduce all of those sources to one repeatable action:

> Save or drop the client files into one folder.

Dad Image Tool watches that folder, processes new items automatically, and opens a finished folder containing JPEG copies.

## Project vision

The program should stay out of the user's way. It should not require the user to choose conversion settings, identify the source service, extract ZIP files, correct phone-picture rotation, or resolve duplicate filenames.

The intended experience is:

1. Save pictures, folders, or ZIP files into **Drop Client Pictures Here**.
2. Dad Image Tool notices them automatically.
3. Finished JPEG files appear under **Finished**.
4. Original files are retained in **Originals Archive** until they can be reviewed or removed.

## Core design principles

- One consistent workflow regardless of where the pictures came from.
- Automatic processing with as few questions as possible.
- Plain-language messages instead of technical errors.
- Original files retained after successful processing.
- Failed items moved to **Needs Attention** instead of being lost.
- The watched-folder workflow remains usable even if Outlook or a cloud service changes.

## Current architecture

The Windows app creates and manages these folders inside `Pictures\Dad Image Tool`:

- **Drop Client Pictures Here**: watched input folder.
- **Finished**: dated folders containing converted JPEG files.
- **Originals Archive**: original files after successful processing.
- **Needs Attention**: items that could not be processed completely.

The program checks the incoming folder automatically, waits for downloads to finish, processes stable files one batch at a time, and opens the completed output folder.

The existing conversion engine supports ordinary image files, nested folders, ZIP archives, direct links, and shared links from major services when those links are added manually. The watched folder is the primary workflow because it works with Outlook attachments and files downloaded from any service.

## Supported image formats

- JPEG and JPG
- PNG
- HEIC and HEIF
- WebP
- TIFF
- BMP

All successful output is saved as JPEG.

## Documentation

For installation and daily use, read [USER_GUIDE.md](USER_GUIDE.md).

For development details and project structure, read [DEVELOPMENT.md](DEVELOPMENT.md).

## Future direction

An optional Outlook feeder may later add a **Send to Dad Image Tool** button that saves attachments and supported links into the watched folder. It should remain optional so the core program is not dependent on Outlook.
