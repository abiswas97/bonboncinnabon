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
2. **Context-aware.** WORK chunks go through the packer (focus blocks). PERSONAL items get a light due time + reminder and NEVER enter packer input. Read a chunk's context from its project (`references/heuristics.md` → Contexts); a chunk with no context is work. Keep the two visually separated in the proposal.
3. **Points are complexity, not time.** Never divide Linear story points into hours.
4. **Confirm before writing.** Show the proposed blocks + the packer summary, get a yes, then write.
5. **Lean, human tasks.** Follow `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md`. Every butler-created task carries the `ai` tag.
6. **Never assume a ticket.** Touch Linear only when the user names an explicit ID this turn.
7. **Never duplicate what already exists.** Reconcile against open tasks AND recurring habits before scheduling. A routine that already fires as a habit (or an existing task) is already handled — do NOT create a task for it. Schedule only the gap: net-new work, and a dateless existing task gets a date rather than a recreated copy (`references/heuristics.md` → Reconciliation).

## Procedure

```
Conduct every interview part per `references/interview.md` (honor each question's
[choice]/[open] tag — see → Presentation): target-day, keep-or-park, must/should/want,
and the fixed-duties read-back are [choice]; "what got in the way?" stays prose.

- [ ] 1. Resolve the target day (references/interview.md → Target day): explicit wins,
        else infer and confirm via the [choice] there.
- [ ] 2. Read open WORK for the target day: active parent work units in the work context's
        projects (contexts.work.projects) and their child chunks (done / not-done /
        unscheduled). A chunk with no context counts as work.
- [ ] 3. Read PERSONAL items for the target day: personal-project tasks
        (contexts.personal.projects) already due or committed for that day, AND the
        recurring habits (`list_habits`). Routines already covered by a habit (reading,
        pet care, finance checks, the planning ritual) or an existing task are ALREADY
        handled — never recreate them; they just fire. Pull MORE personal tasks only if
        the user asks — keep the daily ritual low-noise.
- [ ] 4. Reconcile WORK — CAPPED and NO-BLAME (references/heuristics.md → Reconciliation):
          default = re-surface with "keep or park?" (park = drop date + `parked` tag);
          ask "what got in the way?" for at most the 1–2 most-slipped chunks;
          escalate to "why does this keep slipping?" only on repeat slips;
          catch chunks finished-but-not-ticked. (Personal items just keep or drop, no probing.)
- [ ] 5. Pick what to land; set must/should/want (both contexts). Respect max_musts
        (flag, don't silently exceed).
- [ ] 6. Read the target day's fixed commitments from Calendar; confirm read-back;
        ask about off-calendar duties (references/interview.md → Fixed duties).
- [ ] 7. SCHEDULE WORK (packer): confirm each WORK chunk carries its est0 line (set at
        intake; references/template.md) — don't rewrite est0. Build packer input
        (schemas/packer-input.schema.json) from the contexts.work config + the target day's
        WORK chunks + commitments, then run:
            python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pack_schedule.py input.json
        Personal items NEVER enter packer input. Review scheduled / overflow /
        summary.warnings with the user. Adjust, re-run until it fits.
- [ ] 8. SCHEDULE PERSONAL (light, no packer): give each committed personal item a due
        time + reminder. Ask the user "when"; on defer, derive a sensible time from a live
        read of the day — the WORK blocks just packed, the personal items from step 3, and
        the Calendar commitments — placing it in an open slot that doesn't stack on an
        existing anchor or collide (references/heuristics.md → Personal).
- [ ] 9. Confirm the proposal with the day's WORK blocks and PERSONAL reminders shown as
        two clearly separated sections. On yes, write to TickTick (kind TEXT):
          - work blocks: startDate/dueDate/isAllDay:false/timeZone/reminders +
            focusSummaries.estimatedPomo, intensity tag + must/should/want + `ai`.
          - personal: dueDate/isAllDay:false/timeZone + reminders (the reminder.triggers
            array) + `ai` (+ must/should/want if set); NO focusSummaries, NO intensity tag.
        RE-READ to confirm parentId links (the create response is stale; references/template.md).
- [ ] 10. State the single first physical action so starting is frictionless.
```

## References

Read when the step points to them; each is self-contained:

- `${CLAUDE_PLUGIN_ROOT}/references/heuristics.md` — estimation, AI discount, time-blocking, reconciliation, calibration.
- `${CLAUDE_PLUGIN_ROOT}/references/template.md` — task template + TickTick/Linear/Calendar field mappings + packer I/O.
- `${CLAUDE_PLUGIN_ROOT}/references/interview.md` — question banks per mode.
- `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md` — the lean task writing contract.
- `${CLAUDE_PLUGIN_ROOT}/schemas/` — JSON Schema for tasks and packer I/O.

New work with no tree yet → use `butler:intake` first. Mid-day slip → `butler:reschedule`.
