# Releasing Dad Image Tool

This document is for the person maintaining the project. The end user does not need it.

## Before the first handoff

1. Finish testing on the maintainer's Windows computer.
2. Change the GitHub repository visibility to public.
3. Confirm `version.py` points to:

   `Necropolite/-Dad-Image-Tool`

4. Choose the first release version, such as `0.2.0`.
5. Confirm `APP_VERSION` in `version.py` matches that version.
6. Push all changes to the default branch.
7. Create and push a matching tag with a leading `v`, such as `v0.2.0`.
8. Wait for the **Build Release** GitHub Action to finish.
9. Open the GitHub release and confirm it contains:
   - `Dad-Image-Tool.exe`
   - `Dad-Image-Tool.exe.sha256`
10. Install the release-enabled version on a test computer and use **Check for Updates** to test the next release before giving it to the end user.

## Publishing a normal update

1. Make and test the code changes.
2. Increase `APP_VERSION` in `version.py`.
3. Commit and push the changes.
4. Create a tag that exactly matches the version:

```text
APP_VERSION = "0.2.1"
tag = v0.2.1
```

5. Push the tag.
6. GitHub Actions builds the executable, creates a SHA-256 checksum, and publishes both files in a GitHub release.
7. Installed copies detect the newer release and offer to install it.

The release workflow intentionally fails if the tag and `APP_VERSION` do not match.

## Update safety

The updater:

- Only accepts a release newer than the installed version.
- Requires both the executable and its checksum file.
- Verifies the downloaded executable with SHA-256 before replacement.
- Retries replacement while the old app closes.
- Restarts the new version automatically.
- Does not touch `Pictures\Dad Image Tool` or any client files.

## Private repository limitation

Automatic updates use GitHub's public Releases API and anonymous release downloads. They will not work while the repository is private.

Do not place a personal GitHub token inside the app. Make the repository public before the first external installation, or move compiled releases to a separate public repository and update `GITHUB_REPOSITORY` in `version.py`.

## First-install distribution

For the first test handoff, the end user may download the repository ZIP and run `Install.bat`. After an updater-enabled release is installed, later updates are handled inside Dad Image Tool.

A future improvement is a downloadable setup executable so the end user never has to view the source repository.