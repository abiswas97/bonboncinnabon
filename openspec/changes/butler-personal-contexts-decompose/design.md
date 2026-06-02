## Context

butler 0.2.0 is a single-context (work) planner: `config.yaml` holds one
`work_project`, one `pipeline` of stages, and one `work_window`; every chunk is
stage-tagged and packed by `scripts/pack_schedule.py`. The packer itself is
domain-agnostic — it sorts and places blocks given priority/intensity/activity and
a focus window. 0.3.0 adds a `personal` context that reuses the durable-task-tree
and TickTick-write machinery but skips the stage axes and the packer in favor of a
light time + reminder. State lives only in TickTick + Google Calendar; Linear is
read-only and explicit-ID only. The user's tenets (DRY, data-driven, single source
of truth, small blast radius) require that "personal" be config + a lighter flow,
not a parallel engine.

## Goals / Non-Goals

**Goals:**
- One config-driven `contexts` model; context derived from project, always confirmed.
- A `decompose` skill for existing TickTick tasks, context-aware, interview-gated.
- A real hard gate on the intake/decompose interview.
- `plan`/`reschedule` that schedule work via the packer and personal via light reminders, in one flow.
- Zero behavior change for existing work trees (missing `context` = work).

**Non-Goals:**
- No personal focus window, personal packer, or personal capacity model (YAGNI).
- No change to the packer algorithm or `packer-input.schema.json`.
- No multi-day personal scheduling; day-at-a-time stays.
- No new external state or side files; no Linear writes.

## Decisions

### D1: Work scheduling config folds under `contexts.work` (correct structure)

Add a `contexts` map to `config.yaml`. Each entry declares `projects`,
`decomposition`, `axes`, `scheduling`, plus its own scheduling config. Fold ALL
work-owned settings under `contexts.work.*` — `work_window`, `pipeline`,
`capacity`, `intensity_tags`, `recharge_tag`, `executes_with_ai`,
`points_calibration` — and rename `work_project` → `contexts.work.default_project`.
Personal-owned settings live under `contexts.personal.*`.

Settings that belong to **no single context** stay top-level: `timezone`,
`planning_project` (the Ops/ritual location, used to plan both contexts),
`priority_tags` (both contexts commit must/should/want), `ai_tag` and `parked_tag`
(applied to all generated tasks), and `ritual`. (`intensity_tags` and
`points_calibration` are work-only — they fold under `contexts.work`, not
top-level — since personal tasks have no intensity axis and no story-points
envelope.)

- `contexts.work.projects` is the single source of truth for "is this work?".
- `contexts.work.default_project` is where `intake` creates a new work unit; it MUST
  be a member of `contexts.work.projects` (documented invariant).
- The packer **script** (`pack_schedule.py`) is unaffected — it reads its generated
  `input.json`, not `config.yaml`. Only the skill step that **builds** packer input
  changes its read paths from top-level to `contexts.work.*`. All 19 packer tests
  stay green.

*Rationale:* correctness over expedience (user tenet) — work scheduling settings are
work-context-owned and belong inside the context; the flat layout's "settings in
two mental places" is exactly what we remove. *Cost:* mechanical rewrite of the
packer-input builder's config reads and skill references; no behavior change.

*Alternative considered:* keep packer keys top-level for a smaller diff. Rejected by
user preference for the correct structure.

### D2: Context detection = derive-by-project, then confirm (never silent)

A small shared resolution step (documented in `references/heuristics.md`, used by
`decompose` and `plan`): look up the task's project in `contexts.*.projects`,
state the derived context, and confirm. Unmapped project → ask which context. This
is the single rule; every skill calls it the same way. No keyword/title heuristics.

*Alternative considered:* infer silently and let the user correct later. Rejected:
the handover mandates explicit confirmation; silent misclassification would packer
a personal errand or vice-versa.

### D3: Schema uses JSON Schema `if/then` keyed on `context`

In `chunk-task.schema.json`: add `context` enum `[work, personal]`. Replace the
flat top-level `required` (which currently hard-requires the work axes) with
conditional logic:
- base `required`: `[id, title, context, kind, ai_generated]`
- `if context == work` → `then required: [stage, intensity, ai_discount, est0_min]`
- personal needs no extra required fields; `priority`, `est0_min`, `reminder`
  optional.

`context` defaults to `work` is **not** expressed in the schema as a JSON default
(that would silently inject the field); instead the *reader* treats an absent
`context` as work (D7). Keep `additionalProperties: false`; add `reminder` to
properties.

*Alternative considered:* two separate schemas (work-chunk, personal-chunk).
Rejected: duplicates the shared fields (id/title/kind/ai_generated/priority/
est0_min) and the contract, violating DRY; `if/then` keeps one file.

