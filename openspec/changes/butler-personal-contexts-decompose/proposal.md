## Why

butler 0.2.0 only models **work**: every task is shredded into pipeline stages
(`research→deploy`) carrying `stage`/`intensity`/`ai_discount` and packed into a
deep/shallow focus window. That machinery is wrong for personal tasks ("book the
dentist", "sort the photo backup") — they need free-form steps (often none) and a
light time + reminder, not a packed focus block. butler is also missing a way to
**talk through breaking down a task that already exists** in TickTick, and its
mandated intake interview is skippable (the author skipped it on ING-165 because a
checklist line can be skimmed). The scheduling engine is already domain-agnostic;
"personal" should be config + a lighter flow, not a parallel system.

## What Changes

- **Introduce `contexts` (work | personal)** in `config.yaml`, data-driven. A
  task's context is *derived from its TickTick project* and then **confirmed with
  the user** (never silent). Work keeps the full model; personal drops the
  `stage`/`intensity`/`ai_discount` axes and carries only `priority` + `est0_min`
  + a `reminder`.
- **Add `butler:decompose`** — an interview-first skill that breaks down an
  *existing* TickTick task: resolve it by name/search or pick from undecomposed
  candidates, derive + confirm its context, augment if already split, then
  decompose context-aware (work → pipeline stages, personal → free-form or none).
- **Make the intake interview a HARD GATE.** intake and decompose MUST complete a
  blocking interview (intent / prior progress / which-shape-applies) before
  producing or writing any task tree. Add a "do not proceed until X" red-flags
  block. (Behavior change to shipped `intake`.)
- **Make `plan` / `reschedule` context-aware.** Work chunks go through the packer
  unchanged; personal chunks bypass the packer and get a due time + reminder, kept
  visually separated in the proposal. (Behavior change to shipped `plan` /
  `reschedule`.)
- **Extend `chunk-task.schema.json`** with a `context` enum and conditional
  requirements: `stage`/`intensity`/`ai_discount`/`est0_min` required only when
  `context: work`; a personal chunk is `{ id, title, context, priority?,
  est0_min?, reminder?, kind, ai_generated }`. **Missing `context` = work**
  (back-compat for existing chunks).
- **0.3.0 release**: version bump in `plugin.json` + the marketplace entry,
  CHANGELOGs, `claude plugin tag`, push.

No breaking changes to the packer contract or to existing work trees: personal
chunks never enter the packer, and absent `context` reads as `work`.

## Capabilities

### New Capabilities
- `task-contexts`: the work|personal context model — config shape, derive-by-project
  + mandatory user confirmation, the personal lightweight task model, the
  `chunk-task` schema `context` field with conditional axis requirements, and the
  missing-context-is-work back-compat rule.
- `interview-gate`: the shared hard-gate requirement that both `intake` and
  `decompose` complete a blocking interview before any decomposition or write.
- `decompose-skill`: the new `butler:decompose` skill — resolve an existing task,
  derive+confirm context, augment-if-already-split, context-aware decomposition,
  re-parent the existing task, re-read to confirm linkage, offer next step.
- `context-aware-scheduling`: `plan` and `reschedule` behavior split by context —
  work via the packer (unchanged), personal as light time + reminder, visually
  separated, with personal "when" chosen conversationally.

### Modified Capabilities
<!-- openspec/specs/ is empty: no existing capability specs to modify. The behavior
     changes to shipped intake/plan/reschedule are captured as ADDED requirements
     in the new capabilities above (interview-gate, context-aware-scheduling). -->

## Impact

- **Config**: `plugins/butler/config.yaml` gains a `contexts` block; work scheduling
  config (`work_window`, `pipeline`, `capacity`, and `work_project` →
  `contexts.work.default_project`) folds under `contexts.work`; cross-context
  infrastructure (`planning_project`, `ai`/`parked` tags, calibration, ritual) stays
  top-level. Packer values are unchanged; only the input-builder's read paths move.
- **Schema**: `plugins/butler/schemas/chunk-task.schema.json` (new `context` enum +
  `if/then` conditional requirements). `packer-input.schema.json` unchanged.
- **Skills**: new `plugins/butler/skills/decompose/SKILL.md` + `commands/decompose.md`;
  edits to `skills/intake/SKILL.md` (hard gate) and `skills/plan` + `skills/reschedule`
  (context-aware).
- **References**: `references/interview.md` (decompose bank + hard-gate red-flags),
  `references/heuristics.md` (personal decomposition + light scheduling),
  `references/task-contract.md` (confirm applies to all generated tasks),
  `references/template.md` (personal field mapping: reminder, no pomo/intensity).
- **Tests**: `scripts/pack_schedule.py` unchanged → 19 packer tests stay green;
  personal logic is skill-level (no script test). Re-validate with
  `claude plugin validate ./plugins/butler --strict`.
- **Release**: `plugins/butler/.claude-plugin/plugin.json` + marketplace entry +
  both CHANGELOGs + `butler--v0.3.0` tag.
- **External state**: TickTick + Google Calendar only (no side files). Linear stays
  read-only, explicit-ID only.
