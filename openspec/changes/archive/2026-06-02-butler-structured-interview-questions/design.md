## Context

butler's interviews live in `references/interview.md` as conversational question
banks; `intake`/`decompose` SKILL.md procedures point at them and the model renders
questions as prose. The harness exposes AskUserQuestion (structured option cards,
auto "Other", multi-select, ≤4 questions/call) — used by `superpowers:brainstorming`
— but butler never calls it. This change adopts it for the discrete forks only. It
is a presentation change: no task-model, schema, packer, or scheduling change.

## Goals / Non-Goals

**Goals:**
- Discrete interview decisions become tappable structured choices in intake + decompose.
- Open-ended prompts stay free text.
- Conversational discipline (one thread, no wall) preserved.
- No hard dependency on the tool (prose fallback for other harnesses).

**Non-Goals:**
- No `plan`/`reschedule` changes (target-day, must/should/want, keep-or-park) — later release.
- No new task fields, schema, or packer change.
- Not turning the whole interview into a form — open prompts stay open.

## Decisions

### D1: Annotate the question banks, don't fork them

`references/interview.md` stays the single source of the questions. Add a short
"Presentation" note at the top and tag each question line as **[choice]** (present
via AskUserQuestion with suggested options) or **[open]** (free text). This keeps
SSOT — the skills don't restate questions — and makes the structured/open split a
property of the bank, not duplicated logic.

*Alternative considered:* encode the option lists in the SKILL.md procedures.
Rejected: duplicates question text across files and drifts from the bank.

### D2: The model invokes the tool; the skill instructs, not the harness

A markdown skill can't "call" a tool by itself — it instructs the model to. So the
convention is phrased as an instruction the model follows: "for a [choice] question,
present it with AskUserQuestion using these suggested options; for [open], ask in
prose." This matches how `superpowers:brainstorming` does it.

### D3: Which questions are [choice] vs [open]

- **[choice]**: prior-progress (fresh / already-begun), shape (single action /
  multi-step), stage selection or tree-shape confirm (build as proposed / adjust
  granularity / fewer stages), decompose context (work / personal), augment-vs-leave
  when already split.
- **[open]**: done-criteria, first physical action, what's fuzzy / blocked, the
  riskiest part, estimate sanity-check. These elicit unbounded input.

Stage *selection* is agent-proposed then confirmed; the confirmation is the [choice]
(as demonstrated live in this session), not an enumeration the user hand-picks from
scratch.

### D4: Discipline ceiling, not target

AskUserQuestion allows 4 questions/call; interview.md's "one main thread at a time"
still governs. The convention explicitly says: batch only genuinely-related forks,
prefer one decision at a time. multiSelect is used only where a question is truly
multi-pick (rare here).

### D5: Graceful degradation

Every [choice] question is phrased so its prose form is still answerable (the option
labels read as a plain "X or Y?" question). On a harness without AskUserQuestion the
interview proceeds as today. So the tool is an enhancement, never a hard dependency.

### D6: Scope to intake + decompose

Only the two decomposition skills this release. `plan`/`reschedule` have their own
discrete forks (target-day, commitment tags, keep-or-park) that would benefit too,
but that's additional surface and testing — deferred (YAGNI), noted for a follow-up.

## Risks / Trade-offs

- **[Over-structuring kills the conversation]** → D3 keeps open prompts open; only
  finite-set decisions become choices.
- **[Wall of cards]** → D4 carries interview.md's one-thread rule into the convention.
- **[Tool-absent harness]** → D5 prose fallback; no hard dependency.
- **[Bank annotations drift from skill steps]** → D1 keeps questions in the bank
  only; skills reference, never restate.

## Migration Plan

- Additive, prose-only edits to `interview.md` + the two SKILL.md files. No code,
  schema, or config change.
- Rollback: revert the plugin version; nothing persisted changes.
- Release: bump `plugin.json` + marketplace entry (equal), update both CHANGELOGs,
  `claude plugin tag ./plugins/butler` → `butler--v0.4.0`, push branch + tag.

## Open Questions

- Whether to fast-follow with `plan`/`reschedule` structured forks in 0.5.0 (target
  day; must/should/want; keep-or-park) — likely yes, but out of scope now.
