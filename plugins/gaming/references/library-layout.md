# Library layout

`<root>` is the canonical library's `root` from the profile. A different storage medium changes the root, never the layout. System folders use lowercase, frontend-compatible ids such as `nes`, `snes`, `gb`, `gbc`, `gba`, `nds`, `3ds`, `ps2`, `switch`. When a device names a system differently (for example `n3ds`), record that as `devices.<id>.systems.<system>.folder` in the profile instead of renaming library folders.

```text
<root>/
  ROMs/<system>/<canonical game file or game folder>
  Media/<system>/covers/<ROM stem>.<ext>
  Media/<system>/screenshots/<ROM stem>.<ext>
  Media/<system>/titlescreens/<ROM stem>.<ext>
  Media/<system>/marquees/<ROM stem>.<ext>
  Media/<system>/videos/<ROM stem>.<ext>
  Documents/<system>/<ROM stem>/In Box/<descriptive name>.pdf
  Documents/<system>/<ROM stem>/Guides/<descriptive name>.pdf
  Documents/<system>/<ROM stem>/Documentation/<descriptive name>
  BIOS/<system or existing platform family>/
  Archives/<system>/
  Frontends/<app>/<device label>/Current/<actual frontend files>
  Frontends/<app>/<device label>/Prepared/<pending frontend files>
  Recovery/<device label>/<timestamp>/<archive and manifest.json>
  Staging/<run id>/<run.json and staged files>
  Tools/Cheats/<system>/<game>/
  Tools/DATs/<catalogue files>
  Tools/profile.json
  library-manifest.json
```

## Rules

- **Follow this layout strictly.** It is system-first: never a franchise-first layout, and never a chat or scratch workspace as the final home.
- **Create only what is needed.** Make only the folders that real assets need.
- **One stem everywhere.** The ROM file name without its extension names the media files and the document folder.
- **Multi-file games:** 3DS titles, Switch base, update and DLC files, and disc sets keep one canonical folder per game. Its folder name is the document and media identity, and the manifest lists each constituent file.
- **Do not rename ROMs casually.** Frontend references, saves and achievement hashes may depend on the current name or content.
- **Media is the canonical home for artwork.** Frontend media folders are device copies. Never let a frontend folder hold the only curated copy. Keep existing preferred artwork unless the owner asks to replace it.
- **Documents:**
  - `In Box` holds material that shipped with that edition: booklets, maps, reference cards, inserts, and a guide only if it was actually in the box.
  - `Guides` holds separately sold guides of the time.
  - `Documentation` holds hack, patch or translation documents. Never present those as retail material.
- **PC and BIOS.** Preserve the existing `PC` area and BIOS conventions. BIOS, firmware and keys only ever come from the owner's own files.
- **Archives** hold originals that were replaced or consolidated. Archive, never delete.
- **Staging** holds work in progress, run ledgers and unfinished snapshots, on the library drive to save internal disk space. Publish from staging into the layout one top-level folder at a time. `sync` never copies `Staging/` to backup targets.
- **Per-game tools.** `Tools/Cheats/<system>/<game>/` holds a README, emulator cheat and override files, patch sources, tests, save editors and data for one game. `sync` mirrors it like the rest of the library.
- **Filesystem clutter.** Copies to exFAT drives can leave `._*` files. Clean only the specific folder you wrote (for example `dot_clean -m <that folder>`), never the whole drive.

## The manifest

`library-manifest.json` is the one catalogue; never start a competing one.

- **Keep the existing schema, `files` and historical `additions`.** Add entries in the same shape: source, bytes, SHA-256, game and edition mapping, document classification, and verification and gap evidence.
- **Collection definitions** live in its `collections` field as root-relative ROM identities.
  - Keep observed device memberships separate from desired or prepared ones.
  - Frontend collection files on devices (for example ES-DE `.cfg` files with absolute paths) are device-specific projections, not the catalogue.
- **Portable descriptive metadata** goes in the manifest. Live frontend gamelists stay frontend-specific.

## Migrating or consolidating

- **Copy with verification.** Copy curated assets with source and destination hash checks.
- **Backups stay backups.** Treat older backup libraries (the profile's `extra_sources`) as backups to search, not as the authoritative library.
- **Newer deployed copies.** If a device holds newer chosen artwork, compare its bytes with the deployment evidence before adopting it.
- **Old backups may be stale.** Never assume an old backup matches a device's current state.
- **Missing sources are gaps.** An unavailable source is a recorded gap, not permission to guess.
- **Keep the originals.** Never delete original artwork or backup copies just to consolidate.
