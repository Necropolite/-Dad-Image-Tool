# Releasing D.A.D. — Dad Image Tool

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

The official brand strings and version live in `version.py`. `build_version_info.py` generates the Windows executable Properties metadata during local and release builds.

## Before a release

1. Review every changed file.
2. Double-click `Run-Tests.bat` on Windows.
3. Complete the applicable manual checks in [TESTING.md](TESTING.md).
4. Update `APP_VERSION` in `version.py`.
5. Commit and push the completed changes to `main`.
6. Confirm the **Tests** workflow succeeds for that exact commit.
7. Create and push the matching version tag.

Do not tag a commit whose tests or manual acceptance checks are unknown.

## Automated release build

A tag matching `v*` starts `.github/workflows/release.yml` on a Windows runner. The workflow:

1. verifies that the tag matches `APP_VERSION`.
2. installs dependencies.
3. compiles the Python files.
4. runs the automated test suite.
5. generates Windows version metadata.
6. builds `Dad-Image-Tool.exe` without renaming the installed application.
7. creates `Dad-Image-Tool.exe.sha256`.
8. publishes both files in a GitHub Release.

A workflow entry is not proof of success. Open the run and confirm every step completed before using the release.

## Release verification

After the workflow succeeds:

1. Open the release.
2. Confirm both required files are present.
3. Download the executable and checksum on a separate Windows test computer.
4. Confirm the published SHA-256 matches the executable.
5. Open the executable's **Properties > Details** and confirm the D.A.D. description, Dad Image Tool product name, tagline, and version.
6. Test a fresh installation or controlled executable replacement.
7. Process at least one ordinary image, one nested ZIP, one duplicate-name batch, and one failed item.
8. Confirm the source folders and job history remain intact.

## Automatic updates

The installed application checks the public GitHub Releases API. Automatic updates cannot work while this repository is private.

Before the first external installation, either:

- make this repository public, or
- move compiled releases to a separate public repository and update `GITHUB_REPOSITORY`.

Do not place a personal access token in the application.

Test updating from the previous released version to the new version before relying on automatic delivery. Confirm the new version restarts and that `Pictures\Dad Image Tool` is unchanged.

## First installation

The current first-install method is the repository ZIP plus `Install.bat`. This requires Python during the build and is not yet a commercial-style installer.

A future setup executable should install the already-built application without requiring the end user to download source code or Python. It must preserve the same watched-folder locations, application name, shortcuts, and update behavior.
