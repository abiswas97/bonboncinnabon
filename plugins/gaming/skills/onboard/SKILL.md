---
name: onboard
description: Adds games to the owner's library as complete, verified packages (ROM identity checked against reference catalogues, artwork, original manuals and documents), optionally installs them on a device, and keeps collections and backups current. Use when the owner wants a game added, imported, replaced with a better dump, its art or manuals filled in, or a batch of games brought into the library. Not for copying already-onboarded games to backups or devices (use sync) or for cheats (use cheats).
---

# Onboard games

Outcome: each requested game sits in the canonical library with verified files, mapped artwork, correctly classified documents and an updated manifest. Each gap is stated, and the game is installed only where the owner opted in. The owner's instructions override this skill.

The plugin root is two folders above this file. Run scripts as `python3 <plugin root>/scripts/<name>.py`. Before starting, read these references under `<plugin root>/references/`: `profile.md`, `library-layout.md` and `verification.md`.

## Start

- **Read the profile** (`gaming_profile.py show`). If it is missing, stop and point the owner to `setup`.
- **Check the drive** with `checks.py mounted --library <id>` before any write. Never create a stand-in folder when the drive is absent.
- **Run ledger.** Open or create `<root>/Staging/<run id>/run.json` (see `verification.md`). If a ledger for this request exists, resume from its `next_step` and reuse verified work.
- **Reuse, don't redo.** A repeat request for a game already in the library reuses verified files and fills gaps. It never duplicates or silently replaces anything.

## Stages

Update the ledger after each stage. A failed check stops the stages that depend on it until it is fixed and rechecked.

1. **Identity and scope.**
   - Establish: title, system, edition or revision, region, language, original or remake or hack, destination library, and the components wanted (game, art, documents, install).
   - Ask only about ambiguity that would change the result.
   - Note which collections and backup targets the profile says to keep current.
   - Storage only is the default. Install only if the owner asked or the device's `install_opt_in` is true. A game's name alone never implies installation.
2. **Acquire and verify the game.**
   - Look in this order: files the owner gave, the library (including other systems' folders), then the library's `extra_sources`. Absence from one folder is not absence from the drive.
   - Download only when needed, following `<plugin root>/references/acquisition.md`: ask first (file, source, size), respect access restrictions, and keep sign-ins temporary and out of every file.
   - Where a catalogue covers the game, check it with `verify_rom.py <file> --dat <root>/Tools/DATs/<dat>`; a mismatch blocks that edition. For hacks and translations, verify the base ROM against the DAT instead, and record the patch's own identity (name, version, source, hash) with the patched file's hash. For homebrew or anything no catalogue covers, run `verify_rom.py <file>` without `--dat` (hash and archive test only) and record the source, version and hash.
   - Hash the prepared file. Keep three things distinct: catalogue identity, transfer integrity, and achievement-hash compatibility.
   - Any patching or normalisation keeps the original file and needs evidence specific to that edition.
3. **Artwork.**
   - Gather cover, screenshot, title screen, marquee or logo, and metadata. Videos are optional.
   - Name each file with the exact ROM stem, matching this edition, and keep existing preferred art.
   - Run `checks.py images` on every image.
4. **Documents.**
   - Prefer original colour scans that match the language, region and edition: booklet, maps, reference cards and inserts.
   - Classify each as `In Box`, `Guides` or `Documentation`, following `library-layout.md`. Hack documentation is never presented as retail material.
   - Record source, page count and provenance, and render a representative page.
   - Reject modern abbreviated electronic manuals as substitutes for retail scans.
   - State what is missing rather than borrowing contents from another edition.
   - Importing into a reader app or converting formats is a separate opt-in.
5. **Publish.**
   1. Stage files in their final layout under `<run>/files/` (for example `files/ROMs/gba/...`), with a path, source and hash list in the ledger.
   2. Run `checks.py collisions <run>/files <root>`. Before replacing a different file, establish who owns it and keep a recovery copy.
   3. Run the reviewer gate from `verification.md` on the staged package. It judges identity, artwork, documents and the publish plan.
   4. For each staged top-level folder, run `sync_tree.py <run>/files/<folder> <root>/<folder> <run>/evidence/<folder>.json --apply`; when a replacement was approved, add `--preserve-conflicts --recovery-root "<root>/Recovery/Previous Library Files"`. The run folder itself is never copied.
   5. Copy `library-manifest.json` to `<run>/manifest-before.json`. Then update the manifest in its existing shape, marking verified items and gaps separately and never inventing provenance.
   6. Run `checks.py manifest-preserved <run>/manifest-before.json <root>/library-manifest.json`, adding `--updated <file>` for each replaced file and `--moved <old>=<new>` for each rename. Then run `checks.py manifest <root> --hash`.
   7. Never delete original art or backup copies to consolidate.
6. **Install** (opt-in only). Follow `references/device-install.md`: the reviewer gate on the install plan before writing, then `checks.py device-hashes`, a gamelist play-history comparison and the baseline drift check after writing. Report runtime as observed or pending; a launch command is not proof.
7. **Collections and backups.** If the profile enables collection upkeep or backup targets, run the `sync` workflow for the new games. Edits waiting on a stopped frontend stay in `Prepared/` and are reported as pending, not current.

## Done when

Every requested game is published with passing checks and reviewer verdicts, or listed as incomplete with the reason.

Report:
- the library location of each game
- verified components and gaps (missing requested components mean incomplete)
- install and runtime status
- backup and collection status
- the ledger path

Keep the verification evidence in the run folder and the manifest, never credentials.
