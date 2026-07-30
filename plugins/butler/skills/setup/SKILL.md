---
name: setup
description: Use when the user wants to set up, configure, or reconfigure butler — "set up butler", "configure butler", "butler setup", "change my butler config", "what projects is butler using", or the first run when no config exists yet. Interviews for user-specific values and writes the host-provided persistent plugin config. Re-runnable to update individual fields.
---

# Set up butler

Write Butler's user config to its persistent plugin-data home so every skill can read
it. Resolve that home exactly as `../../references/paths.md` specifies.

## Core rules

1. **Only ever write to the resolved plugin-data `config.yaml`.** Never write real user values into the installed plugin package. The shipped `../../config.example.yaml` is a read-only template.
2. **Use the harness-substituted path, not a shell variable.** Follow `../../references/paths.md`; if neither host token resolves, stop rather than guessing.
3. **Idempotent.** If a config already exists, update only the fields the user changes; preserve everything else (including their comments). Never clobber.
4. **Confirm before writing.** Show the assembled config, get a yes, then write.
5. **Validate what you write.** A config that fails the schema is a failure, not a success.

## Config

The template + field meanings + the version-check rule are the single source:
`../../config.example.yaml` and `../../references/template.md` → Config
preflight. Ask discrete choices as native questions, open values as prose
(structured-interview convention). Keep the tone per `references/accommodations.md`.
Load deferred MCP tools (TickTick; Google Calendar) with tool_search when needed.

## Procedure

```
- [ ] 1. EXISTING CONFIG? Resolve the plugin-data directory per `../../references/paths.md`,
        then check `<resolved-plugin-data>/config.yaml`.
        - Present → UPDATE mode: read it, show current values, ask which to change
          (AskUserQuestion), edit ONLY those fields, preserve the rest. Skip to step 5.
        - Absent → first-time setup; continue.
- [ ] 2. READ THE TEMPLATE: `../../config.example.yaml` for the full
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
- [ ] 5. WRITE: using the harness-resolved plugin-data path from step 1
        (rule 2 — never the bare shell var), create that data dir, then write
        `<resolved>/config.yaml` from the template + answers. Set `config_version` to the
        schema's `configVersion`. In UPDATE mode, apply targeted edits, not a rewrite.
- [ ] 6. VALIDATE: check the written file against `../../schemas/config.schema.json`
        and assert `config_version` == `configVersion`. On failure, surface it and fix;
        do NOT report success on a bad write.
- [ ] 7. DONE: confirm butler is configured and point to `/butler:plan` (or `/butler:intake`).
```

## References

- `../../references/paths.md` — host-neutral package and data path resolution.
- `../../config.example.yaml` — the template (every field + comments).
- `../../schemas/config.schema.json` — the shape to validate against.
- `../../references/template.md` — Config preflight (the version-check rule).
- `../../references/accommodations.md` — tone.
