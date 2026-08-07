# Releasing Dad Image Tool

Dad Image Tool uses `major.minor.patch` versions. `APP_VERSION` in `internal/src/version.py` is the version source of truth.

The published release tag is `vX.Y.Z` and must match `APP_VERSION`.

## Main-branch build gate

Every non-setup-build push to `main` runs `.github/workflows/build-test-installer.yml`.

Before it publishes the root setup executable, the workflow must successfully:

1. install dependencies;
2. compile the Python source;
3. run the automated test suite;
4. generate `Dad-Image-Tool.ico` from the embedded horse asset;
5. build the PyInstaller onedir application with the horse icon;
6. smoke-test the packaged executable;
7. build `Dad-Image-Tool-Setup.exe` with the same icon;
8. install and smoke-test the installed application;
9. run an upgrade test that verifies obsolete runtime files are removed while Pictures data survives;
10. upload the test installer artifact;
11. publish the tested setup executable at the repository root.

A root installer commit is therefore evidence that the preceding build gates completed successfully for that build.

## User acceptance

Before publishing a release intended for normal use, complete the applicable checks in [TESTING.md](TESTING.md) on a real Windows PC. Automated tests do not replace the fresh-install and real-client-file checks.

## Publishing a release

The release workflow accepts either a matching version tag or a `release/vX.Y.Z` branch. The release branch method is useful when release creation is being driven through the GitHub connector.

Recommended process:

1. Finish and validate the intended `main` commit.
2. Set `APP_VERSION` to the release version before the final validated build.
3. Confirm the main-branch test installer has passed for that state.
4. Complete the required real Windows acceptance checks.
5. Create `release/vX.Y.Z` from the validated commit.
6. The release workflow verifies the branch/version match, repeats tests and packaging, and publishes GitHub Release `vX.Y.Z`.
7. Verify the release tag exists and the setup/checksum assets are present.
8. From the prior installed version, run **Check for Updates** and confirm the released update installs and restarts correctly.

Do not reuse an existing release version for changed binaries. Increment the version instead.

## Release assets

Each release publishes:

- `Dad-Image-Tool-Setup.exe`
- `Dad-Image-Tool-Setup.exe.sha256`

These same installer assets serve both first-time installation and in-app updates. The updater verifies the SHA-256 checksum before launching setup.

Dad should receive the setup program or the normal download link, not a repository ZIP, workflow artifact, or maintainer file.

## Data-safety requirement

A release must never depend on manually deleting the installed application directory. Setup is responsible for cleaning obsolete runtime files while preserving the separate `Pictures\Dad Image Tool` data tree.
