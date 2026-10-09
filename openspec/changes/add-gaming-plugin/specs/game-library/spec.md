## ADDED Requirements

### Requirement: Canonical system-first layout

The plugin SHALL document one library layout in `references/library-layout.md`:
- `ROMs/<system>/`
- `Media/<system>/<category>/<ROM stem>.<ext>`
- `Documents/<system>/<ROM stem>/{In Box,Guides,Documentation}/`
- `BIOS/`
- `Archives/<system>/`
- `Frontends/<app>/<device>/{Current,Prepared}/`
- `Recovery/<device>/<timestamp>/`
- `Staging/<run-id>/`
- `Tools/` (including `Tools/Cheats/<system>/<game>/` and `Tools/profile.json`)
- `library-manifest.json`

The library root SHALL come from the profile. Multi-file games SHALL keep one canonical folder per game, and the manifest SHALL record their constituent files.

#### Scenario: New platform

- **WHEN** the owner adds a first Switch game
- **THEN** it is placed under `ROMs/switch/<game folder>/`
- **AND** the manifest lists base, update and DLC files
- **AND** no skill text changes are needed

### Requirement: Onboard workflow parity

`onboard` SHALL carry every rule mapped to it in `parity.md`:
1. Resolve identity and scope.
2. Acquire and verify the game.
3. Prepare artwork.
4. Prepare original documents.
5. Publish to the library.
6. Install only with opt-in.
7. Refresh collections and enabled targets.

Storage-only SHALL be the default, and installation SHALL require explicit or standing opt-in.

#### Scenario: Name only, no install request

- **WHEN** the owner asks to add a game without asking for installation, and no standing opt-in exists for any device
- **THEN** `onboard` prepares the library package only
- **AND** it makes no device writes

#### Scenario: Repeat invocation

- **WHEN** `onboard` runs again for an already-onboarded game
- **THEN** it reuses verified files, fills gaps, and neither duplicates nor silently replaces anything

### Requirement: Scripted checks before reliance

Mechanical facts SHALL be established by bundled scripts that exit non-zero with a reason on failure:
- hash identity against a reference catalogue (DAT) file
- size and presence
- path and name collisions
- image header sanity
- archive members
- manifest consistency
- source stability during copy

Work that depends on a failed check SHALL stop until it is fixed and rechecked.

#### Scenario: Hash mismatch

- **WHEN** a prepared ROM's hash is absent from the selected DAT
- **THEN** the ROM is not published as that edition
- **AND** the ledger records the mismatch

### Requirement: One fresh-context reviewer at irreversible steps

Before publishing to the library and before installing on a device, the skill SHALL ask the host for a subagent with no conversation history. The subagent receives only the request, raw paths and `references/reviewer.md`, and it reviews the judgment calls listed there without modifying files. If the host cannot provide one, the skill SHALL stage and report only.

#### Scenario: Host without subagents

- **WHEN** the host cannot start an isolated subagent
- **THEN** `onboard` stops after staging
- **AND** it reports that review is pending

### Requirement: Run ledger on the library drive

`onboard` and `sync` SHALL stage under `<library>/Staging/<run-id>/` and keep `run.json`, which records items, stage status, evidence paths and the next step. A new turn or a compacted session SHALL resume from the ledger.

#### Scenario: Resume after interruption

- **WHEN** a 13-game onboarding stops after 5 games
- **THEN** the next invocation reads `run.json` and continues with game 6 without redoing verified work

### Requirement: Platform knowledge is data and references

Skills SHALL NOT hard-code emulator, frontend or device names. Devices SHALL declare emulators per system in the profile. Tool knowledge SHALL live in `references/tools/<tool>.md` and be read only when the active device declares that tool. BIOS, firmware and keys SHALL only come from the owner's files.

#### Scenario: Device without RetroArch

- **WHEN** a device's profile maps `ps2` to PCSX2
- **THEN** skills working on that device do not read the RetroArch reference

### Requirement: Parity with the replaced skills is proven before release

Together, the plugin's skills, references, scripts and the migrated profile SHALL produce every effect and carry every piece of knowledge of the replaced `onboard-game`, `sync-games` and `retrobackup` skills, plus the lessons listed in `parity.md`. Before release:
- A fresh-context reviewer SHALL compare the original skill files with the new plugin and the migration report, row by row, and SHALL report any missing rule, effect or value.
- Every reported gap SHALL be fixed and re-reviewed.
- The only accepted deviation SHALL be the owner-approved verification model (scripted checks plus one reviewer).

#### Scenario: Rule dropped in the rewrite

- **WHEN** the parity review finds an original rule with no home in the new plugin
- **THEN** release is blocked until the rule is added and the review passes again
