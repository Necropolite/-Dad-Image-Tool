# Third-Party Review Guide

## Review target

Review pull request **#2**, branch `code-review-hardening-0.2.2`, against `main`.

Use the pull request's **Files changed** view as the authoritative review surface. The branch history contains mechanical one-file commits created by the GitHub connector; those commits do not represent architectural units. The pull request should be squash-merged only after review and validation.

Dad Image Tool is a Windows watched-folder application for a nontechnical equine specialist. The user saves pictures, folders, or ZIP files into one folder. The program waits for the item to stabilize, converts supported pictures to JPEG, archives successful originals, and retains failed sources for attention.

The application is intentionally small. The review should favor reliability, understandable boundaries, and preservation of client files over additional features.

## Architecture

The intended dependency direction is:

```text
main.py
  -> watcher.py
       -> ui_layout.py
       -> history_window.py
       -> update_ui.py -> updater.py
       -> watcher_processing.py -> app.py, history.py, watcher_support.py
       -> watcher_support.py -> app.py
```

Important boundaries:

- `app.py` contains conversion and ZIP handling. It must not depend on Tkinter, GitHub, or the watched-folder UI.
- `watcher.py` coordinates scanning, lifecycle, and UI events. It should not duplicate conversion or updater internals.
- `watcher_processing.py` owns per-source routing and history recording.
- `watcher_support.py` owns filesystem stability, Windows folder resolution, moves, and single-instance behavior.
- `updater.py` owns network access, release verification, executable replacement, restart confirmation, and rollback.
- UI modules should remain thin and should not perform conversion or network work directly.

## Safety invariants

Please treat violations of these rules as high-severity findings:

1. Processing must never delete an original source.
2. Existing finished files and archived originals must never be overwritten.
3. A failed source must not contaminate the routing of an unrelated successful source.
4. Changing or partial downloads must not be processed.
5. Directory links and Windows junctions must not be followed into unrelated locations.
6. ZIP entries must not escape their extraction directory or exploit Windows path behavior.
7. A failed install or update must leave a runnable prior version whenever replacement had begun.
8. Installer and updater operations must not modify `Pictures\Dad Image Tool` user data.
9. Updating, closing, or uninstalling must not interrupt an active picture-processing job.
10. The released application must not contain a GitHub token or another embedded secret.

## Threat model

Inputs are untrusted client files downloaded from email or cloud services. Relevant threats include:

- corrupt or malformed image files;
- decompression bombs and excessive resource consumption;
- encrypted or corrupt ZIP files;
- path traversal and absolute ZIP paths;
- case-insensitive filename collisions on Windows;
- reserved Windows names, alternate data stream syntax, and file/folder conflicts;
- nested ZIP recursion;
- symbolic links and junctions;
- incomplete downloads and files still held open by another process;
- interrupted installer or updater replacement;
- compromised or incomplete release downloads.

The updater trusts GitHub's public Releases API only to locate assets. The downloaded executable is accepted only when its SHA-256 matches the separately published checksum asset. This protects against accidental corruption and asset mismatch, but it is not code signing and does not protect against compromise of the release repository itself.

## Review priorities

Please review these areas most closely:

1. Tkinter thread handoff and shutdown behavior in `watcher.py` and `update_ui.py`.
2. Race conditions between stability detection, processing, moves, closing, installing, and updating.
3. ZIP validation and extraction in `app.py`.
4. Original preservation and routing in `watcher_processing.py` and `watcher_support.py`.
5. Windows path handling, links, junctions, and reserved names.
6. Transaction and rollback behavior in `Install.bat`, `Uninstall.bat`, and `updater.py`.
7. Whether module responsibilities remain coherent and easy to maintain.
8. Missing tests for plausible failures, especially Windows-only paths.

## Questions for the reviewer

- Is any module doing work that clearly belongs in another module?
- Are there hidden dependencies, circular responsibilities, or state mutations that make behavior hard to follow?
- Can any timing window destroy, overwrite, strand, or repeatedly process a source item?
- Can a crafted archive write outside its temporary extraction directory or create an unsafe Windows path?
- Can updater or installer failure leave neither the old nor new executable usable?
- Are errors understandable to the end user while preserving enough information for support?
- Are any tests asserting implementation details instead of durable behavior?
- What should be fixed before the first installation on the end user's computer?

## Automated review commands

On Windows with Python 3.12:

```bat
Run-Tests.bat
```

Equivalent commands:

```text
python -m pip install -r requirements-dev.txt
python -m compileall -q app.py history.py history_window.py main.py ui_layout.py update_ui.py updater.py version.py watcher.py watcher_processing.py watcher_support.py tests tools
python -m ruff check .
python -m coverage run -m unittest discover -s tests -v
python -m coverage report -m
python tools/generate_review_fixtures.py review-fixtures
```

The coverage threshold applies only to the core processing, history, updater, routing, and filesystem-support modules. Tkinter layout code is tested selectively but is not included in the numeric threshold.

## Current evidence

- Syntax compilation passed locally.
- 49 automated tests passed locally.
- Branch-aware core-module coverage measured 71% locally.
- The application-module import graph had no cycles in the prior architecture pass.

These statements are not substitutes for Windows CI. Review the current workflow result for the exact PR head before relying on them. Ruff could not be installed in the isolated local audit environment, so the first authoritative Ruff result must come from Windows CI or a reviewer's environment.

## Known unverified areas

The following require a real Windows acceptance test and should not be treated as passed merely because source tests succeed:

- packaged HEIC and HEIF decoding;
- PyInstaller executable startup on the target Windows version;
- desktop and startup shortcuts;
- SmartScreen behavior;
- installation over an actively running older copy;
- forced installer rollback;
- full update from an older public GitHub Release;
- startup-marker update rollback in the packaged executable;
- reboot and automatic-start behavior.

See `TESTING.md` for the manual acceptance checklist.
