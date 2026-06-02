## 1. Accommodations reference (single source)

- [x] 1.1 Create `references/accommodations.md` with one `<accommodations>` XML block: the six principles (action-first, if-then-cue, mastery+pleasure, flexibility-with-spine, non-punitive, tone), each `<principle>` carrying name + behavior + evidence anchor + `confidence`. Include the `<do-not>` anti-requirements. Source the content from `docs/research/butler-accommodations-evidence.md` (keep it tight — doctrine, not the full lit review).
- [x] 1.2 Add an `## Accommodations` pointer to each skill's reference list (`intake`, `decompose`, `plan`, `reschedule`): one line, "apply `references/accommodations.md` where you speak to the user," no restatement.

## 2. Skills apply the principles (at existing touchpoints)

- [x] 2.1 `skills/plan/SKILL.md`: reconciliation step → non-punitive miss-handling (neutral event + keep-or-park + small next step; surface facts on a spiral); selection step → mastery+pleasure blend + partial-completion framing; committed first action → action-first if-then cue. Reference accommodations, don't duplicate.
- [x] 2.2 `skills/reschedule/SKILL.md`: the slipped-block handling follows the non-punitive + flexibility-with-spine principles (graded smaller version instead of drop).
- [x] 2.3 `skills/intake/SKILL.md` + `skills/decompose/SKILL.md`: chunk first-action is action-first (one observable physical verb); tone pointer. (Mostly already true post-0.7.0; add the pointer + tighten any verdict-ish phrasing.)

## 3. Burnout detection (auto, inside plan)

- [x] 3.1 `skills/plan/SKILL.md`: add a reconciliation sub-step that computes the overload signal from a rolling `pacing.window_days` window — completed load (`list_completed_tasks_by_date`) + scheduled load per day vs the user's own baseline (median + `packed_quantile`); components = packed streak (≥`min_packed_streak`) + mandatory no-recovery flag (`recovery_fraction`). Completion (`high_completion`) is NOT a gate — read it only to tune wording. Bail to silent when history is thin (no reliable baseline).
- [x] 3.2 Fire on the RISING EDGE only: when the current consecutive packed streak *first reaches* `min_packed_streak` (one day of grace for a skipped planning day); for any longer streak the edge has passed → stay SILENT. No persisted state. Skip-not-defer if the crossing day wasn't planned (fail-safe to silence). Honor the soft work-window (a late evening alone is not overload).
- [x] 3.3 When it fires: surface ONE no-blame observation + ask whether to keep the next day lighter; act only on yes (lighten / defer / protect a recovery gap / offer low-energy). NEVER add a task, auto-insert rest, or reschedule unasked.
- [x] 3.4 `references/heuristics.md`: add a `Pacing` section documenting the signal, the rising-edge cool-down, and the never-add-a-task rule (single source; skill references it).

## 4. Low-energy reduced mode

- [x] 4.1 `skills/plan/SKILL.md`: accept a user low-energy signal at any point → reduced day (~one mastery + one pleasure, smallest first step, not defer-all). Offer reduced mode as one option when burnout fires (never auto-apply).
- [x] 4.2 `references/heuristics.md` → Pacing: document reduced mode (what it cuts to, how it is triggered/offered).

## 5. Versioned config additions

- [x] 5.1 `config.yaml`: add the top-level `pacing` block (window_days 7, min_packed_streak 4, packed_quantile 0.75, recovery_fraction 0.5, high_completion 0.8) with comments; bump `config_version` 1 → 2.
- [x] 5.2 `schemas/config.schema.json`: add `pacing` properties; bump `configVersion` 1 → 2.
- [x] 5.3 Confirm the shared preflight migration story covers v1 → v2 (additive `pacing` defaults) — no preflight prose change needed if it already generalizes.

## 6. Validate

- [x] 6.1 `openspec validate butler-accommodations --strict`.
- [x] 6.2 `claude plugin validate ./plugins/butler --strict` and `claude plugin validate . --strict`.
- [x] 6.3 `config.yaml` validates against `config.schema.json` (jsonschema fixture); config_version (2) == configVersion (2).
- [x] 6.4 Packer + chunk-schema tests still pass (no code change).
- [x] 6.5 Grep: no anti-requirement residue introduced (no streak/guilt/overdue-badge/productivity-as-worth phrasing in skills or references).

## 7. Release (0.9.0)

- [x] 7.1 Bump `version` to `0.9.0` in `plugins/butler/.claude-plugin/plugin.json` AND the marketplace entry (equal).
- [x] 7.2 Update `plugins/butler/CHANGELOG.md` and root `CHANGELOG.md` with the 0.9.0 entry.
- [x] 7.3 `claude plugin tag ./plugins/butler` → `butler--v0.9.0`.
- [x] 7.4 `git push origin main && git push origin refs/tags/butler--v0.9.0`.
- [x] 7.5 Archive + sync specs (accommodations + burnout-detection new; context-aware-scheduling delta).
