---
name: setup
description: Use when the user wants to set up, configure, or reconfigure butler — "set up butler", "configure butler", "butler setup", "change my butler config", "what projects is butler using", or the first run when no config exists yet. Interviews for the user-specific values and writes the global config at ${CLAUDE_PLUGIN_DATA}/config.yaml. Re-runnable to update individual fields.
---

# Set up butler

Write butler's user config to its global, machine-wide home so every skill can read
it. The config lives at **`${CLAUDE_PLUGIN_DATA}/config.yaml`** — persistent across
plugin updates, the same in every project, and never committed to the plugin repo.

## Core rules

1. **Only ever write to `${CLAUDE_PLUGIN_DATA}/config.yaml`.** Never write real user values into the plugin repo (`${CLAUDE_PLUGIN_ROOT}` is ephemeral and published). The shipped `config.example.yaml` is a read-only template.
2. **Use the harness-substituted path, NOT the shell variable.** Claude Code substitutes `${CLAUDE_PLUGIN_DATA}` with butler's own data dir directly in this skill's text — use that resolved literal path for every read/write/`mkdir`. Do NOT rely on `$CLAUDE_PLUGIN_DATA` inside a Bash subprocess: in a bare shell it can reflect a *different* plugin's dir. If you ever see the literal unsubstituted string `${CLAUDE_PLUGIN_DATA}` (braces intact), stop and tell the user rather than guessing a path.
3. **Idempotent.** If a config already exists, update only the fields the user changes; preserve everything else (including their comments). Never clobber.
4. **Confirm before writing.** Show the assembled config, get a yes, then write.
5. **Validate what you write.** A config that fails the schema is a failure, not a success.

## Config

The template + field meanings + the version-check rule are the single source:
`${CLAUDE_PLUGIN_ROOT}/config.example.yaml` and `references/template.md` → Config
preflight. Ask discrete choices as native questions, open values as prose
(structured-interview convention). Keep the tone per `references/accommodations.md`.
Load deferred MCP tools (TickTick; Google Calendar) with tool_search when needed.

## Procedure

```
- [ ] 1. EXISTING CONFIG? Check `${CLAUDE_PLUGIN_DATA}/config.yaml`.
        - Present → UPDATE mode: read it, show current values, ask which to change
          (AskUserQuestion), edit ONLY those fields, preserve the rest. Skip to step 5.
        - Absent → first-time setup; continue.
- [ ] 2. READ THE TEMPLATE: `${CLAUDE_PLUGIN_ROOT}/config.example.yaml` for the full
        shape, comments, and the current `config_version`.
- [ ] 3. INTERVIEW for the user-specific values (offer sensible defaults from the
        template; only the project names + timezone truly must be answered):
          - timezone (IANA, e.g. America/New_York) [open].
          - TickTick projects: optionally read `list_projects` to show the user their
            REAL lists, then map which are WORK (`contexts.work.projects` + a
            `default_project` that is one of them) and which are PERSONAL
            (`contexts.personal.projects`) [choice from live lists].
          - planning_project: the list the daily planning ritual lives in [choice/open].
          - calendar: `source` (google | none) [choice]; if google, which `calendars`
            (default `[primary]`) [open].
          - work_window `start`/`end` (local time) [open].
          - Optional tuning — offer "keep defaults or customize?" [choice]; only on
            customize, ask about `breaks` (lunch_min/decompress_min), `pacing`
            (window/streak/quantile/recovery), or `capacity`. Defaults come from the template.
- [ ] 4. CONFIRM the assembled config with the user (show it).
- [ ] 5. WRITE: using the harness-RESOLVED `${CLAUDE_PLUGIN_DATA}` path from this skill
        (rule 2 — never the bare shell var), `mkdir -p` that data dir, then write
        `<resolved>/config.yaml` from the template + answers. Set `config_version` to the
        schema's `configVersion`. In UPDATE mode, apply targeted edits, not a rewrite.
- [ ] 6. VALIDATE: check the written file against `${CLAUDE_PLUGIN_ROOT}/schemas/config.schema.json`
        and assert `config_version` == `configVersion`. On failure, surface it and fix;
        do NOT report success on a bad write.
- [ ] 7. DONE: confirm butler is configured and point to `/butler:plan` (or `/butler:intake`).
```

## References

- `${CLAUDE_PLUGIN_ROOT}/config.example.yaml` — the template (every field + comments).
- `${CLAUDE_PLUGIN_ROOT}/schemas/config.schema.json` — the shape to validate against.
- `${CLAUDE_PLUGIN_ROOT}/references/template.md` — Config preflight (the version-check rule).
- `${CLAUDE_PLUGIN_ROOT}/references/accommodations.md` — tone.
