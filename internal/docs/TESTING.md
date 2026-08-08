# Dad Image Tool Acceptance Testing

Use this checklist for the parts of Dad Image Tool that automated tests cannot fully prove on a real Windows computer.

## Test as the user

Start with `Dad-Image-Tool-Setup.exe`. For pre-release acceptance, use the exact installer artifact produced by the validated commit. After publication, also verify the normal GitHub download link serves the released installer.

During the user-facing test, do not use PowerShell, Command Prompt, Git, Python, source files, or maintainer scripts to make the normal workflow succeed. Anything that requires those tools is a product or installation problem.

## 1. Fresh computer

Prefer a Windows PC that has not previously had Dad Image Tool installed.

Confirm:

- `Dad-Image-Tool-Setup.exe` downloads or transfers intact;
- for a published release, the normal GitHub download link returns the expected installer;
- any Edge/SmartScreen warnings can be handled using the User Guide;
- setup does not request developer software;
- setup can complete without an administrator password;
- **Open Dad Image Tool now** launches the application;
- Windows Settings lists Dad Image Tool as installed;
- desktop shortcuts exist for **Dad Image Tool** and **Drop Client Pictures Here**;
- the horse mark appears as the Dad Image Tool setup/application/shortcut icon instead of the generic executable icon;
- the application starts automatically after a Windows sign-in/restart.

## 2. Main window

Confirm the main window remains plain and functional:

- Dad Image Tool is the clear title;
- the short description is **Automatic image converter**;
- the instruction mentions pictures, folders, ZIP, DOCX, PDF, and EML inputs;
- the drop-folder path is visible;
- status and progress are visible;
- controls are limited to **Open Drop Folder**, **Open Finished Pictures**, **View History**, and **Check for Updates**;
- there is no About button or decorative horse image inside the window.

## 3. Basic conversion

Drop one ordinary JPG or PNG into the watched folder.

Confirm:

- processing begins without a Start button;
- a readable JPEG is created;
- the Finished batch opens automatically;
- the original moves to `Originals Archive`;
- job history records the result.

## 4. Real consultant samples

Test representative real files one at a time, including the original ZIP, DOCX, PDF, and EML files rather than manually unpacking them first.

For the EML case, use a real saved message whose photos display inline in the email body rather than as normal attachments. Confirm all expected inline photos are extracted as usable JPEGs.

Confirm the resulting JPEGs are usable for the actual downstream workflow and the original source files remain unchanged in `Originals Archive` after success.

## 5. Image formats

Test JPG/JPEG, PNG, HEIC/HEIF, WebP, TIFF, and BMP from the installed application. Confirm readable JPEG output and correct orientation.

## 6. Containers and structure

Test:

- nested folders;
- a ZIP containing folders;
- a ZIP inside a ZIP;
- a folder containing a ZIP;
- a Deflate64 ZIP;
- unrelated unsupported files beside valid pictures;
- a DOCX containing several pictures in known order;
- a DOCX exported from Google Docs;
- a PDF containing several embedded raster pictures;
- an EML containing several inline MIME images;
- an EML containing both inline images and normal image attachments;
- DOCX/PDF/EML files nested inside a folder or ZIP.

Confirm the converted pictures stay grouped sensibly under their source folder/container names, DOCX picture order is preserved where expected, and EML pictures follow MIME message order.

## 7. Failure handling

Test a corrupt picture, corrupt ZIP, password-protected ZIP, damaged DOCX, a document with no usable embedded pictures, damaged/password-protected PDF, an EML with no supported pictures, and an unsupported video.

Confirm:

- the source is retained in `Needs Attention`;
- no misleading success is reported;
- unrelated items still process normally;
- no partial or empty Finished result is presented as successful.

## 8. Batch and duplicate safety

Drop multiple files together and confirm they share one Finished batch. Add another item while a larger job is processing and confirm it waits safely.

Test duplicate filenames and confirm existing Finished or archived files are never overwritten.

## 9. Update path

From a valid older release, use **Check for Updates** and install the newer release without manually deleting application files first.

Confirm:

- the update downloads and installs through the application;
- Dad Image Tool closes and reopens normally;
- the displayed version changes;
- existing Finished, Originals Archive, Needs Attention, drop-folder contents, and history remain intact;
- conversion still works after the update.

CI separately verifies cleanup of obsolete runtime files inside the application directory.

## 10. Repair and uninstall

Run the current setup program over the installed version and confirm the application/shortcuts are repaired without changing Pictures data.

Then uninstall through Windows Settings and confirm the application and shortcuts are removed while `Pictures\Dad Image Tool` remains.

## Release readiness

A release is ready for the end user when the applicable automated checks pass and this real-Windows workflow can be completed without developer intervention.
