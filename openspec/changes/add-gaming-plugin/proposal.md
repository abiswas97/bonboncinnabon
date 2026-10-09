## Why

The owner's game-library workflows (adding games, syncing backups, snapshotting devices) exist only as Codex-only personal skills with hard-coded paths, device names and cloud IDs, and the device knowledge they depend on is scattered across project notes, agent memories and live config files. A host-neutral `gaming` plugin with one persistent profile lets Claude Code and Codex share the same workflows and memory, and covers any emulated or native platform rather than one handheld.

## What Changes

- Add `gaming@bonboncinnabon`, installable in Claude Code and Codex, with six skills: `setup`, `onboard`, `sync`, `backup`, `configure`, `cheats`.
- Add a persistent profile at `${XDG_CONFIG_HOME:-~/.config}/bonboncinnabon/gaming/profile.json` holding libraries, backup targets, devices and how to connect to them, per-device emulators and frontend baselines, policies, preferences and short learned notes. Only a bundled stdlib script writes it, atomically, with schema checks and a history copy. It never holds credentials.
- Make every device's frontend setup (ES-DE first) a recorded baseline: intended settings in the profile, full files in the library, and a drift check before and after changes.
- Replace per-stage model verifiers with scripted checks (hashes against reference catalogues, sizes, paths, collisions, manifest consistency) plus one fresh-context reviewer before anything is published to the library or installed on a device.
- Keep all platform and tool knowledge out of the core workflows: systems map to emulators as profile data, and tool-specific knowledge lives in references read only when that tool is involved.
- Migrate the owner's existing values losslessly into the profile through an itemised migration report the owner approves; old sources stay untouched until the owner confirms archiving.
- Add portability tests (frontmatter shape, host-only patterns, emphasis words, size) and Python tests for every bundled script to `npm run validate`.

## Capabilities

### New Capabilities

- `gaming-profile`: Location, format, ownership, write path, privacy and migration of the shared gaming profile.
- `game-library`: Canonical library layout, the `onboard` workflow, run ledgers and the verification model.
- `game-sync-and-backup`: The `sync` and `backup` workflows, non-destructive copy rules and evidence.
- `frontend-baseline`: Recording, checking and restoring each device's frontend setup.
- `emulator-customization`: The `configure` and `cheats` workflows, scope rules and per-game tool storage.

### Modified Capabilities

- `portable-plugin-marketplace`: Adds `gaming@bonboncinnabon` to both generated marketplaces and its tests to repository validation.

## Impact

- New `plugins/gaming/` package (canonical `plugin.json`, six skills, shared references, stdlib Python scripts, JSON schema, example profile, tests, README, CHANGELOG) and its generated Claude and Codex projections.
- `marketplace/marketplace.json`, `package.json` scripts and the generated catalogs gain the new plugin.
- Outside the repository: a new profile under `~/.config/bonboncinnabon/gaming/`, a Mac ES-DE snapshot added to the owner's library, and the superseded Codex skills archived (not deleted) after the plugin is installed and verified in Codex.
- One-time host permissions that plugins cannot grant themselves: `setup` prints the Claude settings and Codex `writable_roots` entries for the owner to add.
