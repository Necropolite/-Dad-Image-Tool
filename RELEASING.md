# Releasing D.A.D. — Dad Image Tool

This document is for the maintainer. The end user does not need it.

## Versioning

Dad Image Tool uses three-part versions:

`major.minor.patch`

Increase the patch number for compatible fixes, the minor number for meaningful new behavior, and the major number for an incompatible redesign.

The release tag must exactly match `APP_VERSION` with a leading `v`.

```text
APP_VERSION = "0.3.0"
tag = v0.3.0
```

The official brand strings and version live in `version.py`. The build scripts generate matching Windows executable and setup metadata.

The release must identify D.A.D. as **Dad's Automated Dropzone** with the tagline **Drop • Archive • Deliver**. It must not describe the application as downloading files from email or cloud services.

## Test build on main

Every push to `main` runs `.github/workflows/build-test-installer.yml`. It:

1. installs Python dependencies.
2. compiles the source.
3. runs automated tests.
4. builds `Dad Image Tool.exe`.
5. compiles `DAD-Setup.exe`.
6. uploads a temporary `DAD-Test-Installer` artifact.

The artifact is for acceptance testing. It is not a public versioned release.

## Before a release

1. Review every changed file.
2. Confirm the test-installer workflow succeeds for the exact commit.
3. Download the generated **DAD-Setup.exe** test artifact.
4. Complete the user-facing checks in [TESTING.md](TESTING.md) without using developer tools.
5. Complete the format, failure, repair-installation, uninstall, and update checks that apply.
6. Confirm `APP_VERSION` is correct in `version.py`.
7. Commit and push the completed changes to `main`.
8. Create and push the matching version tag.

Do not tag a commit whose automated or manual acceptance results are unknown.

## Automated release build

A tag matching `v*` starts `.github/workflows/release.yml` on a Windows runner. The workflow:

1. verifies that the tag matches `APP_VERSION`.
2. installs dependencies.
3. compiles the Python source.
4. runs the automated test suite.
5. generates Windows executable metadata.
6. builds the raw `Dad-Image-Tool.exe` update asset.
7. builds the user-facing `DAD-Setup.exe` installer.
8. creates SHA-256 files for both.
9. publishes all four files in a GitHub Release.

## Release assets

The normal end-user download is:

- `DAD-Setup.exe`

The application updater uses:

- `Dad-Image-Tool.exe`
- `Dad-Image-Tool.exe.sha256`

The setup checksum is:

- `DAD-Setup.exe.sha256`

Dad should receive only the setup program or a direct link to it. He should not receive the repository ZIP, source files, batch files, or build instructions.

## Release verification

After the workflow succeeds:

1. Confirm all four required assets exist.
2. Verify both published SHA-256 files.
3. Download `DAD-Setup.exe` on a separate Windows test account or computer.
4. Test from the setup program only.
5. Confirm the executable's **Properties > Details** shows the correct identity and version.
6. Process at least one ordinary image, one forwarded-client ZIP, one duplicate-name batch, and one failed item.
7. Confirm startup, repair installation, uninstall safety, and preserved history.
8. Test updating from the previous released version.

## Automatic updates

The installed application checks the public GitHub Releases API for `Dad-Image-Tool.exe` and its checksum. The repository is public, so anonymous update checks can work after a valid versioned release exists.

Never place a personal access token in the application.

Test updating from the previous released version before relying on automatic delivery. Confirm the new version restarts and that the Windows Pictures data folder remains unchanged.

## Installation architecture

`DAD-Setup.exe` is a per-user Windows installer. It installs the prebuilt application under the user's Local AppData folder, creates desktop and startup shortcuts, and registers a normal Windows uninstaller. It does not require the end user to install Python or work with the source repository.

`Install.bat` and `Run-Tests.bat` are maintainer tools only. They are not part of the end-user installation path.
