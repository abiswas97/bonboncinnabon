## Why

butler reads its config from `${CLAUDE_PLUGIN_ROOT}/config.yaml`. That is wrong on
two counts, confirmed against the live Claude Code docs:

1. **`${CLAUDE_PLUGIN_ROOT}` is ephemeral** — the docs say "treat it as ephemeral and do not write state here"; it is wiped ~7 days after a plugin update. A user's config there silently vanishes on update.
2. **It couples personal data to the published plugin.** The config file lives in the repo we publish, so there is no place for real TickTick projects that isn't committed (the exact tension 0.7.1 scrubbed).

The user needs ONE machine-global config, the same regardless of which project
folder Claude Code is launched from, never committed. The blessed, documented home
is **`${CLAUDE_PLUGIN_DATA}`** — "a persistent directory for plugin state that
survives updates," created on first reference, and inline-substituted in SKILL.md
exactly like `CLAUDE_PLUGIN_ROOT`. Real plugins (`amcheste/ea-agent`,
`robertnowell/video-essay`) use precisely this shape: a re-runnable `/setup` command
that interviews the user and writes a versioned config into the persistent data dir.

## What Changes

- **Config moves to `${CLAUDE_PLUGIN_DATA}/config.yaml`** — persistent, survives updates, machine-global, never in the repo. **BREAKING**: the config location changes (anyone who hand-edited the in-plugin file re-runs setup).
- **The in-repo `config.yaml` becomes `config.example.yaml`** — the generic template shipped for structure + schema reference, and the starting point `/butler:setup` copies. The plugin no longer reads a config from its own root.
- **New `/butler:setup` skill** — interviews the user (timezone, planning project, work projects + default, personal projects, calendar source/calendars, work window, optional breaks/pacing overrides), `mkdir -p "$CLAUDE_PLUGIN_DATA"`, writes `config.yaml` there at the current `config_version`, validates against the schema. Idempotent: re-running offers to update individual fields, never clobbers.
- **Config-read changes** (the shared preflight + all four skills): read `${CLAUDE_PLUGIN_DATA}/config.yaml`; if absent, STOP and tell the user to run `/butler:setup` — no silent fallback to the generic template (its placeholder projects would mis-target TickTick).

No packer code change.

## Capabilities

### New Capabilities
- `global-config`: where butler's config lives (`${CLAUDE_PLUGIN_DATA}`), the read + missing-config behavior, and the shipped generic template.
- `setup-skill`: the `/butler:setup` interview that writes and updates the global config.

### Modified Capabilities
- (none at the requirement level — the version check from `config-versioning` and the scheduling behavior are unchanged; only the file location they operate on moves, which the new `global-config` capability defines.)

## Impact

- Rename `plugins/butler/config.yaml` → `plugins/butler/config.example.yaml`.
- New `plugins/butler/skills/setup/SKILL.md`.
- Update every `${CLAUDE_PLUGIN_ROOT}/config.yaml` reference → `${CLAUDE_PLUGIN_DATA}/config.yaml` in `skills/{intake,decompose,plan,reschedule}/SKILL.md` and the `references/template.md` Config preflight (point at the new location + the run-setup-if-absent rule).
- `README.md`: document the global config location + `/butler:setup`.
- `schemas/config.schema.json` stays in plugin root (read for validation).
- Release: 0.10.0.
