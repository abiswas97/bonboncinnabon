# Heuristics

The reasoning the skill applies. Prefer judgment over rigid rules — these explain
*why*, so adapt when a case warrants it.

## Contents

- Contexts — derive from project, confirm, then route (work vs personal)
- Decomposition (work) — work into startable pipeline-stage chunks
- Personal — free-form steps (or none) + light scheduling
- Estimation — points as complexity, the AI discount, paired verification
- Buffering — where the slack actually lives (read this; it's easy to double-count)
- Time-blocking — placing the target day's chunks
- Reconciliation — capped, no-blame
- Calibration — what TickTick can and can't tell you

## Contexts — derive, then confirm

Every task belongs to a **context**, defined in `config.yaml` under `contexts`. The
context decides how a task is decomposed and scheduled. Resolve it the same way
everywhere (intake, decompose, plan):

- **Derive from the project.** Look up the task's TickTick project in `contexts.<name>.projects`. `Plate`/`Promo Track` → work; `Life`/`Photo`/`Finance`/`Relationships`/`Medical`/`Projects` → personal.
- **Confirm, never silent.** State the derived context and confirm in one line ("This is in Life, so personal — treat it as personal?"). Proceed only on a yes.
- **Unmapped project → ask.** A project listed under no context is not a guess to make; ask which context applies.
- **Missing context on an existing chunk = work.** Chunks created before 0.3.0 have no `context` field; read them as work (full pipeline model). Applies on every read.

What each context changes:

| | work | personal |
|---|---|---|
| decompose | pipeline stages (research→deploy) | free-form steps, or none |
| axes | stage, intensity, ai_discount, est0 | priority, est0, reminder |
| schedule | packed (focus window) | light (due time + reminder) |

## Decomposition (work) — pick stages from the pipeline

Work chunks are **pipeline stages**, not freeform steps. The `pipeline` in
`config.yaml` (under `contexts.work`) is the menu (research → db → backend →
frontend → review → address-comments → qa → deploy), each carrying default
`intensity`, `ai_discount`, and a derived `activity`.
This is deliberate: a predictable template removes the "what are my chunks?"
decision every ticket, which is the executive-function win. The AI's guessing moves
out of the title and into the body, where it's lower-stakes and easy to correct.

- **The pipeline is a MENU, not a checklist.** Pick only the stages this ticket needs; skip the rest. A valid plan can be a single stage (a spike = just `research`). Do **not** materialize an empty/ceremonial stage (no `db` on a FE-only ticket, no `deploy` under CD-on-merge).
- **Hybrid: add ad-hoc chunks** for genuine off-pipeline work (mark `ad_hoc`, pick the closest stage). Don't force-fit; don't invent stages.
- **Title = stage + short qualifier.** "Backend: pricer API + carry-back", not a bare "Backend changes" (which blurs across tickets in a flat view). The *concrete first action* goes in the body (`Where:` / first physical action), not the title — that preserves startability while keeping titles stable.
- **Session-sized; split oversized stages with the qualifier.** A big `backend` becomes two `backend` chunks ("Backend: pricer API", "Backend: carry-back") — same stage (so calibration still groups), different qualifier.
- **2–6 chunks.** After selecting stages, merge adjacent thin ones (fold a tiny `db` into `backend`) to land in range. Fewer than 2 = a single action; a wall of stages discourages use.
- **Non-feature work maps onto the same pipeline:** a BUG = `research` ("reproduce X", `none`) → the fix stage → `qa`; a REFACTOR/CHORE = the build stage (often `discounted`) + `review`; a one-liner = a single ad-hoc chunk. No special mini-pipelines.
- **Today-only scheduling.** Create the whole tree so it persists; only the target day's chunks get times (that's `butler:plan`).

The Linear ticket's acceptance criteria are **input** to filling each stage's body,
never mirrored as chunks.

## Personal — free-form steps (or none) + light scheduling

Personal tasks are NOT shredded into a pipeline. Default to **not** decomposing.

- **Free-form, 2–4 steps, only if multi-step.** When a personal task genuinely has separable sittings ("plan the trip" = pick dates → book flights → book stay), break it into 2–4 concrete steps. No stage/intensity/ai_discount — just a title, optional priority (must/should/want), optional light `est0`, and a reminder when scheduled.
- **Single action → don't decompose.** Most personal tasks ("book the dentist") are one action. Leave them whole and offer to schedule/cue. Over-shredding a personal errand is the failure mode; resist it.
- **Titles still follow the task contract**, minus the `stage:` prefix: lean imperative verb + object, sentence case, no emoji, no trailing period, ≤70.
- **Light scheduling — no packer.** A personal chunk never enters packer input. It gets a `dueDate` + a `reminders` TRIGGER (see template.md), not a focus block. It does not consume `focus_cap_min`, has no intensity/`deep_first` ordering, and doesn't contend for the work window.
- **Choosing "when".** Ask the user. On defer, derive a sensible time from a LIVE read of the target day — the day's existing TickTick timed items (`list_undone_tasks_by_date`) plus Calendar events — and place the reminder in an open slot that doesn't stack on an existing anchor or collide with a commitment. There is no fixed default time.

