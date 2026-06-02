---
name: reschedule
description: Use when today has slipped and the user wants to recompute the rest of the day — "reschedule", "I'm behind", "move my blocks", "things slipped", "shift my plan", "recompute from now". Recomputes today's remaining blocks from the current time around the remaining commitments. Never silently drops a must.
---

# Reschedule today

Recompute the rest of **today** from where things actually are. Same packer, same
rules as `butler:plan`; the difference is `now` = the current time, so placement
starts from this moment, and only today's remaining chunks are considered.

## Config

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`. Resolve TickTick names → ids at runtime.
Load deferred MCP tools (TickTick, Google Calendar) with tool_search.

## Core rules

1. **From now.** Placement never starts before the current time.
2. **Schedule only today.** Don't spill into tomorrow's blocks; overflow cascades to unscheduled-for-later, surfaced explicitly.
3. **Work only in the packer.** Only WORK blocks are repacked from now. PERSONAL items keep their reminders (adjust a time only if the user asks); they never enter the packer. A chunk with no context is work.
4. **Never silently drop a must.** A must that can't fit surfaces as overflow with a warning.
5. **Confirm before moving blocks.**
6. **Never duplicate.** Reschedule only MOVES existing blocks — it never creates a task that already exists, and recurring habits already fire on their own (don't re-add them).

## Procedure

```
Conduct the interview per `references/interview.md` → Reschedule (honor each question's
[choice]/[open] tag — see → Presentation): "anything new today?" and "drop a passed block?"
are [choice]; "what's done / left" stays prose.

- [ ] 1. Establish "now" and what's done vs left today (ask briefly).
- [ ] 2. Re-read today's remaining WORK chunks from TickTick (scheduled-but-not-done).
        Note any personal reminders still ahead today — these are kept as-is, not repacked.
- [ ] 3. Re-read the remaining fixed commitments from Calendar (those after now).
- [ ] 4. Build packer input with now = current time (schemas/packer-input.schema.json) from
        the WORK chunks only, then run: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pack_schedule.py input.json
        Review scheduled / overflow / summary.warnings. Do NOT rewrite est0 — it is immutable.
- [ ] 5. On confirmation, update today's WORK blocks in TickTick (batch_update_tasks for moves):
        new startDate/dueDate; keep tags, parentId, est0, focusSummaries intact. Leave personal
        reminders untouched unless the user asked to shift one (then just move its due/reminder).
- [ ] 6. State the next physical action from now.
```

## References

- `${CLAUDE_PLUGIN_ROOT}/references/heuristics.md` — Time-blocking, Reconciliation.
- `${CLAUDE_PLUGIN_ROOT}/references/template.md` — field mappings + packer I/O.
- `${CLAUDE_PLUGIN_ROOT}/references/interview.md` — Reschedule.
- `${CLAUDE_PLUGIN_ROOT}/schemas/` — packer I/O schema.
