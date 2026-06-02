## 1. Config foundation (task-contexts)

- [x] 1.1 Add a `contexts` block to `plugins/butler/config.yaml` with `work` and `personal` entries, each declaring `projects`, `decomposition`, `axes`, `scheduling` (per design D1).
- [x] 1.2 Populate `contexts.work.projects` with `Plate` and `Promo Track` (D9); `contexts.personal.projects` with `Life, Photo, Finance, Relationships, Medical, Projects`.
- [x] 1.3 Fold work scheduling config under `contexts.work`: move `work_window`, `pipeline`, `capacity`, `intensity_tags`, `recharge_tag`, `executes_with_ai`, `points_calibration` inside, and rename `work_project` → `contexts.work.default_project` with a comment that it MUST be a member of `contexts.work.projects` (D1, refined: work-only keys also fold under work).
- [x] 1.4 Keep genuinely cross-context infrastructure top-level: `planning_project`, `priority_tags`, `ai_tag`, `parked_tag`, `ritual`, `timezone` (D1). No `default_reminder` key — personal time is asked, then agent-derived on defer (D5).
- [x] 1.5 Update every config read path (`intake`, `plan`, `reschedule`, and the references) from top-level keys to `contexts.work.*`; confirmed `scripts/pack_schedule.py` reads only `input.json`/stdin + the embedded `config` block (never `config.yaml`), so it is untouched (D1). Verified no stale `work_project` references remain.

## 2. Schema (chunk-task)

- [x] 2.1 Add `context` enum `[work, personal]` to `schemas/chunk-task.schema.json` properties with a clear description.
- [x] 2.2 Add an optional `reminder` property (object: `due` date-time + `trigger` string, date-anchored) to the schema.
- [x] 2.3 Replace the flat `required` with base `[id, title, context, kind, ai_generated]` + `if context==work then required [stage, intensity, ai_discount, est0_min]` (D3); keep `additionalProperties: false`.
- [x] 2.4 Hand-validate three fixtures against the schema (jsonschema 4.26, Draft202012): valid work chunk PASS, work chunk missing `stage` FAILS, valid personal chunk with no work axes PASS.

## 3. Shared references

- [x] 3.1 `references/heuristics.md`: add the context-resolution rule (derive-by-project → confirm → unmapped asks) used by both `decompose` and `plan` (D2).
- [x] 3.2 `references/heuristics.md`: add personal decomposition guidance (2–4 free-form steps OR none; default to not over-shredding) and light scheduling (time + reminder, no packer) (D4).
- [x] 3.3 `references/interview.md`: add a "Decompose" question bank and a hard-gate "do not proceed until X" red-flags block shared by intake + decompose (interview-gate spec).
- [x] 3.4 `references/task-contract.md`: state the contract applies to ALL contexts; personal titles follow it without the `stage:` prefix (task-contexts spec).
- [x] 3.5 `references/template.md`: add the personal field mapping (dueDate + reminders TRIGGER, `ai` tag, no `focusSummaries`/intensity); add the missing-context-is-work read rule (D7).

## 4. intake hard gate (interview-gate)

- [x] 4.1 Edit `skills/intake/SKILL.md`: promote the interview (step 3) into an explicit hard gate with a red-flags "do not proceed until intent / prior progress / shape confirmed" block.
- [x] 4.2 Edit `skills/intake/SKILL.md`: set `context: work` on intake-created chunks and reference the context model. (Also disambiguated intake's trigger description from decompose: intake = NEW work, decompose = existing TickTick task.)

## 5. decompose skill (decompose-skill)

- [x] 5.1 Create `skills/decompose/SKILL.md` with frontmatter (name, triggers-only description for "break down / decompose / scope an existing TickTick task").
- [x] 5.2 Implement resolve step: title search + confirm match, OR list undecomposed candidates (no `childIds`) and let the user pick.
- [x] 5.3 Implement derive-and-confirm context step (calls the shared rule from 3.1).
- [x] 5.4 Implement augment-if-already-split: read existing chunks, discuss gaps, add only new chunks (no duplicates).
- [x] 5.5 Wire the hard-gate interview before any decomposition (references 3.3).
- [x] 5.6 Implement context-aware decomposition: work → pipeline stages; personal → free-form steps or no decomposition for a single action.
- [x] 5.7 Implement re-parent + create children (`parentId`, `kind: TEXT`, `ai` tag) + re-read `childIds` to confirm linkage (D8).
- [x] 5.8 Offer next step: `butler:plan` for work, light reminder for personal.
- [x] 5.9 Create `commands/decompose.md` thin command mirroring the existing `intake`/`plan` command shape.

## 6. context-aware plan / reschedule (context-aware-scheduling)

- [x] 6.1 Edit `skills/plan/SKILL.md`: read each chunk's context (absent = work, D7); route work → packer (unchanged), personal → light scheduling.
- [x] 6.2 Edit `skills/plan/SKILL.md`: keep personal chunks out of packer input; assign dueDate + reminder; render Work / Personal as separated sections in the proposal (D6).
- [x] 6.3 Edit `skills/plan/SKILL.md`: scope personal pull to already-due/committed + on-request (D6); ask personal "when", and on defer derive a time from a live read of the target day — query TickTick's existing timed items + read Calendar, place in an open slot avoiding stacking/collisions (D5).
- [x] 6.4 Edit `skills/reschedule/SKILL.md`: repack only work blocks from `now`; keep/adjust personal reminders without repacking.

## 7. Validation & tests

- [x] 7.1 Confirmed `scripts/pack_schedule.py` is untouched (no git diff) and `python3 scripts/test_pack_schedule.py` passes all 19 tests.
- [x] 7.2 Ran `claude plugin validate ./plugins/butler --strict` and `claude plugin validate . --strict` — both pass.
- [x] 7.3 Ran `openspec validate butler-personal-contexts-decompose --strict` — valid.
- [x] 7.4 Dry-run via jsonschema fixtures: personal chunk valid with no work axes; personal-with-stage FAILS (axes forbidden via `else`); work-missing-stage FAILS; no-context chunk fails the schema (context required for new chunks) while the back-compat reader rule (heuristics + template) treats absent context as work on read.

## 8. Release (0.3.0)

- [ ] 8.1 Bump `version` to `0.3.0` in `plugins/butler/.claude-plugin/plugin.json` AND the marketplace entry (keep equal).
- [ ] 8.2 Update `plugins/butler/CHANGELOG.md` and root `CHANGELOG.md` with the 0.3.0 entry.
- [ ] 8.3 `claude plugin tag ./plugins/butler` to create `butler--v0.3.0` (validates version agreement).
- [ ] 8.4 `git push origin main && git push origin refs/tags/butler--v0.3.0` (user runs interactive `/plugin` update commands).
