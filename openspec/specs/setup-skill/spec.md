# setup-skill Specification

## Purpose

A re-runnable `/butler:setup` command that writes and maintains the global config
at `${CLAUDE_PLUGIN_DATA}/config.yaml`, so a user (or adopter) can configure butler
without hand-editing files inside the plugin.

## Requirements

### Requirement: setup interviews and writes the global config

`/butler:setup` SHALL interview the user for the user-specific values (timezone, planning project, work projects + default project, personal projects, calendar source + calendars, work window, and optional breaks/pacing overrides), then `mkdir -p "$CLAUDE_PLUGIN_DATA"` and write `${CLAUDE_PLUGIN_DATA}/config.yaml` starting from `config.example.yaml`, set to the current `config_version`. It SHALL confirm the values before writing.

#### Scenario: First-time setup

- **WHEN** the user runs `/butler:setup` with no existing config
- **THEN** it interviews for the values, confirms, creates the data dir, and writes `${CLAUDE_PLUGIN_DATA}/config.yaml` at the current `config_version`

### Requirement: setup validates what it writes

`/butler:setup` SHALL validate the written config against `schemas/config.schema.json` and confirm `config_version` equals the schema's `configVersion` before reporting success.

#### Scenario: Written config is checked

- **WHEN** setup writes the config
- **THEN** it validates against the schema and surfaces any failure rather than reporting success

### Requirement: setup is idempotent

When `${CLAUDE_PLUGIN_DATA}/config.yaml` already exists, `/butler:setup` SHALL read it, show current values, and offer to update individual fields — it SHALL NOT clobber the whole file or silently overwrite unrelated settings.

#### Scenario: Re-running setup

- **WHEN** the user runs `/butler:setup` with an existing config
- **THEN** it shows current values and updates only the fields the user changes, preserving the rest
