## Context

Config must move off the ephemeral `${CLAUDE_PLUGIN_ROOT}` (wiped on update, and in
the published repo) to a persistent, machine-global, never-committed home. The
research (claude-code-guide + GitHub survey + live docs) settled the location.

## Decisions

### Location: `${CLAUDE_PLUGIN_DATA}`, not a hand-rolled `~/.claude/butler/`
The docs define `${CLAUDE_PLUGIN_DATA}` as "a persistent directory for plugin state
that survives updates," created on first reference, and it is **inline-substituted
in SKILL.md** like `CLAUDE_PLUGIN_ROOT`. So `Read ${CLAUDE_PLUGIN_DATA}/config.yaml`
works directly in skill prose — no `$HOME` resolution gymnastics. It is per-plugin
and machine-wide (resolves the same in every project dir), which satisfies the
"global across the computer" requirement. A hand-rolled `~/.claude/butler/` path was
rejected: the `~/.claude/` directory reference enumerates its contents and has no
per-plugin config dir, so that path is unsanctioned; real plugins use
`${CLAUDE_PLUGIN_DATA}` (often via the `${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/<name>}`
fallback idiom). We rely on the **variable**, never the literal on-disk path (the
exact resolution is convention, not a documented contract).

### Why not `userConfig` in plugin.json
`userConfig` is the blessed mechanism for flat scalars/secrets and prompts on enable,
but it only holds flat values (`string`/`number`/`boolean`/`directory`/`file`) stored
in settings.json. butler's config is a nested blob (contexts, pipeline, capacity,
pacing, breaks) that `userConfig` cannot represent. butler also has no API token of
its own (TickTick/Linear/Calendar auth via their MCP servers). So butler uses the
rich-file-in-`${CLAUDE_PLUGIN_DATA}` pattern (the ea-agent shape) and skips
`userConfig` entirely.

### Template vs live config
The repo ships `config.example.yaml` (generic placeholders, valid against the schema,
current `config_version`). `/butler:setup` reads it as the structural starting point,
fills in the user's answers, and writes `${CLAUDE_PLUGIN_DATA}/config.yaml`. The repo
never contains a real config. The schema stays at `${CLAUDE_PLUGIN_ROOT}/schemas/`
(plugin code, read for validation — fine to be ephemeral, it ships with the plugin).

### Missing-config behavior: route to setup, no silent fallback
If `${CLAUDE_PLUGIN_DATA}/config.yaml` is absent, skills stop and say "run
`/butler:setup`". Falling back to `config.example.yaml` would point planning at
placeholder TickTick projects that don't exist — worse than stopping.

### Writing from a skill — use the substituted path, not the shell var
The reliable mechanism is the harness substituting `${CLAUDE_PLUGIN_DATA}` with
butler's own data dir **inline in the skill text** (exactly how butler's existing
`${CLAUDE_PLUGIN_ROOT}` refs already resolve). `/butler:setup` uses that resolved
literal path for `mkdir -p` and the Write. It must NOT trust the `$CLAUDE_PLUGIN_DATA`
**shell variable** in a bare Bash subprocess: empirically that env var can reflect a
*different* plugin's data dir (observed pointing at another plugin during
development), because the subprocess inherits whatever plugin context spawned it. The
skill carries an explicit guard: if `${CLAUDE_PLUGIN_DATA}` ever appears unsubstituted
(literal braces), stop and ask rather than guess. Idempotent updates: read existing →
show values → targeted Edit of changed fields only (preserve hand-edits/comments).

## Risks / trade-offs

- **Breaking move.** Anyone who edited the in-plugin `config.yaml` loses it on this upgrade. Mitigation: the missing-config path tells them to run `/butler:setup`; the CHANGELOG calls it out. Acceptable — the plugin is early (0.x) and the old location was buggy anyway.
- **`${CLAUDE_PLUGIN_DATA}` literal path is convention.** We never hardcode it; always reference the variable. If a future Claude Code changes the resolution, butler still works.
- **Version-check preflight unchanged in behavior.** It still compares `config_version` to the schema's `configVersion`; only the file it reads moved. No `config-versioning` requirement changes.

## Migration

The config location moves; there is no in-place data migration (the old file was
ephemeral and generic). On first run after upgrade, a user with no
`${CLAUDE_PLUGIN_DATA}/config.yaml` is routed to `/butler:setup`. The 0.9.0
`config_version` (2) and schema are carried into the example unchanged.
