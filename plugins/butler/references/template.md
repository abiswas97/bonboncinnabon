# Template and field mappings

How the plan is represented in TickTick, what to read from Linear and Calendar,
and the packer's I/O. Field names here are verified against the live TickTick MCP
and Linear MCP. Titles/descriptions follow `task-contract.md`.

## Contents

- Task template (parent + chunks)
- Idempotency and calibration
- TickTick field mapping (verified)
- Linear field mapping (read-only, explicit ID only) (verified)
- Calendar field mapping (read-only)
- Packer I/O
- One-time setup (tags, list rename, ritual habit)

## Task template

**Parent task** = one unit of work. `kind: "TEXT"`. Body goes in the **`content`**
field (not `desc` — `desc` is for `kind: CHECKLIST` only).

- `title`: human work-unit name, per the title contract (rewrite the Linear title; never copy it verbatim).
- `content`: the durable metadata block —
  ```
  Linear: <url>
  Ticket: <ID>   Points: <estimate.value>
  Branch: <gitBranchName>
  AC: in-ticket (Linear description "Acceptance Criteria" section)
  ```
  Omit any line that doesn't apply. The `Ticket:` line is the idempotency key.
- `tags`: `ai` always; plus the day's commitment tag (`must`/`should`/`want`) when the unit is active. Priority tags live on chunks, not the parent, when chunks are scheduled.
- `projectId`: the work list from config (default `Plate`); resolve name → id at runtime.
- `priority`: mapped from Linear (see Linear mapping).

**Chunk** = a child task, one focused sitting. `kind: "TEXT"`. Created for every
chunk in the tree. It is a **real subtask (`parentId`), never a checklist item** —
checklist items can't carry their own due date, reminder, or focus estimate.

- `title`: imperative verb + object + done-signal (title contract).
- `parentId`: the parent task's id. Create the parent first, capture its id, then create chunks with `parentId` set.
  - **The create response is stale** — it returns `parentId: null`/`childIds: null` even on success. ALWAYS re-read to confirm: `get_task_by_id` on the parent and assert `childIds` contains each child (or read each child and assert `parentId`). If the link didn't form, surface the failure — never silently fall back to checklist items (that would lose the per-chunk scheduling that is the whole point). The only safe fallback is leaving chunks as flat sibling tasks, still fully scheduled.
- `content`: the chunk's key:value block plus the immutable calibration line —
  ```
  Why: <one clause, if not obvious>
  Where: <file / symbol / endpoint>
  Done: <one observable signal>
  Ref: <PR / issue / ticket>
  est0: 45m  type: wire  ai: discounted
  ```
  The `est0` line is written ONCE at first scheduling and **never overwritten** on reschedule. `type` is the chunk_type; `ai` is the ai_discount value.
- `tags`: exactly one mode tag (`deep`/`shallow`/`comms`/`review`) + `ai` + the day's `must`/`should`/`want` when scheduled today.
- **Target-day chunks only**: set `startDate`, `dueDate`, `isAllDay: false`, `timeZone`, a `reminders` entry, and `focusSummaries: [{ "estimatedPomo": <n> }]`. All other chunks: no dates, so they stay unscheduled.
- **Auto-paired verify chunk**: when a build chunk has `ai_discount: discounted`, create a paired verify chunk (`chunk_type: review`, `mode: review`, `ai_discount: none`, `verify_of` = the build chunk id), e.g. "Review AI output for <thing>". The discount and its review cost are causally linked; budget both.

A recharge break is advisory (packer `breaks`); materialize it as a short
`recharge`-tagged task only if you want breaks visible. Off by default.

## Idempotency and calibration

- **Idempotency**: before Intake creates anything, search the work list for a parent whose `content` contains `Ticket: <ID>`. If found → resume that tree (route to plan), do not create a duplicate.
- **Calibration**: estimate accuracy comes from comparing the immutable `est0` against actual focus time. Read actuals from TickTick: `list_completed_tasks_by_date` / `filter_tasks` for completion, and `get_focuses_by_time` / the task's `focusSummaries` for real pomodoro/time-on-task. Group drift by `type` (chunk_type). This requires the in-app focus timer to be run; without it, calibration degrades to a one-line gut-check.

## TickTick field mapping (verified)

