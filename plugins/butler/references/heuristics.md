# Heuristics

The reasoning the skill applies. Prefer judgment over rigid rules — these explain
*why*, so adapt when a case warrants it.

## Contents

- Decomposition — work into startable chunks
- Estimation — points as complexity, the AI discount, paired verification
- Buffering — where the slack actually lives (read this; it's easy to double-count)
- Time-blocking — placing the target day's chunks
- Reconciliation — capped, no-blame
- Calibration — what TickTick can and can't tell you

## Decomposition — work into startable chunks

The Linear ticket already has acceptance criteria and checklists. Do **not**
mirror them. Produce the *cognitive arc of doing the work* — the steps a person
actually moves through.

- **Session-sized.** Each chunk completable in roughly one focused sitting (~25–90 min). Too big → split; several tiny → merge.
- **Startable, not just titled.** Start each chunk with a concrete verb and a done-signal (`task-contract.md`). Always surface the very first physical action for the day's first chunk — starting is the hardest moment; name the keystroke-level next step.
- **Pipeline stages are natural boundaries.** Real work moves groom → spike → build → self-review → address PR comments → QA/verify → deploy. Many chunks are non-coding. Don't pretend a ticket is one coding session.
- **2–6 chunks.** Fewer than 2 = a single action; more than ~6 = the ticket is too big, stage it rather than shred it. Over-decomposition has its own cost (you plan the plan, and a wall of trivial chunks discourages use).
- **Today-only scheduling.** Create the whole tree so it persists; only the target day's chunks get times.

## Estimation — points as complexity, the AI discount, paired verification

**Points are complexity, effort, and uncertainty — never a time budget.** Use the
points envelope only to set expectations and shape the tree (higher points →
multi-day, more grooming/spike chunks, more slack). The `points_calibration` map
in config is a deliberately coarse envelope, not a points→hours formula.

**Estimate the target day's chunks fresh, in focus-minutes**, based on the nature
of *that chunk*. Anchor on the block cadence (`max_block_min`) and on your own
history for that chunk_type (see Calibration) — not on the gut alone, which is
exactly the faculty time-blindness impairs.

**The selective AI discount** (you execute with AI; set per chunk, in `ai_discount`):

- **`discounted`** (AI compresses): scaffolding/CRUD, boilerplate tests, mechanical refactors, codemods, and wiring **on code you already understand**.
- **`none` / `premium`** (AI doesn't reliably help, and on unfamiliar/coupled code can slow an experienced dev — METR 2025): resolving ambiguous specs, cross-system tracing/debugging ("where does this value come from"), decisions needing people, coordination, and **reviewing/verifying AI output**.

The discount keys on **codebase familiarity and coupling**, not the verb alone.
"Wire a field through an API" is `discounted` only when the surrounding code is
understood; if you must first trace existing coupling to do it, it is `none`.

**Pair every `discounted` build chunk with a verify chunk.** METR found the hidden
cost of AI is reviewing/cleaning its output. The discount and the review are
causally linked, so they're created together: a discounted build → a paired
`review` chunk at no discount. A heavily-AI day still budgets verification time.

## Buffering — where the slack actually lives

Be honest: the day has **several** day-level reducers, not one. The packer applies
all of them; none are per-chunk:

1. `focus_cap_min` — a ceiling on committed focus inside the window.
2. `day_slack_pct` — a share of free time left open for interrupts/overrun.
3. `transition_min` after each block.
4. recharge breaks after every `recharge_after_blocks`.

Per-chunk estimates therefore stay **tight** (points + the AI discount already
encode complexity; multiplying each chunk by a buffer would triple-count). If the
day comes out too light to feel worth using, lower `day_slack_pct` or raise
`focus_cap_min` — don't pad the chunks.

## Time-blocking — placing the target day's chunks

The packer (`scripts/pack_schedule.py`) enforces this; the logic here explains it.

- **Subtract fixed commitments first.** Calendar events + off-calendar duties are removed before placing. Meetings also act as natural breaks.
- **Intensity-aware ordering.** `deep` work goes in the earliest (freshest) slots by default; `shallow` batches later. Within an intensity tier the packer clusters by *activity* — derived from `chunk_type` (build → verify → comms → admin) — to cut context-switching. Activity is never hand-tagged.
- **Intensity is focus, not activity.** A deep code review or verifying coupled AI output is `deep` (it needs a fresh slot), even though its activity is "verify". Judge the focus a chunk demands, not what kind of work it is.
- **No reliable peak.** Deep-early is a *default*, not a law — there's no fixed daily energy peak to assume. When you flag low/high energy at plan time, reorder accordingly (the `deep_first` config and per-chunk `intensity` are the levers).
- **Block length.** Blocks run to ~`max_block_min` (~50). A chunk longer than one sitting stays *one* block with a pomo estimate so the in-app timer handles the mid-break — don't split one chunk into two calendar entries. Genuine deep-flow chunks may warrant a longer block; raise `max_block_min` for those rather than fragmenting.
- **Honest capacity.** Cap committed focus and leave slack. A 100%-packed day guarantees a miss.
- **Stick to three.** More than `max_musts` substantial musts is flagged, not silently scheduled.
- **Never silently drop a must.** Musts are ordered and placed first; a must that physically can't fit surfaces as overflow with a loud warning — never quietly cut.

## Reconciliation — capped, no-blame

When previously-scheduled chunks weren't done, the reason is a planning signal —
but **interrogating every unfinished chunk daily is the thing that makes people
abandon time-blocking**. So:

- **Default: no blame.** Anything not done just re-surfaces with "keep or park?". Parked chunks lose their date and get the `parked` tag — no "why" demanded.
- **Ask why for at most the 1–2 most-slipped chunks**, not the whole list, and only escalate to "want to look at why this keeps slipping?" when a *specific* chunk has slipped repeatedly.
- Route the answer when you do ask:
  - **blocked** → keep, note the blocker, surface something else, flag if aging.
  - **underestimated** → re-block bigger, or split.
  - **too vague / didn't know where to start** → decompose further now (rewrite to verb + first action).
  - **low energy / interrupted / out of day** → just re-block; if it keeps slipping, shrink it or move it to a sharper part of the window.
- Catch the chunk that's finished but never ticked — confirm and mark done.

## Calibration — what TickTick can and can't tell you

Calibration works only because `est0` is stored immutably (re-blocking would
otherwise destroy the original estimate) and only if the focus timer is run.

- Compare `est0` to actual focus minutes (`focusSummaries` / `get_focuses_by_time`), grouped by `type` (chunk_type). Over a few weeks, surface drift in one sentence during reconciliation ("trace chunks have run ~1.5× your estimate lately").
- This is reference-class forecasting: trust the pattern for that chunk_type over the gut.
- Keep it lightweight — a sentence, not bookkeeping. Without the timer, say so honestly and fall back to a gut-check; don't pretend to data you don't have.
