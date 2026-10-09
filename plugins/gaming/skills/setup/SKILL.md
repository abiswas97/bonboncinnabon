---
name: setup
description: Creates or updates the shared gaming profile that every gaming skill reads (libraries, backup targets, devices and how to connect, emulators per system, frontend baselines, policies, preferences) and migrates values from older notes or profiles without losing any. Use on first use, to add or change a device, library or backup location, when another gaming skill reports a missing profile, or to import a profile on a new machine. Not for changing emulator or frontend settings on a device (use configure).
---

# Gaming setup

Outcome: a valid profile that holds everything the other gaming skills need, with every device's connection tested and the owner told how to grant write access. The owner's instructions override this skill.

The plugin root is two folders above this file. Run scripts as `python3 <plugin root>/scripts/<name>.py`. Read `<plugin root>/references/profile.md` before starting.

## Steps

1. **Find the profile.** Run `gaming_profile.py path`, then `gaming_profile.py show`.
   - If it exists, you are updating: show the owner the relevant current values, ask what should change, and go to step 5.
   - If it does not exist, continue.

2. **Gather before asking.** Collect what existing sources already say, without printing file contents or secrets:
   - a library copy at `<library root>/Tools/profile.json`; offer to import it on a new machine
   - an older library profile such as `<library root>/Tools/sync-profile.json`, older skill folders, or project notes the owner points to
   - `Host` aliases in `~/.ssh/config` (names only)
   - each reachable device's frontend settings, read with `esde_baseline.py capture --settings <file>`, which drops account fields
   - emulator config locations, from listing the files only

3. **Ask once.** Put every remaining question in one batch, asked from the main conversation:
   - the canonical library root and the volume it lives on
   - extra folders to search for games
   - backup targets with scope and local mirror
   - devices with label, platform, connection, storage paths, which emulator and core runs each system, and whether installs there are pre-approved
   - which frontend settings are deliberate (the baseline)
   - collection rules, timezone and preferences

   Offer the profile's example values as defaults only where they are generic.

4. **Migration report** (when older sources exist). Write `<library root>/Tools/migration/<YYYY-MM-DD>-report.md`, a table with one row per source value. Each row maps the value to exactly one destination:
   - a profile pointer
   - `library-manifest.json`
   - a snapshot under `Frontends/` or `Recovery/`
   - a tool reference in this plugin
   - `not kept: <reason>`, only for logs and verification evidence

   If any value has no destination, stop and list it for the owner. Get the owner's approval of the report before writing anything. Leave every source file untouched.

5. **Show, then write.**
   - Show the assembled profile, or the exact changes, and get a yes.
   - For a new profile, save the draft to the library's `Staging/` folder, run `gaming_profile.py validate --file <draft>`, then `gaming_profile.py init --from <draft>`.
   - For changes, preview each `set`, `unset` or `note` with `--dry-run`, then apply it.

6. **Read back.** Run `gaming_profile.py show` on every changed pointer. In migration mode, confirm every report row, mark it confirmed in the report, and fix any mismatch before continuing.

7. **Permissions.** Print these for the owner to add. A plugin cannot grant itself access, and the owner manages security settings, so never edit host settings yourself.
   - Claude Code user settings (`settings.json` in the active Claude config folder):
     ```json
     { "permissions": { "additionalDirectories": ["~/.config/bonboncinnabon"], "allow": ["Edit(~/.config/bonboncinnabon/**)"] } }
     ```
   - Codex `~/.codex/config.toml`, using the absolute home path:
     ```toml
     [sandbox_workspace_write]
     writable_roots = ["/Users/<you>/.config/bonboncinnabon"]
     ```
     Codex's default sandbox has no network, so it asks before each SSH command. That is expected.

8. **Test connections read-only.** For each `ssh` device, run `ssh -o BatchMode=yes -o ConnectTimeout=8 <alias> true`. On failure, give the owner the device's `connect.hints` and record any new working hint as a note.

9. **Frontend baselines.** For each device with a frontend and no baseline, agree the deliberate settings with the owner and store them with `gaming_profile.py set /devices/<id>/frontend/baseline/settings '<json>'`. Take a `config` snapshot with the `backup` workflow, and copy the frontend files into the library's `Frontends/<app>/<device>/Current/` following "Refreshing the library copy" in `<plugin root>/references/frontend-baseline.md`. Then run `esde_baseline.py check --settings <settings file> --device <id>` to confirm no drift.

## Done when

- `gaming_profile.py validate` passes.
- Every changed value reads back as intended, and in migration mode every report row is confirmed.
- Each device's connection was tested, or its failure was reported with hints.
- The permission entries were shown to the owner.

Report what changed, the profile path, and anything still pending.
