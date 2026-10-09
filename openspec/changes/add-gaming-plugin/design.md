## Context

The owner runs a system-first game library on an external drive, mirrored to cloud storage, and plays on several devices (an Android handheld and a Mac today; PS2, DS, 3DS, Switch and PC games later). Three personal skills drive this today, written for Codex only: `onboard-game`, `sync-games` and a project skill `retrobackup`. They hard-code the drive path, an SSH alias, a cloud folder ID, a timezone and collection preferences, and they lean on a long project notes file for device knowledge. This change replaces them with a host-neutral plugin and moves every personal value into one profile.

Research inputs (2026-10-09): Anthropic skill-authoring, prompting, context-engineering and Claude Code plugin docs; OpenAI Codex skills, plugins, sandbox, subagent and GPT-6 prompting docs plus the `openai/codex` source; the Agent Skills specification; and a survey of how cross-host plugins and CLIs store user configuration.

## Goals / Non-Goals

**Goals:**
- Parity: the new skills, references, scripts and profile together produce the same effects and carry the same knowledge as the three skills they replace, plus the device lessons gathered since (see `parity.md`).
- One profile shared by Claude Code and Codex, readable when the library drive is unplugged, never holding credentials.
- Every device's frontend setup recorded as a baseline that can be checked and rebuilt.
- Platform-neutral workflows: adding PS2 or Switch support means adding profile data and a tool reference, not editing skills.

**Non-Goals:**
- Hooks that enforce policies (a "no deletes inside the library" guard is the first candidate if a policy is ever broken).
- Codex `onboardingSkill` and `allow_implicit_invocation` generator support; Agent Plugins root manifests; `claude plugin eval` suites (the pinned validator predates it).
- Windows support, scheduled automation, and onboarding any specific games (a follow-up uses the shipped plugin).

## Decisions

