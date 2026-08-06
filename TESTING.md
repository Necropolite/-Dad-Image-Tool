# Testing D.A.D. / Dad Image Tool

**Dad's Automated Downloader**  
**Download • Archive • Deliver**

Use this checklist before giving a version to the end user. Record the tested commit, Windows version, application version, and exact dependency versions with the results.

## 1. Automated tests

Double-click `Run-Tests.bat` on Windows.

Confirm the window reports:

`All D.A.D. automated checks passed.`

The local runner must also complete Ruff, pass the branding and Windows metadata tests, and report core-module coverage at or above the floor configured in `pyproject.toml`. A high test count alone is not sufficient evidence.

Also confirm the GitHub **D.A.D. Tests** workflow succeeds for the exact release commit, including the PyInstaller build smoke test. Download its review-evidence artifact and retain the dependency snapshot, coverage XML, generated fixtures, and packaged executable with the test record. The workflow can be started manually from GitHub Actions. Do not assume a workflow ran merely because the workflow file exists.

## 2. Branding and fresh installation

Test from a newly downloaded and extracted repository ZIP.

1. Run `Install.bat`.
2. Confirm the installer identifies D.A.D., expands it as **Dad's Automated Downloader**, and displays **Download • Archive • Deliver**.
3. Confirm syntax checks and automated tests run before installation.
4. Confirm the installer finishes without an error.
5. Confirm the desktop shortcuts remain exactly **Dad Image Tool** and **Drop Client Pictures Here**.
6. Confirm the installed executable remains exactly `Dad Image Tool.exe`.
7. Open Windows Properties for the executable and confirm:
   - Product name identifies `D.A.D. — Dad's Automated Downloader`.
   - File description identifies `Dad Image Tool — D.A.D.`.
   - Comments show `Download • Archive • Deliver`.
   - Original filename remains `Dad Image Tool.exe`.
   - File and product versions match `APP_VERSION`.
8. Start Dad Image Tool and confirm the main window shows D.A.D., the full expansion, the tagline, and the familiar Dad Image Tool name without crowding or clipping.
9. Confirm the four application folders still exist under the Windows Pictures known folder using the unchanged Dad Image Tool path.
10. Restart Windows or sign out and back in.
11. Confirm Dad Image Tool starts automatically.
12. Start the shortcut again and confirm a second processing window does not remain open.
13. Remove one empty runtime folder while the app is open and confirm it is recreated.

## 3. Ordinary image conversion

Test JPG, JPEG, PNG, WebP, TIFF, BMP, HEIC, and HEIF files.

For each supported type, confirm:

- A readable JPEG is created.
- Phone-picture orientation is correct.
- The original moves to `Originals Archive`.
- The finished folder opens.
- D.A.D. Job History records the source and JPEG count.

HEIC and HEIF must be tested from the packaged executable, not only from source Python.

Also test an unusually large image in a controlled environment and confirm it is rejected with a plain-language safety message rather than exhausting memory.

## 4. Folder and ZIP processing

Test:

- Images in nested folders.
- A ZIP containing nested folders.
- A ZIP containing another ZIP.
- A folder containing a ZIP.
- A ZIP with an unrelated document beside valid images.
- A ZIP containing paths that differ only by letter case.
- A ZIP containing a Windows-reserved name, an alternate-data-stream colon, or a trailing dot.
- A ZIP containing a file and a child path that treats that file as a folder.

Confirm valid inputs are processed and unsafe or conflicting ZIP structures move to `Needs Attention` without overwriting extracted files.

## 5. Duplicate names

Process multiple images with the same filename in one source. Confirm numbered JPEG names are created and no file is overwritten.

Process two top-level source items with the same name at different times. Confirm both originals remain in the archive or attention folder with unique names.

## 6. Incomplete downloads

Download a large image and a large ZIP directly into the watched folder.

Confirm processing does not begin while the file is changing, while it is less than ten seconds old, or while a partial-download file exists inside a downloaded folder. Pause or stall a download and confirm it is not processed immediately. Confirm processing starts only after the completed item remains unchanged through the full stability wait.

## 7. Links and independent routing

Place one valid source and one corrupt source into the watched folder together. Confirm:

- The valid source moves to `Originals Archive`.
- The corrupt source moves to `Needs Attention`.
- The valid source is not treated as failed because of the corrupt source.
- Both jobs appear separately in history.

Also place a Windows shortcut, symbolic link, or junction into the watched folder in a controlled test. Confirm Dad Image Tool does not follow it into another location and routes it for attention.

## 8. Failure safety

Test a corrupt picture, corrupt ZIP, password-protected ZIP, path-traversal ZIP, and unsupported file.

Confirm:

- The original is never deleted.
- Failed or partially failed sources move to `Needs Attention`.
- No empty Finished folder remains after a total failure.
- No partial JPEG remains after a conversion failure.
- Job History shows a plain-English error.
- An unexpected orchestration failure does not create a rapid repeated retry loop for the unchanged source.

## 9. Active-job protection

While a large job is running:

1. Try to close the window. Confirm it finishes the job and then closes without opening extra folders or dialogs.
2. Try a manual update check. Confirm the app tells you to wait.
3. Start `Install.bat` or `Uninstall.bat` in a controlled test. Confirm it asks the app to close safely and does not force-stop an active job.

## 10. Queue behavior

Add more items while a large job is processing. Confirm the new items remain in the watched folder and are processed afterward without restarting the app.

## 11. Reinstallation

Run the newest `Install.bat` over an installed version.

Confirm client files, Finished folders, Originals Archive, Needs Attention, and `job-history.jsonl` remain unchanged. Confirm desktop and startup shortcuts are repaired if they were removed. Confirm no duplicate D.A.D.-named shortcut or folder is created. Confirm the installer restores the prior executable if the replacement cannot initialize in a controlled test.

## 12. Update and release behavior

After public releases exist:

1. Confirm the GitHub Release title identifies D.A.D. while the downloadable assets remain `Dad-Image-Tool.exe` and `Dad-Image-Tool.exe.sha256`.
2. Install the previous released version.
3. Start Dad Image Tool and check for updates.
4. Confirm the newer D.A.D. version and version number are shown.
5. Accept the update.
6. Confirm the download is rejected if its checksum is deliberately wrong in a controlled test release.
7. Confirm a valid update closes the old version and opens the new version.
8. Confirm the new version creates the startup confirmation marker.
9. Confirm all user folders and history remain unchanged.
10. Confirm the previous executable is restored if replacement or startup confirmation is forced to fail in a controlled test.

## Release decision

A version is ready only when:

- Local automated tests pass on Windows.
- GitHub Actions succeeds for the exact commit and release tag.
- D.A.D. branding is correct and technical names remain unchanged.
- Installation, startup, formats, nested ZIPs, duplicate names, ZIP safety, failure routing, queueing, reinstallation, and update checks pass.
- No source or user data is lost.
- Any skipped test is documented as a release risk rather than treated as passed.
