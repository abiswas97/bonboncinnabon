---
name: plan
description: Use when the user wants to plan, time-box, or commit a work day in TickTick — "plan my day", "plan today", "plan tomorrow", "what should I work on today", end-of-day planning for the next day, or reconciling open work and committing a day's blocks. Schedules around Google Calendar commitments. Works for today (planned in the morning) or tomorrow (planned in the evening).
---

# Plan the day

Reconcile open work and time-box a **target day** in TickTick — today when run in
the morning, tomorrow when run in the evening — scheduling around fixed
commitments read from Google Calendar. Day-at-a-time by design: the full tree
already persists; only the target day gets times.

## Config

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml` — the only user-specific surface. Resolve
TickTick project and tag names → ids at runtime (`list_projects` / `list_tags`).
Load deferred MCP tools with tool_search before use (TickTick, Google Calendar).

## Core rules

1. **Schedule only the target day.** Put start/due + reminders on the target day's chunks only; everything else stays dateless.
2. **Points are complexity, not time.** Never divide Linear story points into hours.
3. **Confirm before writing.** Show the proposed blocks + the packer summary, get a yes, then write.
4. **Lean, human tasks.** Follow `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md`. Every butler-created task carries the `ai` tag.
5. **Never assume a ticket.** Touch Linear only when the user names an explicit ID this turn.

## Procedure

```
- [ ] 1. Resolve the target day (references/interview.md → Target day): explicit wins,
        else infer from time of day and confirm in one line.
- [ ] 2. Read open work for the target day from TickTick: active parent work units in
        work_project and their child chunks (done / not-done / unscheduled).
- [ ] 3. Reconcile — CAPPED and NO-BLAME (references/heuristics.md → Reconciliation):
          default = re-surface with "keep or park?" (park = drop date + `parked` tag);
          ask "what got in the way?" for at most the 1–2 most-slipped chunks;
          escalate to "why does this keep slipping?" only on repeat slips;
          catch chunks finished-but-not-ticked.
- [ ] 4. Pick what to land; set must/should/want. Respect max_musts (flag, don't silently exceed).
- [ ] 5. Read the target day's fixed commitments from Calendar; confirm read-back;
        ask about off-calendar duties (references/interview.md → Fixed duties).
- [ ] 6. Confirm each chunk carries its est0 line (set at intake; references/template.md).
        Don't rewrite est0. The packer reads each chunk's `stage` + `intensity`.
- [ ] 7. Build packer input (schemas/packer-input.schema.json) from config + the target
        day's chunks + commitments, then run:
            python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pack_schedule.py input.json
        Review scheduled / overflow / summary.warnings with the user. Adjust, re-run until it fits.
- [ ] 8. On confirmation, write the target day's blocks to TickTick (kind TEXT):
        startDate/dueDate/isAllDay:false/timeZone/reminders + focusSummaries.estimatedPomo,
        intensity tag + must/should/want + `ai`. RE-READ to confirm parentId links (the create
        response is stale; references/template.md).
- [ ] 9. State the single first physical action so starting is frictionless.
```

## References

Read when the step points to them; each is self-contained:

- `${CLAUDE_PLUGIN_ROOT}/references/heuristics.md` — estimation, AI discount, time-blocking, reconciliation, calibration.
- `${CLAUDE_PLUGIN_ROOT}/references/template.md` — task template + TickTick/Linear/Calendar field mappings + packer I/O.
- `${CLAUDE_PLUGIN_ROOT}/references/interview.md` — question banks per mode.
- `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md` — the lean task writing contract.
- `${CLAUDE_PLUGIN_ROOT}/schemas/` — JSON Schema for tasks and packer I/O.

New work with no tree yet → use `butler:intake` first. Mid-day slip → `butler:reschedule`.
