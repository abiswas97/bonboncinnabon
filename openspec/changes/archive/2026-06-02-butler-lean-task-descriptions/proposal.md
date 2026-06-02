## Why

butler's chunk descriptions are a flat `Why / Where / Done / Ref` key:value block
plus an `est0: 60m  stage: backend  ai: discounted` footer. Two problems: (1) the
footer is jargon — `est0` and `ai:discounted` mean nothing to the human reading the
task; (2) the block duplicates acceptance criteria that already live on Linear,
creating a second source that drifts. A personal task manager entry should be a
**launchpad, not a spec**: the one concrete first action + a link back to the
system of record, kept minimal. This change makes chunk descriptions lean and
human-first while preserving the estimate (and thus calibration) under a legible
label.

## What Changes

- **New lean chunk-description format**: a prose first action, a single
  `Done when …` line (no `Done:` heading), the estimate as `~60m`, and a Markdown
  link to the source ticket. No `Why/Where/Ref` labels, no `stage`/`ai` footer.
- **Estimate kept, relabeled**: `est0: 60m` → `~60m`. It remains the immutable
  calibration anchor (never overwritten on reschedule); only the human-facing label
  changes. Calibration is preserved.
- **Stage stays in the title prefix** (`Backend: …`), so it leaves the footer
  without being lost. **`ai_discount` drops from the content** (it's estimation-time
  metadata that defaults from the stage).
- **Multi-criteria acceptance → real subtasks** (decompose), never a checklist in
  the description. A single signal stays a one-line `Done when …`.
- **Detail lives in the link**: descriptions reference Linear, never copy its AC.
- **Personal chunks**: same shape minus the link; **parent work-units** keep their
  `Linear / Ticket / Branch` header (the unit's record).
- **Retrofit** the live ING-165 task descriptions to the new model as the demo.
- **0.6.0 release**: version bump + marketplace entry, CHANGELOGs, tag, push.

## Capabilities

### New Capabilities
- `task-descriptions`: the contract for the body of a generated task — lean
  first-action + `Done when` + `~estimate` + source link; labels/jargon dropped;
  multi-criteria becomes subtasks; detail stays in the linked system of record.

### Modified Capabilities
<!-- task-contexts' TITLE rule (lean imperative, ≤70, no stage prefix for personal)
     is unchanged — this change governs the description BODY, a separate concern. -->

## Impact

- **References**: `references/task-contract.md` (Description contract section
  rewritten), `references/template.md` (chunk content template + the `~60m`
  calibration line), `references/heuristics.md` (Calibration references `~Nm`, not
  `est0`).
- **Schema**: `schemas/chunk-task.schema.json` — field descriptions updated to the
  new rendering (`why` dropped from the rendered form; `est0_min` stays as the
  estimate + anchor). No structural requirement change to scheduling.
- **Live data**: rewrite the ING-165 chunk + subtask descriptions in TickTick to the
  new format.
- **No code**: `pack_schedule.py`, `config.yaml` untouched; tests stay green.
- **Release**: `plugin.json` + marketplace entry + both CHANGELOGs + `butler--v0.6.0`.
- **Compatibility**: existing tasks with the old block still parse (the agent reads
  whatever is there); new tasks use the lean form.
