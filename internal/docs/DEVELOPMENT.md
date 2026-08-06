# Dad Image Tool Development Notes

## Product contract

Dad Image Tool is a Windows watched-folder image converter for a nontechnical user. The watched folder is the only input interface. It does not directly download from Outlook or cloud providers.

The user-facing identity leads with **Dad Image Tool**. See [BRANDING.md](BRANDING.md) for the secondary D.A.D. nickname rules.

## Repository layout

- `README.md` and `USER_GUIDE.md`: user-facing files kept at repository root.
- `internal/src/`: application and build Python source.
- `internal/scripts/`: maintainer convenience scripts.
- `internal/docs/`: maintainer documentation.
- `internal/requirements.txt`: Python build dependencies.
- `tests/`: automated tests.
- `installer/`: Inno Setup source.
- `.github/workflows/`: CI, test-installer, and release workflows.

## Runtime folders

```text
Pictures/Dad Image Tool/
├── Drop Client Pictures Here/
├── Finished/
├── Originals Archive/
├── Needs Attention/
└── job-history.jsonl
```

Each top-level incoming item is one job and jobs run sequentially.

## Processing rules

1. Ignore known partial-download suffixes.
2. Require repeated unchanged scans before processing.
3. Process top-level sources independently.
4. Recursively inspect folders and ZIP files.
5. Convert supported images into a unique dated output folder.
6. Move a fully successful source to `Originals Archive`.
7. Move a failed or partly failed source to `Needs Attention`.
8. Record history after routing.
9. Open successful output automatically.

Supported images are JPG, JPEG, PNG, HEIC, HEIF, TIFF, BMP, and WebP. Existing output files are never overwritten.

## Safety rules

- Never delete source items during processing.
- Never overwrite finished or archived files.
- Never let one source failure affect another source.
- Never process changing or partial downloads.
- Never trust ZIP member paths.
- Never update or uninstall user-data folders.
- Keep the end-user interface small and plain.

## Installation

The supported user path is `Dad-Image-Tool-Setup.exe`, a per-user installer that should not require an administrator password. Developer batch files are not part of the end-user workflow.