## 1. Versioned config schema + config additions

- [x] 1.1 Create `schemas/config.schema.json` — a versioned JSON Schema for `config.yaml` (carries integer `version` = current config version = 1; `$id` + `version` like the task schemas; describes the shape incl. the new `calendar` + `breaks` blocks and `config_version`).
- [x] 1.2 Add `config_version: 1` (top) to `config.yaml`.
- [x] 1.3 Add a top-level `calendar` block to `config.yaml` (template placeholder): source + calendar names to read (default primary), with a comment that it's edited per adopter.
- [x] 1.4 Add `breaks: { lunch_min: 45, decompress_min: 30 }` under `contexts.work` (with comments: reserved as constraints, never tasks; decompress count scales to load).

## 2. Shared config preflight (versioning + migration)

- [x] 2.1 `references/template.md` → Config: document the single shared "config preflight" — read config, compare `config_version` to `schemas/config.schema.json` `version`: equal→proceed; behind→ask to migrate (apply schema defaults for new fields, bump version, proceed); ahead→error, don't run. Missing `config_version` = v0 → offer migration to v1.
- [x] 2.2 Point every skill's Config step (`intake`, `decompose`, `plan`, `reschedule`) at the shared preflight (one-line reference, not restated).

## 3. Calendar sourcing (plan / reschedule)

- [x] 3.1 `skills/plan/SKILL.md`: in the fixed-duties step, detect a Google Calendar MCP; if present, read the target day's events from `config.yaml` `calendar` calendars as fixed commitments. Persist the source in config (don't re-ask).
- [x] 3.2 Fallback ladder (non-blocking): no MCP → run calendar-blind but state it + suggest connecting one; scattered calendars → suggest consolidating to one account. Document in `references/heuristics.md` → Fixed duties.
- [x] 3.3 `skills/reschedule/SKILL.md`: read remaining commitments from the calendar the same way.

## 4. Reserve-only flexible breaks

- [x] 4.1 `skills/plan/SKILL.md`: before packing, reserve lunch (`lunch_min`) + decompress (`decompress_min`, one-or-more scaled to load) as fixed commitments placed around meetings; defer a break that would interrupt an in-progress block; NEVER create them as tasks. Adjustable/skippable.
- [x] 4.2 `references/heuristics.md` → Buffering/Time-blocking: document breaks as reserved constraints (not tasks), scale-to-load, defer-in-flow.

## 5. Fold the 0.7.0 stage-in-title cleanup

- [x] 5.1 Reconcile leftover "stage in the title prefix" / "Title = stage + short qualifier" lines to verb-first + `#stage`: `skills/intake/SKILL.md` step 4 + worked example; `references/template.md` chunk-content note + any "stage lives in the title prefix" phrasing; `references/heuristics.md` if any remain.

## 6. Realign live ING-149 tasks

- [x] 6.1 Migrate the 6 ING-149 chunk titles from `Stage: qualifier` to verb-first + a `#stage` tag (e.g. "Walk PR 2305 + UI with Rishabh" `#research`), via update_task; keep parentId/dates/status/`ai` intact; re-read to confirm.

## 7. Validate

- [x] 7.1 `config.schema.json` is valid JSON Schema and `config.yaml` validates against it (jsonschema fixture, like chunk-task).
- [x] 7.2 `claude plugin validate ./plugins/butler --strict` and `claude plugin validate . --strict`.
- [x] 7.3 `openspec validate butler-calendar-and-breaks --strict`.
- [x] 7.4 Packer + chunk-schema tests still pass (no code change). Confirm no stage-in-title residue (`rg "title.*stage|stage.*prefix"`).

## 8. Release (0.8.0)

- [x] 8.1 Bump `version` to `0.8.0` in `plugins/butler/.claude-plugin/plugin.json` AND the marketplace entry (equal).
- [x] 8.2 Update `plugins/butler/CHANGELOG.md` and root `CHANGELOG.md` with the 0.8.0 entry.
- [x] 8.3 `claude plugin tag ./plugins/butler` → `butler--v0.8.0`.
- [x] 8.4 `git push origin main && git push origin refs/tags/butler--v0.8.0`.
