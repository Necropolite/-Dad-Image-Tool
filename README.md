# Dad Image Tool

Dad Image Tool is a Windows utility that converts client photos into standard JPEG files.

It watches a desktop drop folder, handles the common ways photos arrive, keeps the original source files, and opens the finished JPEGs when conversion is complete.

An experimental **Ask Pete** window can connect to Pete's separately operated private Knowledge Core assistant for text questions. It does not upload client pictures or save conversations.

## Download

[**Download Dad Image Tool for Windows**](https://github.com/Necropolite/-Dad-Image-Tool/releases/latest/download/Dad-Image-Tool-Setup.exe)

The download is `Dad-Image-Tool-Setup.exe`. Run it normally to install or repair Dad Image Tool.

Windows or Microsoft Edge may warn that the installer is not commonly downloaded. See the [User Guide](USER_GUIDE.md) for the exact installation and troubleshooting steps.

## Daily use

1. Save or download whatever the client sent.
2. Drag the original item onto **Drop Client Pictures Here** on the desktop.
3. Dad Image Tool converts the photos to JPEG.
4. The finished folder opens automatically.
5. Move the JPEGs wherever you want to keep them.

ZIP, DOCX, PDF, EML, and Outlook MSG files do not need to be unpacked manually first.

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

## Scope

Dad Image Tool is a converter, not a document-management or download service. It does not connect to email or cloud providers, and it does not decide how the finished JPEGs should be organized afterward. Save the source locally, drop it into the watched folder, then file the resulting JPEGs however you prefer.

## Experimental Ask Pete feature

Select **Ask Pete (Experimental)** in the main window. During local development, the assistant address defaults to `http://127.0.0.1:8787`; enter the private access token supplied by the assistant administrator. A remote address must use HTTPS.

Dad Image Tool keeps the token only in memory for the open Ask Pete window. It does not write the token, questions, or answers to disk. Answers display the Knowledge Core citations returned by the private assistant. This feature asks text questions only: client images are not sent to the assistant.

## More information

See the [Dad Image Tool User Guide](USER_GUIDE.md) for installation, updates, troubleshooting, and uninstall instructions.
