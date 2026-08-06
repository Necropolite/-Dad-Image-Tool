# Releasing Dad Image Tool

Dad Image Tool uses three-part versions: `major.minor.patch`.

The release tag must match `APP_VERSION` in `internal/src/version.py` with a leading `v`.

## Test build

Every push to `main` runs the test-installer workflow. It installs dependencies, compiles source, runs tests, builds `Dad Image Tool.exe`, builds `Dad-Image-Tool-Setup.exe`, and uploads a temporary acceptance-test artifact.

## Before release

1. Confirm the test-installer workflow succeeds for the exact commit.
2. Download `Dad-Image-Tool-Setup.exe` from the artifact.
3. Complete the user-facing checks in [TESTING.md](TESTING.md) without developer tools.
4. Complete image-format, failure, repair-installation, uninstall, startup, and update checks.
5. Confirm `APP_VERSION` is correct.
6. Tag the validated commit with the matching `vX.Y.Z` tag.

## Release assets

Normal user download:

- `Dad-Image-Tool-Setup.exe`
- `Dad-Image-Tool-Setup.exe.sha256`

In-app updater assets:

- `Dad-Image-Tool.exe`
- `Dad-Image-Tool.exe.sha256`

Dad should receive only the setup program or a direct link to it, not the repository ZIP or maintainer files.