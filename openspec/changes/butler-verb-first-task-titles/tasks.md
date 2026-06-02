## 1. Title contract (references/task-contract.md)

- [x] 1.1 Rewrite the "Title contract" section: work form becomes a verb-first next action (concrete physical verb + object), not `Stage: qualifier`; state the free-but-physical verb rule (reject "think about / look into / deal with").
- [x] 1.2 Add the parent carve-out: parent work-units are outcome nouns, NOT verb-first (the GTD project-vs-action split).
- [x] 1.3 Add the don't-hollow + keep-the-cue rules: object stays in the title, one disambiguating cue inline, test-matrix/conditions/AC/why/links go to the body or subtasks.
- [x] 1.4 Remove the `QA: both portals, empty + set` example; update the before/after table to verb-first (e.g. `QA: both portals, set + empty, end to end` → `Verify Neighborhood Location end to end on both pricers`).
- [x] 1.5 State that stage is conveyed by a stage tag, not the title prefix.

## 2. Heuristics (references/heuristics.md)

- [x] 2.1 Decomposition (work): replace "Title = stage + qualifier" with verb-first titles + a stage tag.
- [x] 2.2 Calibration: read the stage from the stage tag, not parsed from the title prefix; note legacy title-prefix parsing as a fallback.
- [x] 2.3 Time-blocking: activity is derived from the stage tag (the stage→activity map is unchanged).

## 3. Template + setup (references/template.md)

- [x] 3.1 Chunk title mapping: verb-first next action; remove the stage-prefix instruction.
- [x] 3.2 Tags: a work chunk carries exactly one stage tag in addition to one intensity tag + `ai` (+ priority when scheduled).
- [x] 3.3 One-time setup: add the `stage` tag family (research/db/backend/frontend/review/address-comments/qa/deploy), parallel to `intensity`; tolerate the tag-write 500 (attaches as a label on first use).

## 4. Config (config.yaml)

- [x] 4.1 Add `stage_as_tag: true` under `contexts.work`; the pipeline stage keys are the single source that seeds the `#stage` tag family. No change to the pipeline menu, intensity tags, or priority tags.

## 5. Schema (schemas/chunk-task.schema.json)

- [x] 5.1 Keep `stage` as a field; update its description to note it renders as a stage tag, not a title prefix; align the title-pattern guidance to verb-first. No structural change to required/scheduling.

## 6. Validate

- [x] 6.1 Confirm only references + config + schema changed (plus version/changelog); no code. Packer + schema tests unaffected.
- [x] 6.2 `claude plugin validate ./plugins/butler --strict` and `claude plugin validate . --strict` — both pass.
- [x] 6.3 `openspec validate butler-verb-first-task-titles --strict` — valid.

## 7. Live migration (done by hand this session)

- [x] 7.1 Rename the ING-165 QA chunk to verb-first + `#qa` (`Verify Neighborhood Location end to end on both pricers`); test-matrix already lives in its 4 subtasks.
- [x] 7.2 Rename the three LOS spike trees' chunks (LOS-5 ×2, LOS-15 ×2, LOS-13 ×1) to verb-first + `#research`; parents left as outcome nouns; parentId/tags intact.

## 8. Release (0.7.0)

- [x] 8.1 Bump `version` to `0.7.0` in `plugins/butler/.claude-plugin/plugin.json` AND the marketplace entry (kept equal).
- [x] 8.2 Update `plugins/butler/CHANGELOG.md` and root `CHANGELOG.md` with the 0.7.0 entry.
- [ ] 8.3 `claude plugin tag ./plugins/butler` → `butler--v0.7.0`.
- [ ] 8.4 `git push origin main && git push origin refs/tags/butler--v0.7.0`.
