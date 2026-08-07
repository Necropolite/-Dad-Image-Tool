# Dad Image Tool Acceptance Testing

## Rule: test like the end user

Begin with **Dad-Image-Tool-Setup.exe**. During the user-facing test, do not use PowerShell, Command Prompt, Git, Python, source files, or maintainer scripts. Record anything that requires technical knowledge as a usability problem.

## 1. Fresh installation

1. Double-click the setup file.
2. Record every Windows or setup message.
3. Confirm no developer software is requested.
4. Confirm setup can finish without an administrator password.
5. Leave **Open Dad Image Tool now** checked and finish setup.
6. Confirm the application opens.
7. Confirm Windows Settings lists Dad Image Tool as an installed app.

## 2. Identity and shortcuts

Confirm:

- The main window leads with **Dad Image Tool**.
- The product description is **Automatic image converter**.
- The version is correct.
- D.A.D. appears only as secondary About information, not the main interface identity.
- Desktop shortcuts exist for **Dad Image Tool** and **Drop Client Pictures Here**.
- Starting Dad Image Tool again does not leave a second processing window open.

## 3. Ordinary conversion

Test one disposable JPG or PNG first. Put it into the drop folder and do nothing else. Confirm the finished folder opens, the JPEG is readable, the original moves to `Originals Archive`, and history records the job.

## 4. Real client samples

After the ordinary image succeeds, test real forwarded consultant samples one at a time. Drop the original ZIP, DOCX, or PDF itself instead of manually extracting it. Confirm pictures are found and converted without changing the original source file.

## 5. Format coverage

Test JPG, JPEG, PNG, WebP, TIFF, BMP, HEIC, and HEIF from the packaged application. Confirm orientation and readable output.

## 6. ZIP and folder coverage

Test nested folders, a ZIP with folders, a ZIP inside a ZIP, a folder containing a ZIP, Deflate64 ZIP compression, and a ZIP containing unrelated documents beside valid pictures.

## 7. DOCX and PDF coverage

Test:

- A DOCX containing several pictures in a known order.
- A DOCX exported from Google Docs.
- A PDF containing several embedded raster pictures.
- A DOCX inside a ZIP.
- A PDF inside a folder or ZIP.
- A DOCX or PDF with no usable embedded pictures.
- A damaged or password-protected document.

Confirm the original document is archived only on full success, extracted pictures remain grouped under the document name, DOCX picture order is preserved, PDF processing extracts embedded pictures rather than screenshots of whole pages, and failures retain the original in `Needs Attention`.

## 8. Failure handling

Test an unsupported video, corrupt picture, corrupt ZIP, password-protected ZIP, damaged DOCX, and damaged/password-protected PDF. Confirm originals are retained in `Needs Attention`, no misleading success is reported, and the message is understandable.

## 9. Queue and duplicate safety

Add more items while a large job is processing. Test duplicate filenames. Confirm jobs wait safely and existing files are never overwritten.

## 10. Restart and startup

Restart or sign out of Windows. Confirm Dad Image Tool starts automatically and continues watching the same folder.

## 11. Repair installation and uninstall

Run the setup file over the installed version and confirm shortcuts are repaired while all Pictures data and history remain unchanged. Then uninstall through Windows Settings and confirm program files/shortcuts are removed while the Pictures data remains.

## 12. Update behavior

Once two valid public releases exist, test updating from the prior release. Confirm checksum verification, restart, and preservation of all user data.

A version is ready only after both automated checks and the applicable real Windows tests pass.