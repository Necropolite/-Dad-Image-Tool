# Releasing Dad Image Tool

This document is for the maintainer. The end user does not need it.

## Versioning

Dad Image Tool uses three-part versions:

`major.minor.patch`

Increase the patch number for compatible fixes, the minor number for meaningful new behavior, and the major number for an incompatible redesign.

The release tag must exactly match `APP_VERSION` with a leading `v`.

```text
APP_VERSION = "0.2.2"
tag = v0.2.2
```

## Before a release

1. Review every changed file.
2. Double-click `Run-Tests.bat` on Windows.
3. Complete the applicable manual checks in [TESTING.md](TESTING.md).
4. Update `APP_VERSION` in `version.py`.
5. Commit and push the completed changes to `main`.
6. Confirm the **Tests** workflow succeeds for that exact commit, including the PyInstaller smoke build.
7. Create and push the matching version tag.

Do not tag a commit whose tests or manual acceptance checks are unknown.

The **Tests** workflow can also be started manually from GitHub Actions when a push-triggered run is unavailable. A workflow entry is not proof of success. Confirm every step completed.

## Automated release build

A tag matching `v*` starts `.github/workflows/release.yml` on a Windows runner. The workflow:

1. Verifies that the tag matches `APP_VERSION`.
2. Installs dependencies.
3. Compiles the Python files.
4. Runs the automated test suite.
5. Builds `Dad-Image-Tool.exe`.
6. Creates `Dad-Image-Tool.exe.sha256`.
7. Publishes both files in a GitHub Release.

## Release verification

After the workflow succeeds:

1. Open the release.
2. Confirm both required files are present.
3. Download the executable and checksum on a separate Windows test computer.
4. Confirm the published SHA-256 matches the executable.
5. Test a fresh installation or controlled executable replacement.
6. Process at least one ordinary image, one nested ZIP, one duplicate-name batch, and one failed item.
7. Confirm the source folders and job history remain intact.
8. Record the exact dependency versions used by the successful Windows build.

## Automatic updates

The installed application checks the public GitHub Releases API. Automatic updates cannot work while this repository is private.

Before the first external installation, either:

- Make this repository public.
- Move compiled releases to a separate public repository and update `GITHUB_REPOSITORY`.

Do not place a personal access token in the application.

Test updating from the previous released version to the new version before relying on automatic delivery. Confirm that the new version writes its startup marker, the old executable backup is removed only after startup confirmation, and `Pictures\Dad Image Tool` remains unchanged.

## First installation

The current first-install method is the repository ZIP plus `Install.bat`. This requires Python during the build and is not yet a commercial-style installer.

A future setup executable should install the already-built application without requiring the end user to download source code or Python. It must preserve the same watched-folder locations and update behavior.
