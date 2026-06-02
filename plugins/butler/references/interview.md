# Interview banks

Thorough but conversational. Ask, listen, adapt — never fire a wall of questions,
and skip anything already answered (by the user, the ticket, or TickTick). One
main thread at a time. The aim of every interview is a small, committed plan for
the **target day** (today when planning in the morning, tomorrow when planning in
the evening), not a multi-day schedule.

## Contents

- Target day (shared, ask first when ambiguous)
- Hard gate (shared, before decomposing) — do not proceed until X
- Intake
- Decompose
- Plan / reconcile
- Reschedule
- Fixed duties (shared)

## Hard gate (shared) — do not proceed until X

Both Intake and Decompose MUST clear this gate before producing or writing ANY task.
It is a real stop, not a checklist line you can skim. Decomposition that skips it is
a defect.

**DO NOT decompose, create, or write a single task until you have confirmed, out
loud with the user:**

- **Intent / done-criteria** — what "done" actually looks like for this task.
- **Prior progress** — fresh start, or already part-done? (Already-done work is not re-created.)
- **Shape** — is this genuinely multi-step, or a single action? (A single action is NOT decomposed.)

Skip questions already answered by the user, the ticket, or TickTick — but still
CONFIRM these three, even when they seem obvious. If any is unresolved, ask; do not
infer and proceed. (Rationale: a mandated-but-skimmable step gets skipped — this is
the stop that prevents shredding work that was never understood.)

## Target day (shared)

Resolve which day you're planning before anything else:
- Explicit ("plan tomorrow", "plan today") wins.
- Otherwise infer from time of day (evening → tomorrow, daytime → today) and confirm in one line: "Planning tomorrow, yeah?"

## Intake

Goal: understand the human shape of the work, then narrow hard to what to land on the target day.

**Frame the work**
- (Linear ID given) "Here's what <ID> says — still accurate, or has it drifted?" Confirm scope before decomposing.
- (Described) "Say a bit more about what 'done' looks like."
- "Fresh start, or already begun part of it?"

**Surface the real shape**
- "Which parts are clear, which are still fuzzy?" (Fuzzy → a grooming/spike chunk first.)
- "Anything blocked, or needing a decision from someone else?"
- "A spike or investigation hiding in here before you can build?"
- "Riskiest / most uncertain part?" (More uncertainty → more slack, expect re-planning.)

**Narrow to the target day**
- "What do you want to actually land that day?" Keep pulling until it's a small, concrete set.
- "Of those, which need deep focus vs are shallow?" (sets intensity; stage defaults seed it; activity is derived from stage)
- "Which will you do with AI?" (sets ai_discount; include a `review` stage when there are discounted build stages)
- "What's the very first thing you'd touch?" (the first physical action)

**Estimate the target day's chunks** (with the user, applying the AI discount)
- "Roughly how long if it goes normally?" Then sanity-check: mechanical/AI-amenable → trim; tracing/ambiguous/decision/review → don't trim.

Then read Calendar (Fixed duties), pack, review, confirm, write.

## Decompose

Goal: break down a task that ALREADY exists in TickTick (work or personal),
interview-first. Clear the **Hard gate** before any decomposition.

**Resolve the task**
- (Named) "Is this the one — '<title>' in <project>?" Confirm the match before touching it.
- (Not named) "Here are tasks with no breakdown yet: … which do you want to work through?" (undecomposed = no `childIds`.)

**Confirm context** (heuristics → Contexts)
- "That's in <project>, so <context> — treat it as <context>?"

**Already split?**
- "It already has these chunks: … want to refine or fill a gap?" Augment; never duplicate existing chunks.

**Then the Hard gate** (intent / prior progress / single-vs-multi), then decompose per context:
- work → pipeline stages (use the Intake "surface the real shape" + "narrow" questions for stages, intensity, AI, first action).
- personal → 2–4 free-form steps, or conclude it's a single action and just schedule/cue it (don't over-shred).

**Confirm, then write**: the existing task becomes the parent; create chunks as
children (`parentId`, kind TEXT, `ai` tag); re-read to confirm `childIds`. Offer the
next step (`butler:plan` for work, a light reminder for personal).

## Plan / reconcile

Goal: reconcile open work honestly without nagging, then commit the target day.

**Reconcile (capped, no-blame — see heuristics)**
- Default: re-surface unfinished chunks with "keep or park?". Park = drop the date + `parked` tag, no "why" needed.
- Ask "what got in the way?" for at most the 1–2 most-slipped chunks. Route: blocked / underestimated / too vague / low-energy (heuristics → Reconciliation).
- Only escalate to "want to look at why this one keeps slipping?" when a chunk has slipped repeatedly.
- "Anything you actually finished but didn't tick?"

**Commit the target day**
- "What do you want to land?" Set must/should/want; respect the 3-musts flag.
- "Which need deep focus vs shallow?"

Then Fixed duties, pack, review, confirm, write the target day's blocks only.

## Reschedule

Goal: recompute the rest of *today* from where things actually are.

- "Where are you right now — what's done, what's left?"
- "Anything new that has to happen today?"
- "Any blocks already passed we should drop or shrink?"

Then re-read remaining chunks + remaining commitments, pack with `now` = current
time, review (overflow cascades, musts never silently dropped), confirm, update.

## Fixed duties (shared)

Read the target day's timed Calendar events in the window first, then confirm and fill gaps:
- "I see <events> on your calendar — still on?"
- "Lunch or a break planned, roughly when?"
- "Any commute or away-from-keyboard time?"
- "Any family or personal time to protect?"

These become the packer's `fixed_commitments`. Default to remembered habits (e.g.
a usual lunch window) but confirm rather than assume.
