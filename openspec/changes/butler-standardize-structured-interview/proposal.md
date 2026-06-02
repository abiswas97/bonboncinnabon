## Why

0.4.0 added structured AskUserQuestion prompts to `intake` and `decompose`, but
`plan` and `reschedule` still interview entirely in free-text prose — their discrete
forks (target-day today/tomorrow, must/should/want commitment, keep-or-park
reconcile, fixed-duties read-back) are exactly the kind of finite choices the tool
handles best. Worse, the *mechanic* ("present discrete decisions as AskUserQuestion
choices…") is currently restated inside each skill — knowledge duplication that will
drift. The convention should be defined once and shared: one source of truth for HOW
to ask, the per-question tags living in the banks, and every skill simply pointing at
it. This change extends structured questions to the last two skills and standardizes
the convention across all four (DRY / single source of truth).

## What Changes

- **Extend structured prompts to `plan` and `reschedule`**: target-day resolution
  (today / tomorrow), per-chunk commitment (must / should / want), the reconcile
  keep-or-park decision, and the fixed-duties calendar read-back become
  AskUserQuestion choices. Open prompts (what got in the way, anything new today,
  off-calendar duty details) stay free text.
- **Standardize the convention as shared, single-source**: `references/interview.md`
  → Presentation is the *only* definition of the `[choice]/[open]` rule; every
  bank carries its own per-question tags; each skill's interview step references the
  convention with one canonical pointer instead of restating the AskUserQuestion
  mechanics. Refactor `intake`/`decompose` to that pointer (remove the duplicated
  mechanics added in 0.4.0) so the rule lives in exactly one place.
- **Tag the remaining banks** (Target day, Plan / reconcile, Reschedule, Fixed
  duties) `[choice]` / `[open]` with inline option labels, same as the 0.4.0 banks.
- **0.5.0 release**: version bump in `plugin.json` + marketplace entry, CHANGELOGs,
  `claude plugin tag`, push.

No task-model, schema, packer, config, or scheduling change — presentation only.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `structured-interview`: broaden the structured-choice requirement from
  intake+decompose to ALL interview-driven skills (intake, decompose, plan,
  reschedule) with the added plan/reschedule decision coverage; add a single-source
  requirement that the convention is defined once and referenced, not restated per
  skill.

## Impact

- **References**: `references/interview.md` — Presentation section strengthened to
  state it is the single source and applies to all interview skills; `[choice]/[open]`
  tags added to the Target day, Plan / reconcile, Reschedule, and Fixed duties banks.
- **Skills**: `skills/plan/SKILL.md` and `skills/reschedule/SKILL.md` interview steps
  adopt the canonical pointer + structured forks; `skills/intake/SKILL.md` and
  `skills/decompose/SKILL.md` refactored from restated mechanics to the same pointer.
- **No code**: schemas, `pack_schedule.py`, `config.yaml` untouched; all tests stay
  green by construction.
- **Release**: `plugins/butler/.claude-plugin/plugin.json` + marketplace entry + both
  CHANGELOGs + `butler--v0.5.0` tag.
- **Compatibility**: additive + harness-aware; prose fallback unchanged.
