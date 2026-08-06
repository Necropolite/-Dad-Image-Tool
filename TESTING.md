# Testing Dad Image Tool

Use this checklist before giving a new version to the end user.

## 1. Automated tests

Double-click `Run-Tests.bat`.

Do not publish the version unless the window says:

`All automated tests passed.`

## 2. Fresh installation

Test from a newly downloaded and extracted repository ZIP.

1. Run `Install.bat`.
2. Confirm the installer finishes without an error.
3. Confirm the desktop contains:
   - `Dad Image Tool`
   - `Drop Client Pictures Here`
4. Confirm these folders exist under `Pictures\Dad Image Tool`:
   - `Drop Client Pictures Here`
   - `Finished`
   - `Originals Archive`
   - `Needs Attention`
5. Restart Windows or sign out and back in.
6. Confirm Dad Image Tool starts automatically.

## 3. Basic picture test

1. Copy one PNG into `Drop Client Pictures Here`.
2. Wait for processing.
3. Confirm a dated folder opens under `Finished`.
4. Confirm it contains one readable `.jpg` file.
5. Confirm the original PNG moved into `Originals Archive`.
6. Open Job History and confirm the completed job is listed.

## 4. Mixed batch test

Place a folder containing several supported formats into the drop folder:

- JPG
- PNG
- WebP
- HEIC or HEIF
- TIFF
- BMP

Confirm every readable image becomes a JPEG and the original folder is archived.

## 5. ZIP test

1. Create a ZIP containing images inside several subfolders.
2. Put the ZIP into the drop folder.
3. Confirm the nested images are converted.
4. Confirm the original ZIP is archived.

## 6. Duplicate-name test

Process two images with the same filename in one job.

Confirm both outputs exist and neither overwrites the other.

## 7. Incomplete-download test

Download a large ZIP directly into the drop folder.

Confirm Dad Image Tool waits until the download has stopped changing before processing it.

## 8. Failure test

Put a damaged ZIP or unsupported file into the drop folder.

Confirm:

- The original moves to `Needs Attention`.
- No original is deleted.
- Job History shows that the job needs attention.
- The message uses plain language.

## 9. Queue test

Add another item while the first job is processing.

Confirm the second item remains in the drop folder and is processed afterward.

## 10. Reinstallation test

Run the newest `Install.bat` over the installed version.

Confirm existing client files, history, archived originals, and finished pictures remain intact.

## 11. Update test

After the repository becomes public and a newer release exists:

1. Install an older release.
2. Start Dad Image Tool.
3. Confirm it detects the newer release.
4. Accept the update.
5. Confirm the app restarts with the new version number.
6. Confirm all client folders and history remain intact.

## Release decision

A version is ready for the end user only when:

- Automated tests pass.
- Installation and startup pass.
- Basic, ZIP, duplicate, failure, queue, and reinstallation tests pass.
- No source files are lost.
- The update test passes before relying on automatic updates.