### D4: Personal scheduling = TickTick dueDate + reminder, no packer

Personal chunks never enter packer input. `plan` assigns a personal item a
`dueDate`/`isAllDay:false`/`timeZone` and a `reminders` TRIGGER array anchored to
that date (per the verified API facts). No `focusSummaries`, no intensity tag, no
must/should/want contention with the focus cap. The personal "when" is asked
conversationally; fallback is a config default time (D5).

### D5: Personal "when" — ask; on defer, derive from a live read of the day

Resolve the open question (always-ask vs fixed config default) as: **ask the user;
on defer, the skill picks a sensible time by reading the live state of the target
day.** There is NO hardcoded `default_reminder` config value — a fixed time would
dump every deferred personal item into the same slot regardless of what the day
actually looks like. The skill's judgment over live data is the default.

Concretely, to place a deferred personal reminder the skill SHALL:
- query TickTick for the target day's existing timed items
  (`list_undone_tasks_by_date` scoped to the day) to see what reminders/tasks are
  already anchored, and
- read the target day's Google Calendar events,

then choose an open, sensible time that does not stack on an existing anchor or
collide with a commitment, and confirm it in one line. The same live read is what
`plan` uses when committing personal items for the day. A habitual slot the user
keeps choosing may be remembered to memory. No personal focus window is invented.

### D6: One unified "plan my day"; personal pulled scoped, not firehosed

`plan` stays a single flow (no context arg). Resolve the open question (pull all
personal projects every run?) as: **default to work + any personal task already
due/committed for the target day; pull more personal only on request.** This keeps
the daily ritual low-noise. The proposal output renders two labeled sections (Work
blocks / Personal reminders). `reschedule` repacks only work; personal reminders
are kept/adjusted, never repacked.

### D7: Missing `context` = work, enforced at read time

Every skill that reads a chunk treats absent `context` as `work` before applying
logic. This is the back-compat guarantee for the ING-165 tree and all 0.2.0
chunks. It lives in the read step, not the schema (D3).

### D8: `decompose` re-parents the existing task; intake still owns new units

`decompose` never creates a new top-level unit. The resolved existing task becomes
the parent (title/content optionally tidied to parent form), and chunks are created
as children with `parentId` + `kind: TEXT` + `ai` tag, then re-read to confirm
`childIds` (create response is stale). `intake` remains the only skill that creates
a brand-new work unit from a Linear ticket or described work. Shared decomposition
heuristics and the interview live in `references/` so both skills read one source.

### D9: Promo Track is work

Resolve the open question: `Promo Track` joins `contexts.work.projects`. No third
context until a real need appears (YAGNI).

## Risks / Trade-offs

- **[`work_project` duplicated in `contexts.work.projects`]** → Documented invariant
  + a config comment that `work_project` must be a member; low churn, two concepts
  (membership vs default create-target) genuinely differ.
- **[`if/then` schema is easy to get subtly wrong]** → Add explicit validation
  fixtures: a valid work chunk, a work chunk missing `stage` (must fail), a valid
  personal chunk. Verify with the schema validator during implementation.
- **[Personal noise in the daily plan]** → D6 scopes personal to already-due +
  on-request; revisit only if the ritual feels heavy.
- **[Reminder needs a date anchor]** → Personal reminders are only written once the
  task has a `dueDate`; never emit a TRIGGER on a dateless task.
- **[Model skims the hard gate again]** → The gate is encoded as a red-flags
  "do not proceed until X" block AND as spec scenarios, not a single checklist line.
- **[Context misclassification]** → Mandatory confirm (D2) catches it before any write.

## Migration Plan

- Additive only. Existing work trees keep working via D7 (no backfill needed).
- `config.yaml`: add `contexts` + `contexts.personal.default_reminder`; add
  `Promo Track` to work projects; leave packer keys untouched.
- Schema change is backward-compatible for readers (absent `context` = work) and
  forward-compatible for the packer (input schema unchanged).
- Rollback: revert the plugin version; no persisted state migration to undo
  (personal chunks are ordinary TickTick tasks).
- Release per handover: bump `plugin.json` + marketplace entry (kept equal), update
  both CHANGELOGs, `claude plugin tag ./plugins/butler` → `butler--v0.3.0`, push
  branch + tag.

## Open Questions

- What signals the agent weighs when deriving a deferred personal time (nearest free
  calendar gap vs end-of-day vs task nature), and whether a repeatedly-chosen slot
  should be remembered to memory — to refine during implementation.
- Whether `decompose` tidying the parent's title/content should be automatic or
  always confirmed (lean: confirm, consistent with "confirm before writing").
