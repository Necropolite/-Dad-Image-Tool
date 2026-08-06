# Testing D.A.D. — Dad Image Tool

Use this checklist before giving a version to the end user. Record the tested commit, Windows version, application version, and results.

## Test rule: behave like the end user

The user-facing test must begin with **DAD-Setup.exe**.

During that test:

- Do not open PowerShell, Command Prompt, Git, Python, or the source repository.
- Do not run `Install.bat`, `Run-Tests.bat`, or any developer script.
- Do not manually create application folders or shortcuts.
- Judge every message as if the tester has no technical background.
- Record any step that requires explanation, guessing, or technical knowledge as a usability problem.

Developer automation may be checked separately in GitHub Actions, but it does not replace this user-facing test.

## 1. Fresh user installation

Use a Windows account that does not already have Dad Image Tool installed, or uninstall the previous test build first while preserving the Pictures data folder.

1. Double-click **DAD-Setup.exe**.
2. Record every Windows or setup message that appears.
3. Confirm setup does not ask the user to install Python or use GitHub tools.
4. Confirm setup does not require PowerShell or Command Prompt.
5. Confirm installation can finish without an administrator password.
6. Leave **Open D.A.D. now** checked and choose **Finish**.
7. Confirm the application opens.
8. Confirm Windows Settings lists **Dad Image Tool** under installed apps.

## 2. Branding and shortcuts

Confirm:

- The main window shows **D.A.D.**.
- It shows **Dad's Automated Dropzone**.
- It shows **Drop • Archive • Deliver**.
- The version is **0.3.0**.
- **About D.A.D.** shows the same identity and version.
- The desktop contains **Dad Image Tool**.
- The desktop contains **Drop Client Pictures Here**.
- The executable remains named `Dad Image Tool.exe`.
- The executable's **Properties > Details** contains the D.A.D. identity and correct version.

Double-click **Dad Image Tool** while it is already open. Confirm a second processing window does not remain open.

## 3. First ordinary conversion

Use one ordinary JPG or PNG that is safe to test.

1. Drag or save it into **Drop Client Pictures Here**.
2. Do not touch the application while it waits and processes.
3. Confirm a finished folder opens automatically.
4. Confirm the finished JPEG opens and looks correct.
5. Confirm the original moved to **Originals Archive**.
6. Confirm **View History** records the job.

The first successful test should require no explanation beyond “put the file in this folder.”

## 4. Forwarded-client ZIP tests

Test the two forwarded x-ray ZIP files individually before combining them with failure cases.

Confirm:

- Every supported image is found inside nested folders.
- A readable JPEG is created for each supported picture.
- The original ZIP moves to **Originals Archive**.
- No unrelated file is converted into a JPEG.
- Job History reports the correct source and count.

Also test a ZIP containing another ZIP and a folder containing a ZIP.

## 5. Supported formats

Test JPG, JPEG, PNG, WebP, TIFF, BMP, HEIC, and HEIF from the installed application.

For each format, confirm:

- A readable JPEG is created.
- Phone-picture orientation is correct.
- The original is archived.
- The output does not overwrite an existing file.

HEIC and HEIF must be tested from the installed executable, not from source Python.

## 6. Unsupported and failed items

Test a video, Word document, corrupt picture, corrupt ZIP, password-protected ZIP, path-traversal ZIP, and another unsupported file.

Confirm:

- The original is never deleted.
- The item moves to **Needs Attention**.
- No empty Finished folder remains after total failure.
- No partial JPEG remains after conversion failure.
- Job History shows a plain-English explanation.
- The warning tells a nontechnical user what to do next.

## 7. Independent routing

Put one valid picture or ZIP and one unsupported video into the drop folder together.

Confirm:

- The valid source succeeds and is archived.
- The unsupported source goes to **Needs Attention**.
- The failed item does not cause the valid item to fail.
- Both appear separately in Job History.

## 8. Duplicate names

Process multiple pictures with the same filename in one source. Confirm numbered JPEG names are created and no file is overwritten.

Process two top-level items with the same name at different times. Confirm both originals remain with unique names.

## 9. Incomplete downloads and queueing

Download a large image or ZIP directly into the drop folder.

Confirm processing does not begin while the file is changing or while a partial-download file exists. Add another item while the first job is processing and confirm it waits and processes afterward without restarting the app.

## 10. Startup and repair installation

Restart Windows or sign out and back in. Confirm Dad Image Tool starts automatically.

Then run **DAD-Setup.exe** again over the installed version. Confirm:

- Client data and history remain unchanged.
- Missing shortcuts are repaired.
- The current executable is replaced cleanly.
- The application opens normally afterward.

## 11. Uninstall safety

Use **Windows Settings > Apps > Dad Image Tool > Uninstall**.

Confirm:

- The executable and shortcuts are removed.
- The startup shortcut is removed.
- The Pictures data folder, finished files, archived originals, Needs Attention files, and job history are not deleted.

Reinstall with **DAD-Setup.exe** and confirm the preserved data is still available.

## 12. Update behavior

After versioned releases exist:

1. Install the previous released setup.
2. Start Dad Image Tool and check for updates.
3. Confirm the newer version is shown.
4. Accept the update.
5. Confirm a deliberately incorrect checksum is rejected in a controlled test release.
6. Confirm a valid update closes the old version and opens the new version.
7. Confirm all user folders and history remain unchanged.
8. Confirm the previous executable is restored if replacement is forced to fail.

## Release decision

A version is ready only when:

- GitHub Actions passes for the exact commit and release tag.
- A tester installs it using only **DAD-Setup.exe**.
- Installation, branding, first use, startup, formats, nested ZIPs, duplicate names, failure routing, queueing, repair installation, uninstall safety, and update behavior pass.
- No source or user data is lost.
- Any confusing step is documented and fixed or accepted as a stated release risk.
- Any skipped test is documented rather than treated as passed.
