## Context

Chunk descriptions today are a `Why/Where/Done/Ref` block + `est0/stage/ai` footer
(task-contract.md → Description contract; template.md → chunk content). The footer
is jargon and the block duplicates Linear's AC. We're making descriptions a lean
launchpad while keeping the estimate (and calibration). Presentation/content only —
no scheduling or packer change.

## Goals / Non-Goals

**Goals:**
- Human-first chunk descriptions: first action + `Done when …` + `~Nm` + ticket link.
- Keep the estimate legible (`~Nm`) and immutable (calibration preserved).
- Multi-criteria → real subtasks; never a description checklist.
- No duplication of Linear AC.

**Non-Goals:**
- No change to titles (task-contexts owns those), the packer, scheduling, or config.
- Not removing calibration — only relabeling its anchor.

## Decisions

### D1: The lean format

```
<first physical action — imperative prose, 1–2 lines; `inline code` for identifiers>
Done when <one observable signal>.

~<minutes>m · [<TICKET> ↗](<linear-url>)
```

- `Done when …` line is OPTIONAL and omitted when the title already implies success.
- Footer line is `~<n>m · [TICKET ↗](url)`. Personal: `~<n>m` alone (no link).
- Parent work-unit unchanged (`Linear / Ticket / Branch` header).

*Alternative considered:* keep the labeled `Why/Where/Done/Ref` block. Rejected —
labels are ceremony and the block duplicates Linear.

### D2: `est0` → `~Nm`, calibration preserved

The estimate is the immutable original (set at intake, never overwritten). Only the
label changes (`est0: 60m` → `~60m`). Calibration still reads `~Nm` vs actual focus
time, grouped by stage. heuristics.md → Calibration is updated to reference `~Nm`.

*Alternative considered:* drop the estimate entirely (the block already shows
duration). Rejected by the user — keep the estimate so calibration survives.

### D3: Stage in the title, ai_discount out of content

Stage already lives in the title prefix (`Backend: …`), so the footer needn't repeat
it; calibration parses stage from the title. `ai_discount` is estimation-time
metadata that defaults from the stage (config `pipeline`) — it drops from the
description. Consequence: calibration groups by stage alone; the stage×ai_discount
cross-tab for research/backend is simplified away (acceptable — it was a refinement,
and the default is recoverable from the stage).

### D4: Multi-criteria → subtasks (reuse decompose), not a checklist

A chunk with several acceptance signals is decomposed into child subtasks (the
mechanism we already use). A description-embedded `- [ ]` checklist is NOT used —
it would re-duplicate AC and isn't a schedulable unit. Single signal → one
`Done when …` line.

### D5: Backward compatibility

Existing tasks keep their old `Why/Where/Done/Ref/est0` block; the agent reads
whatever is present. New tasks use the lean form. The ING-165 live descriptions are
retrofitted as the reference example.

## Risks / Trade-offs

- **[Calibration loses the ai_discount cross-tab]** → D3; acceptable, defaults derive from stage.
- **[First-action prose drifts back into slop]** → the slop blacklist in task-contract.md still applies to the prose; keep it tight, ≤~2 lines.
- **[Link rot / wrong ticket]** → link uses the parent's verified Linear URL; personal chunks omit it.

## Migration Plan

- Prose/schema-description edits only: `task-contract.md`, `template.md`,
  `heuristics.md`, `chunk-task.schema.json` field descriptions. No code/config.
- Retrofit ING-165 chunk + subtask descriptions in TickTick (update_task), re-read to confirm.
- Release: bump `plugin.json` + marketplace (equal), CHANGELOGs, `claude plugin tag`
  → `butler--v0.6.0`, push.
- Rollback: revert plugin version; live task descriptions are cosmetic.

## Open Questions

- None blocking. (`Done when …` inclusion is a judgment call per chunk; the contract
  says "omit when the title implies success".)