- `kind`: **`TEXT`** for work units + chunks. `NOTE`/`CHECKLIST` are the other values. **"TASK" is invalid** for tasks (it is only a *project* kind).
- `content`: task body for `TEXT`/`NOTE`. (`desc` is CHECKLIST-only — do not use it here.)
- `priority`: `0` none, `1` low, `3` medium, `5` high.
- `status`: `0` not done, `2` completed, `-1` abandoned.
- `startDate` / `dueDate`: ISO-8601 with offset, e.g. `2026-06-02T14:45:00+05:30`. No duration field — the start→due span IS the block length. Times are stored/returned in UTC; the offset is converted, not dropped.
- `isAllDay`: `false` for a scheduled chunk; unscheduled chunks carry no start/due.
- `timeZone`: IANA string from config (e.g. `Asia/Kolkata`).
- `reminders`: array of TRIGGER **strings** (not objects). `"TRIGGER:PT0S"` (at start), `"TRIGGER:-PT5M"` (5 min before), `"TRIGGER;RELATED=END:-PT15M"`. Multiple allowed. A reminder needs a date on the task.
- `repeatFlag`: recurrence string. `"RRULE:FREQ=DAILY"`, `"RRULE:FREQ=WEEKLY;BYDAY=MO,WE"`. Needs a `startDate` anchor. (Used by the ritual habit/task, not by work chunks.)
- `parentId`: parent task id for subtasks; `""` to detach. Stale on the create response — re-read to confirm (above).
- `focusSummaries`: array; set `focusSummaries: [{ "estimatedPomo": <n> }]` for the pomo estimate. (`estimatedDuration` in seconds also exists inside the summary; there is no top-level duration estimate.)
- `tags`: array of tag names. A name used before the tag exists attaches as a label but isn't a colored/managed tag until `create_tag` is called (see setup).

Tools: `create_task` (new), `update_task` (edit), `batch_update_tasks` (moving
several blocks on reschedule). Read with `filter_tasks` / `get_task_by_id` /
`list_completed_tasks_by_date`.

> Caveat: tags, project-groups, and columns are exposed by the MCP but are NOT in
> TickTick's documented public API. They work, but treat them as
> higher-breakage-risk than tasks/projects.

## Linear field mapping (read-only, explicit ID only) (verified against ING-165)

Pull only when the user names an ID this turn. Never write to Linear.

- `title` → informs the human parent title (rewrite, don't copy).
- `description` → single markdown string. **Acceptance criteria live INSIDE it** under a `## Acceptance Criteria` heading as `- [ ]` items — there is no separate AC field and no AC sub-issues. Use AC as decomposition input, not as chunks.
- `estimate` → **object** `{value, name}`, e.g. `{value: 1, name: "1 Point"}`; **absent when unestimated**. Read `estimate.value`; record as `Points: <value>`. Never convert to time.
- `gitBranchName` → present on every issue (e.g. `feature/ing-165-...`); `Branch:` line. (Field name is correct as-is.)
- `labels` → array of plain **strings**, mixing type labels with `v*` release tags (e.g. `["Bug","v2.26.1"]`). Use type labels as interview context; ignore the `v*` tags. Don't re-create as TickTick tags.
- `priority` → object `{value, name}` on Linear's scale (`0 None, 1 Urgent, 2 High, 3 Medium, 4 Low`). Translate to TickTick's `0/1/3/5`; the numbers do NOT line up.
- `url` → `Linear:` line.

## Calendar field mapping (read-only)

For the target day, read events overlapping the work window from the primary
calendar. Map each timed event to a busy interval `{title, start, end}` for the
packer's `fixed_commitments`. Ignore all-day events unless the user says one means
they're away. Confirm the read-back and ask about off-calendar duties (lunch,
commute, family, AFK) before packing. Never write to Calendar.

## Packer I/O

Build the packer input from config + the target day's chunks + commitments, then:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pack_schedule.py input.json
```

Input/output shapes are pinned in `schemas/packer-input.schema.json` and
`schemas/packer-output.schema.json`. Key points:

- `now`: the target day's window start when planning today/tomorrow; the current time for reschedule. Placement never starts before `now`.
- `estimate_min`: the fresh focus-minute estimate for the target day (after the AI discount).
- Map `scheduled[].block` → `startDate`/`dueDate`; `pomo_estimate` → `focusSummaries[].estimatedPomo`. Surface `overflow` and `summary.warnings`. `breaks` are advisory.
- Treat the output as the plan to CONFIRM with the user — don't hand-place blocks.

## One-time setup (tags, list rename, ritual habit)

Idempotent; check before creating. Resolve names → ids at runtime.

- **Mode + marker tags**: `deep`, `shallow`, `comms`, `review`, `ai`, `parked`. Try `create_tag` (with colors) — but the tag-write endpoint is undocumented and has been observed returning 500. If it fails, DON'T block: the tag still attaches to a task as a label the first time it's applied (it just won't be a colored sidebar tag until you create it in-app once). Surface the failure and continue.
- **Work list**: default `Plate` (rename from a prior name via `update_project` if needed — renaming preserves the tasks inside).
- **Ritual habit**: a "Plan the day" habit (`create_habit`) with a daily `repeatRule` (`RRULE:FREQ=DAILY`) and a reminder — the external cue that builds the rhythm. The habit lives on TickTick's Habit surface; the streak is the accommodation.
