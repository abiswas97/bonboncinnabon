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

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml` — the only user-specific surface — then run
the config preflight (references/template.md → Config preflight; migrate if behind,
error if ahead). Resolve TickTick project and tag names → ids at runtime
(`list_projects` / `list_tags`).
Load deferred MCP tools with tool_search before use (TickTick, Google Calendar).

## Core rules

1. **Schedule only the target day.** Put start/due + reminders on the target day's chunks only; everything else stays dateless.
2. **Context-aware.** WORK chunks go through the packer (focus blocks). PERSONAL items get a light due time + reminder and NEVER enter packer input. Read a chunk's context from its project (`references/heuristics.md` → Contexts); a chunk with no context is work. Keep the two visually separated in the proposal.
3. **Points are complexity, not time.** Never divide Linear story points into hours.
4. **Confirm before writing.** Show the proposed blocks + the packer summary, get a yes, then write.
5. **Lean, human tasks.** Follow `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md`. Every butler-created task carries the `ai` tag.
6. **Never assume a ticket.** Touch Linear only when the user names an explicit ID this turn.
7. **Never duplicate what already exists.** Reconcile against open tasks AND recurring habits before scheduling. A routine that already fires as a habit (or an existing task) is already handled — do NOT create a task for it. Schedule only the gap: net-new work, and a dateless existing task gets a date rather than a recreated copy (`references/heuristics.md` → Reconciliation).
8. **Breaks are constraints, never tasks.** Reserve lunch + flexible decompress breaks as packer fixed-commitments (gaps) the packer subtracts — scaled to load, deferred when one would interrupt an in-progress block. Never materialize a break as a TickTick task (`references/heuristics.md` → Buffering).
9. **Catch overcommitment, never cause it.** The burnout check is a *question*, never an action: it may surface a no-blame observation and ask, but never adds a task, auto-inserts rest, or reschedules unasked (`references/heuristics.md` → Pacing; `references/accommodations.md`).

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
        recurring habits (`list_habits`). Routines already covered by a habit (e.g. exercise,
        reading, a daily review, the planning ritual) or an existing task are ALREADY
        handled — never recreate them; they just fire. Pull MORE personal tasks only if
        the user asks — keep the daily ritual low-noise.
- [ ] 4. Reconcile WORK — CAPPED and NO-BLAME (references/heuristics.md → Reconciliation;
          references/accommodations.md → non-punitive): re-surface a miss as a neutral event
          ("this didn't happen") + "keep or park?" (park = drop date + `parked` tag) + one small
          next step — never a verdict. If the user spirals, surface the facts ("1 of 5 slipped,
          4 done") and offer one small re-engagement rather than scrapping the plan. Ask "what
          got in the way?" for at most the 1–2 most-slipped chunks; escalate to "why does this
          keep slipping?" only on repeat slips; catch chunks finished-but-not-ticked.
          (Personal items just keep or drop, no probing.)
- [ ] 4b. BURNOUT CHECK (references/heuristics.md → Pacing): compute the overload signal for
          the window and, only on its RISING EDGE, surface ONE no-blame observation and ask
          whether to keep the next day lighter. Act only on a yes (offer to lighten / defer /
          protect a recovery gap / offer low-energy mode at step 5). Stay silent otherwise, and
          on thin history. NEVER add a task, auto-insert rest, or reschedule unasked (Core rule 9).
- [ ] 5. Pick what to land; set must/should/want (both contexts). Respect max_musts
        (flag, don't silently exceed). Apply references/accommodations.md → mastery+pleasure
        and flexibility-with-spine: if the day is all obligation, note the imbalance and OFFER
        a blend — never invent or auto-add a pleasure task (Core rule 7 never-duplicate /
        never-invent; the user names personal items). Frame partial completion as a good
        outcome (offer a graded smaller version, not a binary drop). LOW-ENERGY MODE
        (references/heuristics.md → Pacing): if the user signals low energy at any point, OR
        opts into it when the burnout check fired, reduce to ~one mastery + one pleasure item
        leading with the smallest concrete step — never defer-all, never auto-apply.
- [ ] 6. Read the target day's fixed commitments. Detect a connected Google Calendar MCP;
        if present, read the target day's events from the calendars named in `config.yaml`
        `calendar.calendars` (default primary) as fixed commitments — the source lives in
        config, don't re-ask. Fallback ladder, NON-BLOCKING: no MCP → run calendar-blind
        but STATE it + suggest connecting one; events scattered across many calendars/accounts
        → suggest consolidating to one account. Then RESERVE breaks (see step 7) and confirm
        read-back; ask about off-calendar duties (references/interview.md → Fixed duties).
- [ ] 7. SCHEDULE WORK (packer): confirm each WORK chunk carries its est0 line (set at
        intake; references/template.md) — don't rewrite est0. BEFORE packing, reserve breaks
        as packer FIXED-COMMITMENTS placed around the day's meetings: a lunch
        (`contexts.work.breaks.lunch_min`, default 45) and one-or-more decompress breaks
        (`decompress_min`, default 30) scaled to the focus load; DEFER a break that would
        interrupt an in-progress focus block. Breaks are NEVER created as TickTick tasks (they
        are constraints/gaps); adjustable or skippable per plan (references/heuristics.md →
        Buffering). Build packer input (schemas/packer-input.schema.json) from the
        contexts.work config + the target day's WORK chunks + commitments + reserved breaks,
        then run:
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
- [ ] 10. State the single first physical action as an action-first if-then cue ("when
        [trigger], start by [action]") — one observable physical verb tied to its start
        trigger, never an outcome noun (references/accommodations.md → action-first, if-then-cue).
```

## References

Read when the step points to them; each is self-contained:

- `${CLAUDE_PLUGIN_ROOT}/references/heuristics.md` — estimation, AI discount, time-blocking, reconciliation, calibration.
- `${CLAUDE_PLUGIN_ROOT}/references/template.md` — task template + TickTick/Linear/Calendar field mappings + packer I/O.
- `${CLAUDE_PLUGIN_ROOT}/references/interview.md` — question banks per mode.
- `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md` — the lean task writing contract.
- `${CLAUDE_PLUGIN_ROOT}/references/accommodations.md` — how butler speaks to a user under EF load; apply at miss-handling, selection, next-action, and tone. Single source, don't restate.
- `${CLAUDE_PLUGIN_ROOT}/schemas/` — JSON Schema for tasks and packer I/O.

New work with no tree yet → use `butler:intake` first. Mid-day slip → `butler:reschedule`.
