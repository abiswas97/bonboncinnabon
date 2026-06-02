## 1. Description contract (references/task-contract.md)

- [x] 1.1 Rewrite the "Description contract" section to the lean model (D1): first-action prose + optional `Done when …` + `~<n>m` + `[TICKET ↗](url)`; drop the `Why/Where/Done/Ref` labels and the `est0/stage/ai` footer.
- [x] 1.2 State the rules: `Done when …` omitted when the title implies success; multi-criteria → subtasks (not a description checklist); detail stays on Linear (no AC duplication); slop blacklist still applies to the prose.
- [x] 1.3 Cover personal (same minus link) and confirm the parent metadata header is unchanged.

## 2. Template + calibration (references/template.md, heuristics.md)

- [x] 2.1 `references/template.md`: replace the chunk content template (`Why/Where/Done/Ref` + `est0: …  stage: …  ai: …`) with the lean form; show the `~<n>m · [TICKET ↗](url)` footer; note `est0_min` renders as `~<n>m` and is immutable.
- [x] 2.2 `references/template.md`: note stage is conveyed by the title prefix; `ai_discount` is no longer written to content.
- [x] 2.3 `references/heuristics.md` → Calibration: reference `~<n>m` instead of `est0`; note grouping by stage (the stage×ai_discount cross-tab is simplified away, D3).

## 3. Schema (schemas/chunk-task.schema.json)

- [x] 3.1 Update field descriptions to the new rendering: `est0_min` "renders as `~<n>m`, immutable calibration anchor"; `done` is the single `Done when …` signal; `where` carries the first action; `ref` is the Linear link. Drop/deprecate `why` from the rendered form. No structural change to required/scheduling.

## 4. Validate

- [x] 4.1 Confirm only the references + schema changed (plus version/changelog later); no code/config. Packer + schema tests unaffected.
- [x] 4.2 `claude plugin validate ./plugins/butler --strict` and `claude plugin validate . --strict`.
- [x] 4.3 `openspec validate butler-lean-task-descriptions --strict`.

## 5. Retrofit ING-165 live descriptions

- [x] 5.1 Rewrite the ING-165 chunk descriptions (the 3 completed + the QA parent) and the 4 QA subtasks to the lean model via update_task; keep parentId/tags/dates/status intact.
- [x] 5.2 Re-read a couple to confirm the rewrite landed and linkage held.

## 6. Release (0.6.0)

- [x] 6.1 Bump `version` to `0.6.0` in `plugins/butler/.claude-plugin/plugin.json` AND the marketplace entry (keep equal).
- [x] 6.2 Update `plugins/butler/CHANGELOG.md` and root `CHANGELOG.md` with the 0.6.0 entry.
- [x] 6.3 `claude plugin tag ./plugins/butler` → `butler--v0.6.0`.
- [x] 6.4 `git push origin main && git push origin refs/tags/butler--v0.6.0`.
