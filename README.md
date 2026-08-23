# Dad Image Tool

Dad Image Tool is a Windows desktop utility built around a real image-processing workflow: client photos can arrive as individual image files, folders, ZIP archives, documents, PDFs, or saved emails.

The tool watches one desktop drop folder, extracts usable pictures, converts them to standard JPEG files, preserves the original source material, and routes anything it cannot safely finish to **Needs Attention**.

## Why it exists

The original workflow required repeatedly unpacking archives, opening documents or saved emails, extracting pictures, converting incompatible formats, and reorganizing the results by hand.

Dad Image Tool turns that into one action:

1. Save or download what the client sent.
2. Drop the original item into **Drop Client Pictures Here**.
3. Let the tool extract and convert the pictures automatically.
4. Work from the finished JPEG batch.

The goal is not to be a general document manager. It is a purpose-built utility that removes repetitive file handling from a specific daily workflow.

## Engineering highlights

- Python desktop application with a simple Windows UI and watched-folder workflow.
- Converts JPG/JPEG, PNG, HEIC/HEIF, WebP, TIFF, and BMP to standardized JPEG output.
- Handles folders, nested folders, ordinary ZIPs, nested ZIPs, and Deflate64 ZIP archives.
- Extracts embedded raster pictures from DOCX and PDF files without turning document pages into screenshots.
- Extracts inline and attached pictures from EML and Outlook MSG files.
- Applies image orientation metadata and avoids overwriting duplicate filenames.
- Preserves source/container structure where practical and keeps successful originals in an archive.
- Rejects unsafe ZIP paths and routes corrupt, unsupported, or incomplete inputs to **Needs Attention** instead of presenting partial work as successful.
- Records job history so completed and failed processing can be reviewed later.
- Packages as a normal Windows application with PyInstaller and Inno Setup.
- Includes an in-app updater that verifies the SHA-256 checksum of a released installer before installing it.
- GitHub Actions runs syntax checks, automated tests, packaged-application smoke tests, installer tests, and upgrade-preservation checks before release artifacts are published.

## Download

Download Dad Image Tool for Windows from the repository's **Releases** page.

The installer release asset is named `Dad-Image-Tool-Setup.exe`. Run it normally to install or repair Dad Image Tool.

Windows or Microsoft Edge may warn that the installer is not commonly downloaded. See the [User Guide](USER_GUIDE.md) for the exact installation and troubleshooting steps.

## Daily use

1. Save or download whatever the client sent.
2. Drag the original item onto **Drop Client Pictures Here** on the desktop.
3. Dad Image Tool converts the photos to JPEG.
4. The finished folder opens automatically.
5. Move the JPEGs wherever you want to keep them.

ZIP, DOCX, PDF, EML, and MSG files do not need to be unpacked manually first.

## Supported inputs

Dad Image Tool accepts:

- JPG and JPEG
- PNG
- HEIC and HEIF
- WebP
- TIFF
- BMP
- folders and nested folders
- ZIP files, including nested ZIPs and Deflate64 compression
- DOCX files containing embedded pictures, including DOCX files exported from Google Docs
- PDF files containing embedded raster pictures
- EML email files containing inline or attached pictures
- Outlook MSG email files containing inline or attached pictures

DOCX, PDF, EML, and MSG files are treated as photo containers. Dad Image Tool extracts usable embedded pictures and converts them to JPEG. It does not turn document pages or email text into screenshots.

Videos, older `.doc` files, and other unsupported items are kept in **Needs Attention** rather than deleted.

## Where files go

Dad Image Tool keeps its working data under the Windows Pictures folder:

```text
Pictures\Dad Image Tool\
├── Drop Client Pictures Here\
├── Finished\
├── Originals Archive\
├── Needs Attention\
└── job-history.jsonl
```

- **Finished** contains the converted JPEG batches.
- **Originals Archive** keeps source items that converted successfully.
- **Needs Attention** keeps anything that could not be completed safely.

Files dropped together stay together in one Finished batch, and folder/container structure is preserved where practical.

## Reliability and testing

The repository includes automated coverage for core processing and routing behavior, including image conversion, archive handling, nested containers, DOCX/PDF extraction, EML/MSG processing, duplicate-name safety, history, watcher stability, updater behavior, and Windows-safe paths.

Release builds are also smoke-tested after packaging and after installation. The installer upgrade test verifies that obsolete application runtime files are replaced while user data under `Pictures\Dad Image Tool` remains intact.

Real-Windows acceptance testing is documented in [`internal/docs/TESTING.md`](internal/docs/TESTING.md).

## Scope

Dad Image Tool is a converter, not a document-management or download service. It does not connect to email or cloud providers, and it does not decide how the finished JPEGs should be organized afterward. Save the source locally, drop it into the watched folder, then file the resulting JPEGs however you prefer.

## Experimental teaching tools

Two experimental teaching tools sit beside the normal image workflow:

- **Ask Pete (Experimental)** opens Pete's private Knowledge Core assistant in the web browser.
- **Learning Lab (Experimental)** opens a bundled interactive learning prototype built around public HoofRehab teaching material.

Neither feature uploads client pictures or changes the image-conversion workflow.

### Ask Pete

Select **Ask Pete (Experimental)** in the main window. It opens the hosted private browser assistant over HTTPS, so no local server or command prompt is required.

The browser assistant handles its own private token, conversation, answers, and Knowledge Core citations. Dad Image Tool does not receive or store any of them. An alternate private HTTPS address can be supplied through `DAD_ASSISTANT_URL` without changing the desktop interface.

### Learning Lab

Select **Learning Lab (Experimental)** beside Ask Pete. Dad Image Tool opens the Learning Lab in the default browser from files bundled with the installed application.

The Learning Lab provides **Learn** and **Ask** modes, topic browsing, original HoofRehab source links, suggested questions, related subjects, grounded answers, and source citations. The Lite prototype is based on public HoofRehab teaching material and does not include Pete's book or other private/paid teaching material.

The bundled browser interface is a snapshot of `Necropolite/Pete-Ramey-Learning-Lab`. Its substantive answers still come from the separately operated private Knowledge Core backend over HTTPS. Dad Image Tool does not receive or store the Learning Lab token, conversation, citations, or client pictures.

## More information

See the [Dad Image Tool User Guide](USER_GUIDE.md) for installation, updates, troubleshooting, and uninstall instructions.
