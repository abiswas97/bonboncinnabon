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
3. **Never silently drop a must.** A must that can't fit surfaces as overflow with a warning.
4. **Confirm before moving blocks.**

## Procedure

```
- [ ] 1. Establish "now" and what's done vs left today (ask briefly).
- [ ] 2. Re-read today's remaining chunks from TickTick (scheduled-but-not-done).
- [ ] 3. Re-read the remaining fixed commitments from Calendar (those after now).
- [ ] 4. Build packer input with now = current time (schemas/packer-input.schema.json),
        then run: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pack_schedule.py input.json
        Review scheduled / overflow / summary.warnings. Do NOT rewrite est0 — it is immutable.
- [ ] 5. On confirmation, update today's blocks in TickTick (batch_update_tasks for moves):
        new startDate/dueDate; keep tags, parentId, est0, focusSummaries intact.
- [ ] 6. State the next physical action from now.
```

## References

- `${CLAUDE_PLUGIN_ROOT}/references/heuristics.md` — Time-blocking, Reconciliation.
- `${CLAUDE_PLUGIN_ROOT}/references/template.md` — field mappings + packer I/O.
- `${CLAUDE_PLUGIN_ROOT}/references/interview.md` — Reschedule bank.
- `${CLAUDE_PLUGIN_ROOT}/schemas/` — packer I/O schema.
