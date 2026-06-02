## Context

0.4.0 introduced the `[choice]/[open]` convention (interview.md → Presentation) and
applied AskUserQuestion to intake + decompose, but inlined the mechanic into each
skill's procedure. plan/reschedule still interview in prose. This change finishes the
rollout (plan/reschedule) and refactors to a single shared definition so the
convention isn't duplicated across four skills. Presentation only — no code path
changes.

## Goals / Non-Goals

**Goals:**
- plan/reschedule discrete forks become structured choices.
- One definition of the convention; skills reference it via a single canonical pointer.
- Every bank carries its own per-question tags (the specifics live with the questions).
- No regression to intake/decompose behavior; no code/schema/config change.

**Non-Goals:**
- No change to what the packer does, what gets scheduled, or the task model.
- Not turning prose prompts (what got in the way, off-calendar duties) into forms.

## Decisions

### D1: Single source = interview.md → Presentation; banks carry tags; skills point

The convention lives once in Presentation (already there from 0.4.0). Each bank
tags its own questions `[choice]`/`[open]` with inline option labels. Each skill's
interview step uses ONE canonical pointer sentence and does NOT restate the
mechanics. This is the DRY fix the change exists for: "if the rule changes, edit one
file."

*Alternative considered:* keep the per-skill instructions (0.4.0 style). Rejected —
that's the duplication being removed; four copies drift.

### D2: The canonical pointer (consistent interface across skills)

A single sentence, used verbatim in all four skills' interview steps:

> Conduct the interview per `references/interview.md` (honor each question's
> `[choice]` / `[open]` tag — see → Presentation; discrete = AskUserQuestion, open =
> prose).

intake/decompose are refactored from their 0.4.0 inlined mechanics to this pointer.
The hard-gate's "do not proceed until X" salience stays (that's a gate-discipline
concern, separate from presentation).

### D3: plan/reschedule [choice] vs [open] split

- **[choice]**: target-day (today / tomorrow); fixed-duties read-back ("these events
  — still on?" → confirm / adjust); per-chunk commitment (must / should / want,
  multiSelect when deciding several at once); reconcile keep-or-park (keep / park).
- **[open]**: "what got in the way?" (reconcile follow-up, routed per heuristics),
  "anything new today?" (reschedule), off-calendar duty details, energy notes.

### D4: multiSelect used sparingly

Commitment-setting across several chunks is the one natural multiSelect (pick which
are must, etc.). Everything else is single-select. Keeps the cards legible.

### D5: Discipline unchanged

Presentation's "one main thread at a time, 4-question ceiling, prose fallback" rule
already governs and is not relaxed. Reconcile especially stays capped/no-blame —
structured keep/park must not turn into interrogating every chunk.

## Risks / Trade-offs

- **[Refactoring intake/decompose loses salience]** → the pointer + tagged banks
  retain all the specifics (in the banks); the gate's "do not proceed" stays inline.
- **[Reconcile becomes a wall of keep/park cards]** → D5 + the existing capped
  no-blame reconcile rule (heuristics) bound it; one main thread at a time.
- **[Tool-absent harness]** → prose fallback unchanged (Presentation D5 from 0.4.0).

## Migration Plan

- Additive, prose-only edits to `interview.md` + the four SKILL.md files. No code,
  schema, or config change.
- Rollback: revert the plugin version; nothing persisted changes.
- Release: bump `plugin.json` + marketplace entry (equal), update both CHANGELOGs,
  `claude plugin tag ./plugins/butler` → `butler--v0.5.0`, push branch + tag.

## Open Questions

- None blocking. (Future: a tiny lint that every SKILL interview step contains the
  canonical pointer — deferred; over-engineering for four files.)
