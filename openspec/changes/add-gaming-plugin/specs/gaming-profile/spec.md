## ADDED Requirements

### Requirement: One shared profile outside both hosts

The gaming plugin SHALL keep its user profile at `$XDG_CONFIG_HOME/bonboncinnabon/gaming/profile.json` when `XDG_CONFIG_HOME` is set to an absolute path, and at `~/.config/bonboncinnabon/gaming/profile.json` otherwise. Claude Code and Codex SHALL resolve the same file. The plugin SHALL NOT store the profile in a host plugin-data directory or inside the installed package.

#### Scenario: Both hosts read the same profile

- **WHEN** a gaming skill runs in Claude Code and later in Codex on the same machine
- **THEN** both resolve the path through `scripts/gaming_profile.py path`
- **AND** both read the same file

#### Scenario: Relative XDG value

- **WHEN** `XDG_CONFIG_HOME` is set to a relative path
- **THEN** the resolver ignores it and uses `~/.config`

### Requirement: Script-owned, validated, recoverable writes

Only `scripts/gaming_profile.py` SHALL write the profile. Every write SHALL validate the full result, copy the previous file to `history/profile-<UTC timestamp>.json`, and replace the file atomically. `--dry-run` SHALL show the change without writing. An invalid result SHALL leave the file unchanged and exit non-zero with the failing field.

#### Scenario: Agent records a learned fact

- **WHEN** a skill learns a durable device fact
- **THEN** it shows the owner the note
- **AND** it calls `gaming_profile.py note <device> <text>`
- **AND** a history copy of the previous profile exists

#### Scenario: Invalid update

- **WHEN** an update would remove a required field or set a wrong type
- **THEN** the profile is unchanged
- **AND** the script names the field and exits non-zero

### Requirement: Profile contents and limits

The profile SHALL hold:
- schema version and timezone
- libraries with extra search sources
- backup targets with scope and verification rules
- devices, each with connection method and SSH alias, connection hints, storage paths, a per-system emulator map, emulator config paths, frontend baseline, install opt-in and dated notes
- collection policy
- policies
- preferences

Each device SHALL keep at most 50 notes. Logs and verification evidence SHALL NOT be stored in the profile.

#### Scenario: Note cap reached

- **WHEN** a device already has 50 notes and a new note is added
- **THEN** the script refuses and asks for an existing note to be merged or removed

### Requirement: No credentials in the profile

The profile SHALL NOT contain passwords, tokens, private keys or account secrets. Connection details SHALL be SSH aliases or local paths. Validation SHALL reject keys or values that look like credentials.

#### Scenario: Secret-looking field

- **WHEN** an update adds a key named like `password` or `token`
- **THEN** validation fails and nothing is written

### Requirement: Missing profile routes to setup

When the profile does not exist, every skill except `setup` SHALL stop and direct the owner to the `setup` skill. Skills SHALL NOT fall back to the shipped example profile.

#### Scenario: First run of onboard

- **WHEN** `onboard` runs before any profile exists
- **THEN** it tells the owner to run `setup` and makes no changes

### Requirement: Setup is interview-light and prints permissions

`setup` SHALL:
- First import what existing sources already provide (a previous sync profile, SSH host aliases, existing frontend settings).
- Ask only for missing values, in one batch, from the main conversation.
- Show the assembled profile before writing.
- Test each device's connection read-only.
- Print, without applying, the Claude Code settings entries and the Codex `writable_roots` entry the owner needs to grant write access to the profile folder.

#### Scenario: Re-running setup to add a device

- **WHEN** the owner runs `setup` to add a device
- **THEN** existing values are preserved
- **AND** only the new device's fields are asked for
- **AND** the change is shown before writing

### Requirement: Lossless migration

Migration from existing sources SHALL produce a migration report. The report SHALL map every inventoried value to exactly one destination (profile path, library manifest, library snapshot, tool reference, or "not kept: log or evidence" with a reason). The owner SHALL approve the report before the profile is written. After writing, each mapped value SHALL be read back and confirmed. Source files SHALL NOT be modified or removed by migration.

#### Scenario: Unmapped value

- **WHEN** an inventoried value has no destination
- **THEN** migration stops and lists it for the owner

### Requirement: Profile copy in the library

`sync` and `backup` SHALL copy the current profile to `<library>/Tools/profile.json` after a successful run. The `~/.config` file SHALL remain the source of truth.

#### Scenario: Restoring the profile on a new machine

- **WHEN** the owner sets up a new machine with the library attached
- **THEN** `setup` offers to import `<library>/Tools/profile.json`
