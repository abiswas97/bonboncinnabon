---
name: backup
description: Takes a read-only, verified snapshot of one device's emulator and frontend configuration, or a full snapshot including installed games, BIOS, saves and states, into the library's Recovery folder, without changing anything on the device. Use when the owner asks to back up a device, its settings or saves, or before risky device changes. Not for backing up the library itself to other targets (use sync) or restoring files (a separate, explicit request).
---

# Back up a device

Outcome: a new folder `<library root>/Recovery/<device label>/<timestamp>/` holding an archive and a `manifest.json` with `status: verified`. The device is left exactly as it was. The owner's instructions override this skill.

The plugin root is two folders above this file. Run scripts as `python3 <plugin root>/scripts/<name>.py`. Read `<plugin root>/references/profile.md` first.

## Scope

- **`config`:** emulator config files, overrides, remaps, core options and shader presets, plus the frontend's settings, collections, custom systems and gamelists.
- **`full`:** everything in `config`, plus the frontend home (including media and theme changes), and installed games, BIOS, saves and states. Data folders come from the profile's `paths` and from the emulator's active config (`data_keys`, such as RetroArch's save, state and system directories).

A snapshot is not an image of the whole operating system or of app-private data. Say so when the owner asks for "everything".

## Steps

1. **Pick the device and scope.** Read the profile. Confirm the device id and scope with the owner when the request is ambiguous; `full` can be large.
2. **Preview.** Run `snapshot.py --device <id> --scope <scope> --dry-run` and check the roots and missing paths. Missing roots are recorded, not invented. App-private folders the connection cannot read are gaps to report.
3. **Snapshot.** Run `snapshot.py --device <id> --scope <scope>`. The script:
   - reads the device only
   - checks the library drive is mounted, without creating stand-ins
   - inventories and hashes before and after
   - streams the archive
   - verifies every member
   - writes the manifest
4. **Frontend check.** If the device has a frontend baseline, read its `frontend.settings_file`: in place for a local device, or over SSH with `cat` into `<root>/Staging/<YYYY-MM-DD>-backup-<device id>/`, without printing it. Then run `esde_baseline.py check --settings <file> --device <id>`. Report drift to the owner without fixing it here. To refresh the library's `Frontends/<app>/<device>/Current/` copy, follow "Refreshing the library copy" in `<plugin root>/references/frontend-baseline.md`.
5. **Profile copy.** Copy the profile to `<root>/Tools/profile.json` and compare hashes.

## Rules

- **The device stays untouched.** Never start, stop or reconfigure an app, and never ask one to save its settings. The snapshot records what is on disk, which may differ from unsaved settings in a running app.
- **Config contents stay opaque.** Never print them, copy them into notes or memory, or commit them; they can contain account details. The manifest holds paths, sizes and hashes only. The archive is private but not encrypted.
- **Incomplete means not verified.** If files changed during capture, the script keeps an archive marked incomplete. Report it as not verified and offer to retry at a quieter moment.
- **Connection trouble.** If SSH fails, pass on the device's `connect.hints` (for example, wake the device or turn on its VPN). If the drive is absent, stop. Never substitute an older local or project copy of the device's files for a live snapshot.
- **Where snapshots are built.** The script builds in `<root>/Staging/snapshots/` and moves the folder into `Recovery/` only once verified, so an unfinished snapshot never reaches `Recovery/` or the backup targets.
- **Old snapshots are never overwritten.** Restoring from a snapshot is a separate request; do not restore as part of a backup.

## Done when

`manifest.json` says `status: verified`.

Report:
- the folder
- the verified file count
- missing paths and unreadable areas
- frontend drift, if any

Anything less is reported as not verified.
