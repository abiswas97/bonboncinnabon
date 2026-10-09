# gaming

Game library and device workflows for Claude Code and Codex. Keeps a verified, system-first library on an external drive, backs it up without deletions, snapshots devices, records each device's frontend setup as a baseline it can check and rebuild, and handles emulator settings and cheats. Works for any platform: systems map to emulators as data, and tool knowledge lives in references.

Part of the `bonboncinnabon` marketplace.

## Skills

| Skill | Use it to |
|---|---|
| `setup` | Create or update the shared profile, add devices and storage, migrate older notes without losing values, and print the permissions to grant. |
| `onboard` | Add games with verified ROM identity, artwork and original documents; optionally install them on a device. |
| `sync` | Copy the library and collection changes to backup targets and devices, never deleting, with separate local and cloud evidence. |
| `backup` | Take a read-only, verified snapshot of a device's configuration, or of everything including saves, into the library. |
| `configure` | Change emulator or frontend settings at the narrowest scope, keep the frontend baseline in step, rebuild a frontend. |
| `cheats` | Find, build and install cheats and save edits for an exact ROM revision, keeping per-game tools in the library. |

In Claude Code the skills appear as `/gaming:<skill>`; in Codex, use the skill selector or `$<skill>`.

## The profile

All personal values live in one file that both hosts share:

```text
${XDG_CONFIG_HOME:-~/.config}/bonboncinnabon/gaming/profile.json
```

- `scripts/gaming_profile.py` is the only writer. It validates every change, keeps the previous version in `history/`, and replaces the file atomically.
- It holds libraries, backup targets, devices (SSH aliases, never credentials), emulators per system, frontend baselines, collection rules, policies and preferences.
- `profile.example.json` shows the shape with placeholders; `schemas/profile.schema.json` documents it.
- The profile survives plugin updates and uninstalls. To remove it, delete the `bonboncinnabon/gaming` folder above.

Plugins cannot grant themselves write access. On first run `setup` prints the entries to add:
- **Claude Code:** an `additionalDirectories` entry and an `Edit` allow rule for `~/.config/bonboncinnabon`.
- **Codex:** a `writable_roots` entry. Codex also asks before each SSH command, because its default sandbox has no network.

## Layout

```text
plugin.json            canonical metadata (projections are generated)
skills/<name>/SKILL.md the six skills
references/            profile, library layout, verification, reviewer brief,
                       device installation, frontend baselines, tools/<tool>.md
scripts/               standard-library Python: profile, checks, ROM verification,
                       tree sync, device snapshot, frontend baseline
schemas/               profile JSON Schema
tests/                 portability test and script tests
```

## Development

```bash
npm run plugins:sync
npm run test:gaming
npm run validate
```

Requirements: Python 3.11+ for the scripts (standard library only) and Node 22 for repository tooling. macOS and Linux.
