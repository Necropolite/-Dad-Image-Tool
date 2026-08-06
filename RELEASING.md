# Releasing D.A.D. / Dad Image Tool

**D.A.D. — Dad's Automated Downloader**  
**Download • Archive • Deliver**

This document is for the maintainer. The end user does not need it.

D.A.D. is the product identity. The release artifact and installed application remain named Dad Image Tool so existing updater, shortcut, and path contracts remain stable.

## Versioning

D.A.D. uses three-part versions:

`major.minor.patch`

Increase the patch number for compatible fixes, the minor number for meaningful new behavior, and the major number for an incompatible redesign.

The release tag must exactly match `APP_VERSION` with a leading `v`.

```text
APP_VERSION = "0.2.2"
tag = v0.2.2
```

## Branding and release names

Use a human-readable GitHub Release title in this form:

`D.A.D. v0.2.2 — Dad Image Tool`

Keep these technical names unchanged:

- `Dad-Image-Tool.exe`
- `Dad-Image-Tool.exe.sha256`
- `Dad Image Tool.exe` after installation

Windows file properties are generated from `version.py` and should show:

- product identity: `D.A.D. — Dad's Automated Downloader`
- file description: `Dad Image Tool — D.A.D.`
- comments: `Download • Archive • Deliver`
- original filename: `Dad Image Tool.exe`

## Before a release

1. Review every changed file.
2. Double-click `Run-Tests.bat` on Windows.
3. Complete the applicable manual checks in [TESTING.md](TESTING.md).
4. Confirm the D.A.D. branding, expansion, tagline, executable name, shortcuts, and Windows file properties.
5. Update `APP_VERSION` in `version.py`.
6. Commit and push the completed changes to `main`.
7. Confirm the **D.A.D. Tests** workflow succeeds for that exact commit, including the PyInstaller smoke build.
8. Create and push the matching version tag.

Do not tag a commit whose tests or manual acceptance checks are unknown.

The test workflow can also be started manually from GitHub Actions when a push-triggered run is unavailable. A workflow entry is not proof of success. Confirm every step completed.

## Automated release build

A tag matching `v*` starts `.github/workflows/release.yml`. The Windows workflow:

1. Verifies that the tag matches `APP_VERSION`.
2. Installs dependencies.
3. Compiles the Python files.
4. Runs Ruff.
5. Runs the automated test suite with the coverage gate.
6. Generates branded Windows version metadata.
7. Builds `Dad-Image-Tool.exe`.
8. Creates `Dad-Image-Tool.exe.sha256`.
9. Publishes both files under a D.A.D.-branded GitHub Release title.

## Release verification

After the workflow succeeds:

1. Open the release.
2. Confirm the title identifies D.A.D. and Dad Image Tool without renaming the assets.
3. Confirm both required files are present.
4. Download the executable and checksum on a separate Windows test computer.
5. Confirm the published SHA-256 matches the executable.
6. Open Windows Properties and confirm the product name, file description, version, tagline, and original filename are correct.
7. Test a fresh installation or controlled executable replacement.
8. Process at least one ordinary image, one nested ZIP, one duplicate-name batch, and one failed item.
9. Confirm the source folders and job history remain intact.
10. Record the exact dependency versions used by the successful Windows build.

## Automatic updates

The installed application checks the public GitHub Releases API. Automatic updates cannot work while this repository is private.

Before the first external installation, either:

- Make this repository public.
- Move compiled releases to a separate public repository and update `GITHUB_REPOSITORY`.

Do not place a personal access token in the application.

Test updating from the previous released version to the new version before relying on automatic delivery. Confirm that the new version writes its startup marker, the old executable backup is removed only after startup confirmation, and `Pictures\Dad Image Tool` remains unchanged.

## First installation

The current first-install method is the repository ZIP plus `Install.bat`. This requires Python during the build and is not yet a commercial-style installer.

A future setup executable should install the already-built application without requiring the end user to download source code or Python. It must preserve the D.A.D. identity, the Dad Image Tool executable and shortcut names, the watched-folder locations, and the update behavior.
