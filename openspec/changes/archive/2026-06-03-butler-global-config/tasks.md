## 1. Move config to the persistent data dir

- [x] 1.1 `git mv plugins/butler/config.yaml plugins/butler/config.example.yaml` (the generic template; keep placeholder projects + `config_version: 2`).
- [x] 1.2 `references/template.md` → Config preflight: change the read target from `${CLAUDE_PLUGIN_ROOT}/config.yaml` to `${CLAUDE_PLUGIN_DATA}/config.yaml`; add the missing-config rule (absent → tell the user to run `/butler:setup`, do NOT fall back to the example); note the example is the template `/butler:setup` copies.
- [x] 1.3 Update the Config step in `skills/{intake,decompose,plan,reschedule}/SKILL.md`: read `${CLAUDE_PLUGIN_DATA}/config.yaml`; if absent → run `/butler:setup`. One-line change each, still pointing at the preflight for the version check.

## 2. The /butler:setup skill

- [x] 2.1 Create `skills/setup/SKILL.md` (name: `setup`; description triggers on "set up butler", "configure butler", "butler setup", first-run). Procedure: read `config.example.yaml` for structure; interview for timezone, planning_project, work projects + default_project, personal projects, calendar source + calendars, work_window, optional breaks + pacing overrides (use AskUserQuestion for discrete choices per the structured-interview convention); confirm; `mkdir -p "$CLAUDE_PLUGIN_DATA"`; Write `${CLAUDE_PLUGIN_DATA}/config.yaml` at the current `config_version`.
- [x] 2.2 Idempotency: if `${CLAUDE_PLUGIN_DATA}/config.yaml` exists, read it, show current values, update only changed fields (targeted edits), preserve the rest.
- [x] 2.3 Validation: after writing, validate against `${CLAUDE_PLUGIN_ROOT}/schemas/config.schema.json` and assert `config_version` == `configVersion`; surface any failure instead of reporting success.
- [x] 2.4 Reference the existing single sources (don't restate): template.md → Config preflight, structured-interview convention, accommodations tone.

## 3. Docs

- [x] 3.1 `README.md`: document that config is global at `${CLAUDE_PLUGIN_DATA}/config.yaml`, set up via `/butler:setup`; the in-repo `config.example.yaml` is the template. Remove any "edit config.yaml in the plugin" guidance.
- [x] 3.2 Grep the plugin for stray `${CLAUDE_PLUGIN_ROOT}/config.yaml` or "config.yaml" references that should now be the data-dir path or the example; reconcile.

## 4. Validate

- [x] 4.1 `openspec validate butler-global-config --strict`.
- [x] 4.2 `claude plugin validate ./plugins/butler --strict` and `claude plugin validate . --strict`.
- [x] 4.3 `config.example.yaml` validates against `config.schema.json` (jsonschema fixture); config_version (2) == configVersion (2).
- [x] 4.4 Packer + chunk-schema tests still pass (no code change).
- [x] 4.5 Grep: no remaining `${CLAUDE_PLUGIN_ROOT}/config.yaml` read target anywhere in skills/references; the only `config.yaml` in the repo is `config.example.yaml`.

## 5. Release (0.10.0)

- [x] 5.1 Bump `version` to `0.10.0` in `plugins/butler/.claude-plugin/plugin.json` AND the marketplace entry (equal). Schema `version` → 0.10.0 (configVersion stays 2).
- [x] 5.2 Update `plugins/butler/CHANGELOG.md` and root `CHANGELOG.md` (call out the BREAKING config-location move + `/butler:setup`).
- [x] 5.3 `claude plugin tag ./plugins/butler` → `butler--v0.10.0`.
- [x] 5.4 `git push origin main && git push origin refs/tags/butler--v0.10.0`.
- [x] 5.5 Archive + sync specs (global-config + setup-skill new).

## 6. Set up the real config

- [ ] 6.1 Run `/butler:setup` with the user's real values → write `${CLAUDE_PLUGIN_DATA}/config.yaml`. Confirm a skill (e.g. a dry plan read) sees it.
