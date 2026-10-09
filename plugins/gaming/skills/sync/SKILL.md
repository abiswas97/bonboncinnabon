---
name: sync
description: Copies the owner's verified game library and collection changes to enabled backup targets and devices without ever deleting, keeps collections current under the profile's rules, and reports per-target evidence and restore readiness. Use for library backups, collection upkeep, pushing already-onboarded games or frontend files to a device, drift checks between library and devices, or "is everything backed up". Not for adding new games (use onboard) or snapshotting a device's own setup and saves (use backup).
---

# Sync the library

Outcome: every enabled target holds the in-scope library content, verified to the level claimed. Collections match the agreed rules. Nothing is deleted, and conflicts are preserved for the owner to decide. The owner's instructions override this skill.

The plugin root is two folders above this file. Run scripts as `python3 <plugin root>/scripts/<name>.py`. Before starting, read these references under `<plugin root>/references/`: `profile.md`, `library-layout.md` and `verification.md`. Also read `frontend-baseline.md` when a device's frontend is involved.

## Rules

- **Targets come from the profile.** Read the profile, `library-manifest.json` and the live state of each target. Honour standing opt-ins, and never invent a new target.
- **Copies are additive only.** No deletions, pruning or mirrored deletes. To retire something, the owner must agree to move it to an archive.
- **Saves are never merged.** Never pick a save by newest timestamp. When a save or any file differs between places, keep both and ask the owner which is authoritative. Use `--preserve-conflicts` only after that, and never automatically for saves.
- **New games go through `onboard` first.** Sync never bypasses its identity, art and document checks.
- **Frontend writes wait.** Writes to a device's frontend metadata wait for the owner to confirm the frontend is stopped (`frontend-baseline.md`). Prepare changes in `Prepared/` meanwhile, then re-read and rebase before deploying.

## Steps

1. **Check and discover (read-only).**
   - Run `checks.py mounted --library <id>`.
   - Ground each cloud target before writing: check that the local mirror exists, and confirm the folder (id, name, location) with the cloud connector. Without a connector, write nothing to that target and report it as pending.
   - Run `checks.py manifest <root>`, and run the baseline drift check for each device's frontend.
2. **Library first.** Open a run ledger under `<root>/Staging/<run id>/` (see `verification.md`), and keep script evidence in its `evidence/` folder. Then update the library itself before copying it anywhere:
   1. Copy `library-manifest.json` to `<run>/manifest-before.json`.
   2. Review collections: for each newly approved game, apply the profile's `collections` rules, and record desired membership in the manifest (observed device membership stays separate). Preserve owner edits and overlapping memberships, never pad a collection to fill it, and keep any franchise introduction order the owner set. Custom sort names are shared across every collection containing a game.
   3. Copy the profile to `<root>/Tools/profile.json` and compare hashes.
3. **Change set.**
   - For each folder target, run `sync_tree.py <root> <target> <run>/evidence/<target>.json --exclude Staging` without `--apply`. This covers every folder and the root-level files, and conflict copies land in `<target>/Recovery/Previous Cloud Files/`. Add `--exclude` for anything else outside the target's scope.
   - The library is authoritative for its own `library-manifest.json` and `Tools/profile.json`, so conflicts on those two are expected. When they are the only conflicts, apply with `--preserve-conflicts`, and the target keeps the old copy in its recovery folder. Any other conflict waits for the owner to name the authoritative copy.
   - Device targets do not use `sync_tree.py`. They go through `references/device-install.md`: SSH or SCP by alias, its reviewer gate on the install plan, then its "After writing" checks.
   - Show the owner the plan: counts, conflicts, collection edits and pending frontend writes.
4. **Recovery first.** Before changing a device, take a `full` snapshot with the `backup` workflow (`snapshot.py --device <id> --scope full`), which includes saves, states, BIOS and the frontend tree. Verify target paths from the device's active configuration before copying BIOS, saves, states or overrides.
5. **Apply.**
   - Run each `sync_tree.py ... --apply`.
   - For device targets, follow "Writing" and "After writing" in `references/device-install.md`: `checks.py device-hashes`, the play-history comparison, the baseline check, and a `full` snapshot after the change.
   - Deploy prepared frontend files only after the owner confirms the frontend is stopped.
6. **Verify and record.**
   - Re-run the checks, and check cloud presence and sizes with the connector.
   - Run the reviewer gate before reporting any target as verified.
   - Append a run entry (per-target results and restore paths) to the manifest's `backup_verification.runs` list, leaving existing fields as they are. Check with `checks.py manifest-preserved <run>/manifest-before.json <root>/library-manifest.json`, which fails if earlier history changed.
   - Push the final manifest to each folder target: copy it to `<run>/root-files/library-manifest.json`, then run `sync_tree.py <run>/root-files <target> <run>/evidence/<target>-manifest.json --apply --preserve-conflicts`.

## Evidence

Report each of these separately and only as far as proven:
- **local copy verified:** hashes match after copying
- **cloud presence verified:** connector metadata shows the files and sizes
- **cloud bytes verified:** server checksums or a download and readback
- **runtime observed**

A cloud desktop mirror is local staging until the server side is checked. Do not claim a full verified backup while any required component or target is missing or unverified.

## Done when

Report:
- counts per target
- scope and exclusions
- conflicts kept and awaiting the owner
- pending targets and frontend writes
- evidence paths
- restore steps (where each target's copy and the recovery snapshots live)

Do not set up recurring automation unless the owner asks.
