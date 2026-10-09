---
name: configure
description: Changes emulator or frontend settings on one of the owner's devices at the narrowest scope that works (game, content folder, core, then global), after a backup, keeps the frontend baseline in step, and rebuilds a frontend setup from the library. Use for controls, hotkeys, remaps, turbo, shaders, audio filters, per-game overrides, frontend themes and settings, adding an emulator for a new system, or "why didn't my setting stick". Not for cheats or save edits (use cheats) or backups (use backup).
---

# Configure an emulator or frontend

Outcome: the requested behaviour is in place at the narrowest scope that achieves it. A snapshot exists from before the change, the change is confirmed from the device's files, and the profile reflects any new deliberate setting. The owner's instructions override this skill.

The plugin root is two folders above this file. Run scripts as `python3 <plugin root>/scripts/<name>.py`. Read `<plugin root>/references/profile.md` first. Read `<plugin root>/references/tools/<tool>.md` for each tool the device's profile entry uses, and only those. For frontend changes, also read `<plugin root>/references/frontend-baseline.md`.

## Steps

1. **Understand the request.**
   - Read the device's profile entry: `systems`, `emulators`, `frontend` and `notes`.
   - Restate the goal in one line, for example: L2 and R2 fast-forward without a hotkey, only in Game Boy cores.
   - If it would change something the owner chose earlier (a baselined setting or a note), say so and confirm first.
2. **Find what is in effect now.**
   - Read the device's live files: main config, the overrides at each layer, the active remap, and core options.
   - Identify which file wins for each relevant key, using the layering rules in the tool reference.
   - For "it didn't stick", explain the cause from those files before proposing a fix. Typical causes: an override masking a global change, a remap rewritten on exit, a single remap file winning, or appended config persisting.
3. **Check the docs.** Confirm the setting names and values in the tool reference and the official documentation for the device's version. Well-known community setup guides help with intent, but the official docs and source decide syntax.
4. **Snapshot.** Run `snapshot.py --device <id> --scope config`, or follow the `backup` skill. Also keep a dated `.bak-<YYYYMMDD>-<topic>` copy next to each file you will edit.
5. **Change at the narrowest scope.**
   - Prefer a game override over a content-folder override, over a core override, over global.
   - Edit files while the emulator is closed, or say when a running app will overwrite them.
   - Keep one action per button unless the owner wants otherwise.
   - For frontend settings, get the owner's confirmation that the frontend is stopped when the profile requires it.
6. **Verify.**
   - Re-read the edited files from the device and show the changed keys.
   - Run the frontend baseline check when the frontend was touched.
   - List what only an in-game test can confirm, and ask the owner to try it, or test on a desktop copy when one exists.
7. **Record.**
   - If the owner adopted a new deliberate frontend setting, update the baseline with `gaming_profile.py set`.
   - If you learned a durable device fact (a quirk, a whitelist need, a path), add it with `gaming_profile.py note`.
   - Tool-wide lessons belong in the tool reference; propose that edit to the owner.

## Rebuilding a frontend

When a device's frontend was reset or reinstalled, follow "Rebuild a frontend" in `frontend-baseline.md`: snapshot, stopped confirmation, restore from the library's `Frontends/<app>/<device>/Current/` with gamelists rebased on live play history, then a drift check and the owner's visual confirmation.

## Adding a system or emulator

- **Discover the emulator's facts.** For a new system on a device (for example PS2 or Switch on the desktop), find its formats, BIOS, firmware or key needs, config locations and how the frontend launches it.
- **Record them in the profile** with `set` under `systems` and `emulators`.
- **BIOS, firmware and keys** come only from the owner's own files.
- **Prefer what the owner prefers** (`preferences`), for example standalone builds over store builds, and windowed play.

## Done when

The change is confirmed in the device's files, any frontend drift is resolved or reported, and the snapshot path is reported. Also report what still needs an in-game check, and the profile updates made.
