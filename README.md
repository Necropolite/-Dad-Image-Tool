# Dad Image Tool

Dad Image Tool is a Windows utility that converts client photos into standard JPEG files.

It watches a desktop drop folder, handles the common ways photos arrive, keeps the original source files, and opens the finished JPEGs when conversion is complete.

An experimental **Ask Pete** button opens Pete's private Knowledge Core assistant in the web browser. Dad Image Tool does not upload client pictures or handle assistant credentials itself.

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

Select **Ask Pete (Experimental)** in the main window. It opens the same private browser assistant used outside Dad Image Tool. During local development, the address defaults to `http://127.0.0.1:8787/`; that local assistant must already be running on the same computer.

The browser assistant handles its own private token, conversation, answers, and Knowledge Core citations. Dad Image Tool does not receive or store any of them. A future private HTTPS address can be supplied through `DAD_ASSISTANT_URL` without changing the desktop interface.

## More information

See the [Dad Image Tool User Guide](USER_GUIDE.md) for installation, updates, troubleshooting, and uninstall instructions.
