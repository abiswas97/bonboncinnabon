## ADDED Requirements

### Requirement: The config has a versioned schema

`config.yaml` SHALL carry a top-level integer `config_version`, and the plugin SHALL
define the config shape and its current version in a versioned
`schemas/config.schema.json` (parallel to the task schemas). The schema version is the
single source of truth for "current"; `config_version` bumps whenever the config shape
changes in a way that needs migration.

#### Scenario: Config and schema both carry a version

- **WHEN** the plugin ships
- **THEN** `config.yaml` has a `config_version` and `schemas/config.schema.json` declares the current config version and shape

### Requirement: Config version is checked on every read

Every skill that reads `config.yaml` SHALL first compare the installed `config_version`
to the plugin's current schema version, using a single shared check, before using the
config:

- **equal** → proceed.
- **behind** (installed < current) → tell the user the config is out of date and ASK
  whether to migrate; on yes, apply the new schema's defaults for any added fields,
  bump `config_version`, then proceed; on no, proceed with a stated caveat or stop.
- **ahead** (installed > current) → surface an ERROR (the config is newer than the
  plugin — this shouldn't happen; e.g. a downgraded plugin) and do NOT silently run.

#### Scenario: Up-to-date config proceeds

- **WHEN** the installed `config_version` equals the plugin's current version
- **THEN** the skill proceeds without prompting

#### Scenario: Out-of-date config offers migration

- **WHEN** the installed `config_version` is behind the current version
- **THEN** the skill tells the user and asks to migrate; on confirmation it applies defaults for new fields, bumps `config_version`, and proceeds

#### Scenario: Config newer than the plugin errors

- **WHEN** the installed `config_version` is ahead of the plugin's current version
- **THEN** the skill surfaces an error and does not silently run
