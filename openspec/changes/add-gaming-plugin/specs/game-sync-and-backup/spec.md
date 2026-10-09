## ADDED Requirements

### Requirement: Sync workflow parity

`sync` SHALL carry every rule mapped to it in `parity.md`:
- read-only discovery and a concrete change set before writing
- additive copies only
- conflicts preserved before any replacement
- no save merging, timestamp winners or mirrored deletions
- collection upkeep under the profile's policy
- frontend writes only after the owner confirms the frontend is stopped
- separate evidence for local copies, cloud presence, cloud bytes and runtime

#### Scenario: Divergent save on two targets

- **WHEN** a save differs between the library and a device
- **THEN** `sync` keeps both versions
- **AND** it asks the owner which is authoritative
- **AND** it does not pick the newer timestamp

#### Scenario: Cloud mirror only

- **WHEN** files have been copied to a cloud desktop mirror but server presence is unverified
- **THEN** the report says local staging only
- **AND** it does not claim a verified cloud backup

### Requirement: sync_tree behaviour parity

`scripts/sync_tree.py` SHALL keep every effect T1-T9 in `parity.md`, each covered by a test:
- refuses symlinked directories, non-regular files, unfinished-operation markers and overlapping roots
- plans by default, and writes only with `--apply`
- copies through a temporary file with hash checks
- preserves conflicts only when asked
- reports cloud flags as unverified

#### Scenario: Conflict without preservation flag

- **WHEN** a destination file differs and `--preserve-conflicts` is absent
- **THEN** the script exits non-zero
- **AND** the destination is unchanged

### Requirement: Backup is a read-only device snapshot

`backup` SHALL snapshot a device into `<library>/Recovery/<device>/<timestamp>/` without launching, stopping or reconfiguring anything on it. It offers two scopes:
- `config`: the emulator and frontend configuration files
- `full`: adds the frontend tree, installed ROMs, BIOS, saves and states at the configured paths

`scripts/snapshot.py` SHALL keep effects B1-B14 in `parity.md`, each covered by a test where it can run locally. Success SHALL mean only a manifest with `status: verified`.

#### Scenario: Files change during capture

- **WHEN** a source file changes between the before and after inventories
- **THEN** the archive is kept under `Staging/snapshots/`, marked incomplete, and reported as not verified
- **AND** nothing is added to `Recovery/`

#### Scenario: Library drive not mounted

- **WHEN** the library root is not a mounted volume
- **THEN** the script stops without creating any folder

### Requirement: Secrets stay opaque

Scripts and skills SHALL NOT print, log or copy into notes the contents of configuration files that may hold credentials. Snapshot manifests SHALL record only paths, sizes and hashes.

#### Scenario: SSH command fails

- **WHEN** a remote read fails
- **THEN** the error states the failed step and connection hints from the profile
- **AND** it does not echo command output
