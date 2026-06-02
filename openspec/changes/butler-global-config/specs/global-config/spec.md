# global-config

## Purpose

Define where butler's user config lives so it is machine-global (independent of
the project folder), survives plugin updates, and is never committed to the
published plugin. Grounded in the Claude Code docs: `${CLAUDE_PLUGIN_DATA}` is the
sanctioned persistent per-plugin store; `${CLAUDE_PLUGIN_ROOT}` is ephemeral and
must not hold state.

## ADDED Requirements

### Requirement: Config lives in the persistent plugin data dir

butler SHALL read its config from `${CLAUDE_PLUGIN_DATA}/config.yaml` — the persistent, update-surviving, machine-global per-plugin directory — and SHALL NOT read or write user config under `${CLAUDE_PLUGIN_ROOT}` (which is ephemeral). The path is the same regardless of which project directory Claude Code runs in.

#### Scenario: A skill reads config

- WHEN any skill (intake, decompose, plan, reschedule, setup) needs the config
- THEN it reads `${CLAUDE_PLUGIN_DATA}/config.yaml`
- AND it does not read a config from `${CLAUDE_PLUGIN_ROOT}`

#### Scenario: Config persists across a plugin update

- WHEN the plugin is updated
- THEN the config at `${CLAUDE_PLUGIN_DATA}/config.yaml` is unaffected (it lives outside the ephemeral plugin-root)

### Requirement: Missing config routes to setup

When `${CLAUDE_PLUGIN_DATA}/config.yaml` does not exist, a skill SHALL stop and direct the user to run `/butler:setup`, and SHALL NOT silently fall back to the shipped generic template (whose placeholder projects would mis-target TickTick).

#### Scenario: No config yet

- WHEN a skill runs and `${CLAUDE_PLUGIN_DATA}/config.yaml` is absent
- THEN it tells the user to run `/butler:setup` and does not proceed with planning or intake

### Requirement: The plugin ships a generic template

The plugin SHALL ship `config.example.yaml` in its root as the generic, committed template — valid against `schemas/config.schema.json`, carrying placeholder projects and the current `config_version` — used for structure/schema reference and as the starting point `/butler:setup` copies. The repo SHALL NOT contain a real user `config.yaml`.

#### Scenario: Adopter inspects the plugin

- WHEN someone reads the published plugin
- THEN they find `config.example.yaml` (generic placeholders), not a personal config
- AND no committed file contains real user projects
