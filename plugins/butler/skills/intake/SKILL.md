---
name: intake
description: Use when the user names an explicit Linear ticket ID, or describes a NEW piece of work not yet in TickTick and wants it turned into tasks — "start ABC-123", "scope this new work", "how should I approach X", "turn this into a task tree". Builds a durable task tree in TickTick. For breaking down a task that ALREADY exists in TickTick, use butler:decompose.
---

# Intake new work

Turn a unit of work into human, session-sized chunks and a **durable task tree**
in TickTick. Build the whole tree once (it persists); scheduling the day is
`butler:plan`'s job. Idempotent: re-running on the same ticket resumes the
existing tree, never duplicates it.

## Config

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`, then run the config preflight (references/template.md → Config preflight; migrate if behind, error if ahead). Resolve TickTick names → ids at runtime.
Load deferred MCP tools (TickTick; Linear only if an ID is named) with tool_search.

## Core rules

1. **Interview is a HARD GATE.** Do NOT decompose or write anything until you have run the interview and confirmed intent / prior progress / single-vs-multi-step (`${CLAUDE_PLUGIN_ROOT}/references/interview.md` → Hard gate). A skimmed interview is a defect, not a shortcut.
2. **Never assume a ticket.** Pull Linear only when the user names an ID this turn; else use the described work.
3. **Idempotency first.** Before creating anything, search the work context's `default_project` for a parent whose `content` has `Ticket: <ID>`. If found → resume that tree (hand to `butler:plan`), do NOT create a duplicate.
4. **Points are complexity, not time.** Use the envelope to shape the tree (more grooming/spike chunks, more slack); never divide into hours.
5. **Lean, human tasks.** Follow `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md`. Tag every created task `ai`.
6. **Confirm before writing.**

## Red flags — do not proceed until cleared

STOP and resolve before creating ANY task:

- Haven't confirmed what "done" looks like → ask, don't assume.
- Haven't confirmed fresh-start vs already-part-done → already-done work is not re-created.
- Haven't confirmed multi-step vs single action → a single action is not shredded into a tree.
- About to decompose straight from the ticket/description without the interview → that is exactly the skip this gate exists to prevent.

## Procedure

```
- [ ] 1. Resolve the work. If a Linear ID is named, pull the ticket and map fields
        (references/template.md → Linear): estimate.value for Points; AC from the
        description "Acceptance Criteria" section; gitBranchName; url; labels (ignore v* tags).
        NEVER fetch Linear without an explicit ID.
- [ ] 2. IDEMPOTENCY CHECK: search the work context's `default_project` for an existing parent
        with `Ticket: <ID>`. If found, summarize the existing tree and route to `butler:plan`
        instead of creating.
- [ ] 3. HARD GATE — interview for the human shape and what to land first, honoring the
        bank's [choice]/[open] tags (references/interview.md → Hard gate, then Intake; →
        Presentation for how to ask). Surface unknowns and blockers. Do NOT proceed to step 4
        until intent / prior progress / single-vs-multi-step are confirmed; a single-action task
        is not decomposed.
- [ ] 4. Decompose by PICKING STAGES from `contexts.work.pipeline` (references/heuristics.md →
        Decomposition (work)): skip stages that don't apply; merge thin ones to land in 2–6; add
        ad-hoc chunks for off-pipeline work. Title = verb-first next action naming the object;
        stage rides a `#stage` tag, not the title. Each chunk is
        `context: work` and inherits its stage's default intensity + ai_discount (override per
        chunk); set est0 now. Include a `review` stage when there are `discounted` build stages
        (it absorbs AI-output verification). Confirm the proposed tree before writing
        (interview.md → Intake, "Confirm the shape" [choice]).
- [ ] 5. Build the tree (references/template.md, schemas/parent-task + chunk-task): create the
        parent (kind TEXT, metadata in `content`), capture its id, then create ALL chunks as
        child tasks with parentId set. RE-READ to confirm childIds linked (create response is stale).
        Leave all chunks dateless — scheduling is butler:plan.
- [ ] 6. State the single first physical action — one observable physical verb, not an outcome
        noun (references/accommodations.md → action-first) — then offer to plan the target day (butler:plan).
```

## Worked example (abbreviated)

User: "linear ticket ABC-123, I want to start it today." A 1-point change that
adds a field to two forms and wires it to a checkout API. Pick stages (no `db` —
the field already exists). Each chunk is a verb-first action + a stage tag (with `intensity`, ai `discount`):

- Trace where the field is read + the checkout→API flow — `#research`, `deep`, ai `none`.
- Add the dropdown to both forms + carry-over — `#frontend`, `shallow`, ai `discounted`.
- Wire the value into the checkout API (empty-safe) + carry-back — `#backend`, `deep`, ai `discounted`.
- Submit the PR + AI-assisted review — `#review`, `deep`, ai `none` (absorbs AI-output verification).
- Verify the new field end to end on both forms — `#qa`, `shallow`, ai `none`.

The whole tree is created; `butler:plan` schedules only the chosen day's chunks.

## References

- `${CLAUDE_PLUGIN_ROOT}/references/heuristics.md`
- `${CLAUDE_PLUGIN_ROOT}/references/template.md`
- `${CLAUDE_PLUGIN_ROOT}/references/interview.md`
- `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md`
- `${CLAUDE_PLUGIN_ROOT}/references/accommodations.md` — how butler speaks to a user under EF load; apply at miss-handling, selection, next-action, and tone. Single source, don't restate.
- `${CLAUDE_PLUGIN_ROOT}/schemas/`
