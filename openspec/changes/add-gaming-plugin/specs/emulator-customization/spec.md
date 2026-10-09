## ADDED Requirements

### Requirement: Configure at the narrowest working scope

`configure` SHALL change emulator or frontend settings on a device at the narrowest scope that achieves the request (game, then content folder, then core, then global). Before writing, it SHALL take a `config` snapshot of the device and SHALL check the tool reference and official documentation. Afterwards it SHALL verify the change from the device's files and report what still needs an in-game check by the owner.

#### Scenario: Hotkeys for one core family

- **WHEN** the owner wants shoulder buttons to fast-forward without a hotkey in Game Boy cores only
- **THEN** `configure` uses core overrides for those cores
- **AND** global settings stay unchanged

#### Scenario: Setting does not stick

- **WHEN** the owner reports a setting reverting
- **THEN** `configure` explains the override and remap layering for that tool
- **AND** it identifies which file wins before proposing a fix

### Requirement: Tool knowledge is preserved in references

`references/tools/retroarch.md` SHALL carry every RetroArch and mGBA lesson mapped to it in `parity.md` (X1-X12, X23). `references/tools/es-de.md` SHALL carry every ES-DE lesson (D7-D9, L8, S8, X13-X15). Each reference SHALL include its source links and the version it was verified against.

#### Scenario: Cheat filename quirk

- **WHEN** `cheats` installs a game cheat file for RetroArch 1.21 on Android
- **THEN** it writes the file under both the full-name and the double-stripped name, as the reference describes

### Requirement: Cheats and save edits for a specific ROM revision

`cheats` SHALL:
- Identify the exact ROM revision.
- Research codes from official and community sources, using the owner's preferred research tool from the profile when available.
- Check each code against the emulator's cheat engine limits.
- Install cheat files under the names the emulator loads.
- Keep per-game tools, data and a README in `<library>/Tools/Cheats/<system>/<game>/`, mirrored by `sync`.

Save edits SHALL back up the save first, disable savestate auto-load for that game, repair checksums, and confirm no progress was lost.

#### Scenario: Owner wants items through a save edit

- **WHEN** the owner asks for items added to a save
- **THEN** `cheats` backs up the save
- **AND** it edits it with checksum repair and verifies play time is unchanged
- **AND** it records the tool in the game's tools folder

### Requirement: Skills only for non-generic work

The plugin SHALL NOT add skills for tasks a general agent handles without the owner's conventions, such as walkthroughs, level curves or evolution lookups.

#### Scenario: Owner asks for a team level curve

- **WHEN** the owner asks what level their team should be
- **THEN** no gaming skill is required for the answer
