---
name: intake
description: Use when the user names an explicit Linear ticket ID (e.g. "linear ticket ING-165, I want to do X") or describes a new piece of work and wants it broken down — "break this down", "decompose", "scope this", "how should I approach X", "turn this into tasks". Builds a durable human task tree in TickTick. Never queries Linear without an explicit ticket ID.
---

# Intake new work

Turn a unit of work into human, session-sized chunks and a **durable task tree**
in TickTick. Build the whole tree once (it persists); scheduling the day is
`butler:plan`'s job. Idempotent: re-running on the same ticket resumes the
existing tree, never duplicates it.

## Config

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`. Resolve TickTick names → ids at runtime.
Load deferred MCP tools (TickTick; Linear only if an ID is named) with tool_search.

## Core rules

1. **Never assume a ticket.** Pull Linear only when the user names an ID this turn; else use the described work.
2. **Idempotency first.** Before creating anything, search work_project for a parent whose `content` has `Ticket: <ID>`. If found → resume that tree (hand to `butler:plan`), do NOT create a duplicate.
3. **Points are complexity, not time.** Use the envelope to shape the tree (more grooming/spike chunks, more slack); never divide into hours.
4. **Lean, human tasks.** Follow `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md`. Tag every created task `ai`.
5. **Confirm before writing.**

## Procedure

```
- [ ] 1. Resolve the work. If a Linear ID is named, pull the ticket and map fields
        (references/template.md → Linear): estimate.value for Points; AC from the
        description "Acceptance Criteria" section; gitBranchName; url; labels (ignore v* tags).
        NEVER fetch Linear without an explicit ID.
- [ ] 2. IDEMPOTENCY CHECK: search work_project for an existing parent with `Ticket: <ID>`.
        If found, summarize the existing tree and route to `butler:plan` instead of creating.
- [ ] 3. Interview for the human shape and what to land first
        (references/interview.md → Intake). Surface unknowns, blockers, prior progress.
- [ ] 4. Decompose into human, session-sized chunks (references/heuristics.md → Decomposition):
        pipeline stages are natural boundaries; aim for 2–6; verb + done-signal; don't over-split.
        Set each chunk's intensity, chunk_type, and ai_discount. For each `discounted` build chunk,
        add a paired `review` verify chunk (heuristics → Estimation).
- [ ] 5. Build the tree (references/template.md, schemas/parent-task + chunk-task): create the
        parent (kind TEXT, metadata in `content`), capture its id, then create ALL chunks as
        child tasks with parentId set. RE-READ to confirm childIds linked (create response is stale).
        Leave all chunks dateless — scheduling is butler:plan.
- [ ] 6. State the single first physical action, then offer to plan the target day (butler:plan).
```

## Worked example (abbreviated)

User: "linear ticket ABC-123, I want to start it today." A 1-point change that
adds a field to two forms and wires it to an API. Human chunks:

Each line is `intensity`, chunk_type, ai_discount (activity is derived from chunk_type):

- Trace where the field is read on the form — `deep`, type `trace`, ai `none` (you must understand it).
- Wire the field into both forms and the API call — `deep`, type `wire`, ai `discounted`.
- Review AI output for the wiring — `deep`, type `review`, ai `none` (auto-paired with the wire chunk; verifying coupled output needs focus).
- Manually verify both forms end to end — `shallow`, type `qa`, ai `none`.

The whole tree is created; `butler:plan` schedules only the chosen day's chunks.

## References

- `${CLAUDE_PLUGIN_ROOT}/references/heuristics.md`
- `${CLAUDE_PLUGIN_ROOT}/references/template.md`
- `${CLAUDE_PLUGIN_ROOT}/references/interview.md`
- `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md`
- `${CLAUDE_PLUGIN_ROOT}/schemas/`