### D1. Profile at `${XDG_CONFIG_HOME:-~/.config}/bonboncinnabon/gaming/profile.json`
- Host plugin-data folders were rejected. They are per host (this machine already has three copies of another plugin's data folder), Claude Code deletes them on uninstall, and Codex does not substitute `${PLUGIN_DATA}` into skill text, so a Codex skill cannot locate it.
- `~/.config/<app>` is the common convention for cross-host tool config on macOS and Linux, used by gh, git, uv, ponytail and superpowers/episodic-memory. XDG classes a curated profile as configuration.
- `~/Library/Application Support` was rejected: it is meant for GUI apps, and its space breaks shell quoting.
- The `bonboncinnabon/` namespace means one permission grant and one backup path cover future plugins.
- Relative `XDG_CONFIG_HOME` values are ignored, per the XDG specification.
- The data library was rejected because it is unavailable whenever the drive is unplugged. The library still receives a copy (D3).

### D2. JSON written only by `scripts/gaming_profile.py`
- Plugin scripts use the Python standard library, which reads JSON but not YAML.
- Agents never hand-edit the file. `gaming_profile.py` provides `path`, `show [pointer]`, `set <pointer> <json> [--dry-run]`, `note <device> <text>`, `validate` and `init --from <file>`.
- Every write validates the result, copies the previous version to `history/profile-<UTC>.json`, then replaces the file atomically.
- `schemas/profile.schema.json` documents the shape for editors and for the dev-time schema test. `gaming_profile.py` enforces the same required fields and types at runtime without third-party libraries.
- Notes are dated one-liners, at most 50 per device, holding durable facts only. Logs and verification evidence go to the library manifest or run ledgers.

### D3. What lives where
- **Profile (intent and access):**
  - libraries and their extra search sources
  - backup targets
  - devices: connection method and SSH alias, storage paths, per-system emulator and core, frontend baseline, install opt-in, notes
  - collection policy, policies, preferences
- **Library:**
  - `library-manifest.json`: the catalogue and its evidence
  - `Frontends/<app>/<device>/Current`: actual frontend files
  - `Recovery/<device>/<timestamp>`: device snapshots
  - `Tools/`: per-game tools and the reference catalogue (DAT) files
- **Profile copy in the library:** `sync` and `backup` copy the profile into `Tools/profile.json`, so it is recoverable from the library and the cloud. This is a copy, not a second source: the `~/.config` file stays authoritative.
- **Connection secrets:** stay in SSH configuration and host credential stores. The profile stores only aliases.

### D4. Verification: scripts plus one reviewer
- **Scripted checks:** hashes against No-Intro or Redump DATs, sizes, presence, path and name collisions, image header sanity, archive members, manifest consistency, and source stability during a copy. Scripts exit non-zero with a reason, and a failed check stops dependent work.
- **One reviewer for judgment calls:** right edition and region, art that matches the exact ROM, a manual that is an original retail scan, correct document classification. The reviewer runs once before publishing to the library and once before installing on a device.
- **How the reviewer is started:** the skill asks the host for a subagent with no conversation history and gives it only paths, the request and `references/reviewer.md`. It never modifies files. This follows devlab's proposer and critic pattern.
- **If the host cannot start a subagent:** the skill stages and reports, and publishes nothing.
- **Why:** this replaces the seven per-stage model verifiers. The owner approved the change on 2026-10-09 because scripted checks are stronger evidence than model agreement, and multi-agent runs cost about 15x a single chat.

### D5. Platform-neutral by data
- Devices declare `systems.<library-system-id>` → `{emulator, core?, folder?}`, so per-device folder names such as `n3ds` versus `3ds` are data.
- Tool knowledge lives in `references/tools/<tool>.md`: `retroarch.md` and `es-de.md` now, others as they are needed. Skills read a tool reference only when the device in use declares that tool.
- Multi-file games (3DS folders; Switch base, update and DLC) keep one folder per game in `ROMs/<system>/`, and the manifest records each constituent file.
- BIOS, firmware and keys only ever come from the owner's own files. No skill downloads them.

### D6. Frontend baseline
- Each device's `frontend.baseline` records the settings the owner chose deliberately, plus theme, variant and collection presentation. It is a subset, not the whole settings file.
- The full current files live in the library under `Frontends/<app>/<device>/Current`.
- `scripts/esde_baseline.py check` compares a settings file with the baseline and lists drift. `configure`, `sync` and `backup` run it before and after touching a device.
- **Changing a baselined value** requires the owner's confirmation and updates the baseline in the same step.
- **Restoring** rebuilds from `Current` after the owner confirms the frontend is stopped.
- **The Mac ES-DE setup** gets its first snapshot during migration: settings, custom systems, find rules, the launcher and the theme link.

### D7. Long jobs keep a run ledger on the library drive
- `onboard` and `sync` stage under `<library>/Staging/<run-id>/` with a `run.json` ledger: items, stage status, evidence paths and next step.
- Staging on the library drive saves internal disk space.
- The ledger lets a run resume after compaction or a new turn, since Codex drops a skill's instructions between turns.

### D8. Skill style
Rules for every `SKILL.md`:
- Frontmatter: `name` and `description` only.
- The description starts with what the skill does and when to use it, then says what it is not for.
- The body states the outcome, the stop rules and the done-check, and gives reasons instead of capitalised emphasis.
- The owner's instructions override the skill.
- The model is never asked to write out its reasoning.
- Questions go to the owner from the main conversation, never from a subagent.
- Bodies stay under 8,000 bytes, with detail in references.
- Shared references use the repository's `../../references/` convention. Its known ceiling: a skill installed alone, outside the plugin, loses them.
- Tests enforce the frontmatter shape, host-only patterns (`$ARGUMENTS`, `CLAUDE_SKILL_DIR`, `mcp__` tool IDs, `/gaming:` command references, model pins), capitalised emphasis words and the size cap.

### D9. Lossless migration and parity
- **Sources:**
  - the library's existing sync profile
  - the handheld project notes
  - the owner's Claude memories
  - values embedded in the three Codex skills
  - live and snapshotted frontend settings for both devices
  - the device lessons from 2026-10-09
- **Procedure:**
  1. Inventory every value.
  2. Draft the profile.
  3. Produce a migration report that maps each inventory row to a profile path, the library manifest, a snapshot, a tool reference, or "not kept: log/evidence" with a reason.
  4. The owner reviews the report.
  5. `gaming_profile.py init` writes the profile, and a re-read confirms every mapped row.
- The inventory, the report and the profile contain personal data, so they stay outside the repository.
- `parity.md` in this change maps every rule of the three replaced skills to its new home. Before release, a fresh-context reviewer compares the originals with the new plugin and must report no missing rule or effect.
- Ported scripts keep every refusal case of the originals, each covered by a test.

### D10. Permissions are printed, not applied
- Plugins cannot ship permission rules, and the owner manages security settings.
- `setup` prints the Claude user-settings entries (`additionalDirectories` plus an `Edit` allow rule for the profile folder) and the Codex `writable_roots` entry.
- It also notes that Codex asks before SSH, because its default sandbox has no network access.

### D11. Retiring the old skills
- After the plugin is installed and its skills are listed in both hosts, the Codex personal `onboard-game` and `sync-games` folders and the project `retrobackup` folder move to a dated archive folder outside any skill discovery path. Nothing is deleted.
- Their existing drive backups stay as they are.

## Risks / Trade-offs

- **The profile survives uninstall** → intended for memory. The README documents where it is and how to remove it.
- **Permission prompts until the owner adds the printed entries** → `setup` prints the entries on first run, and scripts fail with the same hint.
- **A reviewer is less thorough than seven verifiers on judgment-heavy items** → the reviewer brief lists every judgment the old verifiers covered (`parity.md`), and the scripted checks cover the mechanical ones more strictly.
- **`../../references/` breaks a standalone skill install** → accepted for consistency with butler and devlab, and revisited if single-skill installs are ever needed.
- **Codex substitution behaviour was read from source, not tested** → the design does not depend on it, because the profile path is resolved by script.

## Migration Plan

1. Build and validate the plugin on `feat/gaming-plugin`; nothing is committed without the owner's approval.
2. Install the plugin locally in both hosts, run `setup` in migration mode, review the report, and write the profile.
3. Snapshot the Mac frontend and record both baselines.
4. Run the parity review and fix any gaps.
5. Archive the old skills.

**Rollback:** the old skills come back from the archive folder, and the profile is removed by deleting its folder.