## Estimation — points as complexity, the AI discount

**Points are complexity, effort, and uncertainty — never a time budget.** Use the
points envelope only to set expectations and shape the tree (higher points →
multi-day, more stages, more slack). The `points_calibration` map in config is a
deliberately coarse envelope, not a points→hours formula.

**Estimate each chunk fresh, in focus-minutes** (`est0`), based on the stage and
its qualifier. Anchor on the block cadence (`max_block_min`) and on your own
history for that **stage** (see Calibration) — not on the gut alone, which is
exactly the faculty time-blindness impairs. `est0` is set at intake and never
overwritten.

**The selective AI discount** seeds from the stage default (`contexts.work.pipeline`
in config) and is overridable per chunk:

- **`discounted`** (AI compresses): the build stages — `db`/`backend`/`frontend` — when on code you already understand; mechanical refactors, codemods, boilerplate.
- **`none` / `premium`** (AI doesn't reliably help, and on unfamiliar/coupled code can slow an experienced dev — METR 2025): `research` (ambiguous-spec resolution, cross-system tracing), `review` (verifying AI output is the hidden cost), decisions needing people.

Override the default when reality differs: a `backend` chunk that requires tracing
existing coupling first is `none`, not `discounted`. The discount keys on
**codebase familiarity and coupling**, not the stage alone.

**Verification is its own stage, not a per-chunk pairing.** The `review` stage
("submit PR + AI-assisted review", `intensity: deep`, `ai_discount: none`) is where
AI output gets verified — METR's hidden cost. Include it whenever the ticket has
`discounted` build stages, so a heavily-AI day still budgets review time.

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
- **Intensity-aware ordering.** `deep` work goes in the earliest (freshest) slots by default; `shallow` batches later. Within an intensity tier the packer clusters by *activity* — derived from `stage` (build → verify → comms → admin) — then by pipeline order (research → … → deploy) as a low-priority tiebreak. Activity is never hand-tagged.
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

- **Never duplicate what already exists (the default).** Before scheduling anything, read BOTH the open tasks AND the recurring habits (`list_habits`) for the target day. A routine already covered by a habit (reading, pet care, finance checks, the planning ritual) or an existing task is ALREADY handled — do NOT create a task for it; it just fires. Schedule only the GAP: genuinely net-new work, plus existing DATELESS tasks (which get a date, never a recreated copy). Dedupe by title/ticket against what's already there.
- **Default: no blame.** Anything not done just re-surfaces with "keep or park?". Parked chunks lose their date and get the `parked` tag — no "why" demanded.
- **Ask why for at most the 1–2 most-slipped chunks**, not the whole list, and only escalate to "want to look at why this keeps slipping?" when a *specific* chunk has slipped repeatedly.
- Route the answer when you do ask:
  - **blocked** → keep, note the blocker, surface something else, flag if aging.
  - **underestimated** → re-block bigger, or split.
  - **too vague / didn't know where to start** → decompose further now (rewrite to verb + first action).
  - **low energy / interrupted / out of day** → just re-block; if it keeps slipping, shrink it or move it to a sharper part of the window.
- Catch the chunk that's finished but never ticked — confirm and mark done.

## Calibration — what TickTick can and can't tell you

Calibration works only because the original estimate (the immutable `~<n>m` line,
`est0_min`) is stored and never overwritten on re-blocking, and only if the focus
timer is run.

- Compare the `~<n>m` estimate to actual focus minutes (`focusSummaries` / `get_focuses_by_time`), grouped by **stage** (parsed from the title prefix). Over a few weeks, surface drift in one sentence during reconciliation ("backend chunks have run ~1.5× your estimate lately"). Stage is a better reference class than the old 15-value taxonomy — fewer classes fill with data faster.
- `research` and `backend` are high-variance (a 20-min trace vs a multi-hour spike); report their drift cautiously.
- This is reference-class forecasting: trust the pattern for that stage over the gut.
- Keep it lightweight — a sentence, not bookkeeping. Without the timer, say so honestly and fall back to a gut-check; don't pretend to data you don't have.
