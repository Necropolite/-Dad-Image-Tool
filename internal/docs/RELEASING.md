# Releasing Dad Image Tool

Dad Image Tool uses `major.minor.patch` versions. `APP_VERSION` in `internal/src/version.py` is the version source of truth.

The published release tag is `vX.Y.Z` and must match `APP_VERSION`.

## Validation build gate

`.github/workflows/build-test-installer.yml` runs for pushes to `main`, pull requests targeting `main`, and manual workflow dispatches.

A successful validation workflow must:

1. install dependencies;
2. compile the Python source;
3. run the automated test suite;
4. generate `Dad-Image-Tool.ico` from the embedded horse asset;
5. build the PyInstaller onedir application with the horse icon, Learning Lab bundle, and required runtime dependencies;
6. smoke-test the packaged executable using the approved-runtime self-test;
7. build `Dad-Image-Tool-Setup.exe` with Inno Setup;
8. install and smoke-test the installed application;
9. run an upgrade test that verifies obsolete runtime files are removed while Pictures data survives;
10. upload the test installer and checksum as a temporary GitHub Actions artifact;
11. report the validation result on the tested commit.

The validation artifact is for testing only. It is not the normal end-user distribution path and is not published as a GitHub Release.

## User acceptance

Before publishing a release intended for normal use, complete the applicable checks in [TESTING.md](TESTING.md) on a real Windows PC. Automated tests do not replace the fresh-install, real-client-file, live Ask Pete/Learning Lab, update, and uninstall checks.

## Publishing a release

Production releases require an explicit matching version tag. A branch push alone must never publish a release.

Recommended process:

1. Finish the intended code and documentation changes.
2. Create a validation branch for the next version and set `APP_VERSION` to that version.
3. Open a pull request into `main` so the complete Windows validation workflow runs against the release candidate.
4. Confirm both the normal test workflow and the Windows installer validation workflow pass.
5. Use the generated test installer for any required real-Windows acceptance checks in [TESTING.md](TESTING.md).
6. When automated and manual acceptance are complete, merge the validated version bump into `main`.
7. Create tag `vX.Y.Z` on that exact approved commit.
8. The release workflow repeats syntax checks, automated tests, packaging, packaged and installed smoke tests, and upgrade/data-preservation checks before publishing GitHub Release `vX.Y.Z`.
9. Verify the release assets are present.
10. From the prior installed version, run **Check for Updates** and confirm the released update installs and restarts correctly.

Do not reuse an existing release version for changed binaries. Increment the version instead.

## Release assets

Each production release publishes:

- `Dad-Image-Tool-Setup.exe`
- `Dad-Image-Tool-Setup.exe.sha256`
- `Dad-Image-Tool-Update.json`

The setup program and checksum serve both first-time installation and in-app updates. The updater verifies the SHA-256 checksum before launching setup.

`Dad-Image-Tool-Update.json` is a small fallback manifest containing the released version and expected asset names. The updater checks the GitHub Releases API first. If `api.github.com` is unavailable or returns an unusable response, it requests this manifest through the ordinary `github.com/releases/latest/download/...` path and then downloads version-pinned setup/checksum assets. This keeps one GitHub hostname or API path from being a single point of failure.

Dad should receive the setup program or the normal release download link, not a repository ZIP, workflow artifact, or maintainer file.

## Data-safety requirement

A release must never depend on manually deleting the installed application directory. Setup is responsible for cleaning obsolete runtime files while preserving the separate `Pictures\Dad Image Tool` data tree.
