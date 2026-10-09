## ADDED Requirements

### Requirement: Every device frontend has a recorded baseline

Each device in the profile that runs a frontend SHALL record a baseline: the deliberately chosen settings with their values, the theme and variant, collection presentation, custom systems or launch rules, and whether writes require stopped-frontend confirmation. The full current files SHALL be kept in `<library>/Frontends/<app>/<device>/Current/`.

#### Scenario: Mac frontend has no snapshot yet

- **WHEN** migration finds a device frontend with no library snapshot
- **THEN** a snapshot is captured into `Current/`
- **AND** its baseline is recorded before migration completes

### Requirement: Drift check before and after device changes

`scripts/esde_baseline.py check` SHALL compare a frontend settings file with the device baseline. It SHALL list every baselined key whose value differs or is missing, and exit non-zero on drift. `configure`, `sync` and `backup` SHALL run it before and after touching a device's frontend.

#### Scenario: Setting changed outside the plugin

- **WHEN** the theme variant on a device no longer matches the baseline
- **THEN** the check reports the key, the expected value and the found value
- **AND** the skill asks the owner whether to restore the baseline or adopt the new value

### Requirement: Baseline changes are deliberate

A baselined value SHALL change only with the owner's confirmation. The baseline update SHALL happen in the same step as the device change. Onboarding and sync SHALL NOT change frontend appearance.

#### Scenario: Owner changes the startup system

- **WHEN** the owner asks `configure` to change the frontend's startup system
- **THEN** the device setting and the baseline are updated together after confirmation

### Requirement: Rebuild from the baseline

The plugin SHALL support rebuilding a device's frontend setup from `Current/` and the baseline. The owner SHALL first confirm the frontend is stopped. The rebuild SHALL re-read and rebase live gamelists to keep play history, and SHALL take a recovery snapshot first.

#### Scenario: Restore after a reinstall

- **WHEN** a device's frontend was reinstalled with default settings
- **THEN** `configure` restores baselined settings, theme, collections and launch rules from the library
- **AND** it verifies them with the drift check
