# Interview banks

Thorough but conversational. Ask, listen, adapt — never fire a wall of questions,
and skip anything already answered (by the user, the ticket, or TickTick). One
main thread at a time. The aim of every interview is a small, committed plan for
the **target day** (today when planning in the morning, tomorrow when planning in
the evening), not a multi-day schedule.

## Contents

- Presentation (how to ask: [choice] vs [open])
- Target day (shared, ask first when ambiguous)
- Hard gate (shared, before decomposing) — do not proceed until X
- Intake
- Decompose
- Plan / reconcile
- Reschedule
- Fixed duties (shared)

## Presentation

This is the SINGLE SOURCE of the choice/open convention for every interview-driven
skill (intake, decompose, plan, reschedule). Each question in the banks below is
tagged for HOW to ask it:

- **[choice]** — a decision over a known, finite set. Present with the **AskUserQuestion** tool, offering the listed options (the tool adds an "Other" escape; use multiSelect only where noted).
- **[open]** — unbounded input. Ask in prose and accept a free-text answer. Never force these into options.

Discipline still holds: one main thread at a time, never a wall of cards. AskUserQuestion's 4-question batch is a ceiling, not a target — prefer one decision at a time, batching only tightly-related forks. Phrase every [choice] so it still reads as a plain question when AskUserQuestion is unavailable (other harnesses): the tool is an enhancement, never a hard dependency.

**Canonical pointer** — a skill's interview step quotes this instead of restating the mechanics:

> Conduct the interview per `references/interview.md` (honor each question's `[choice]` / `[open]` tag — see → Presentation; discrete = AskUserQuestion, open = prose).

## Hard gate (shared) — do not proceed until X

Both Intake and Decompose MUST clear this gate before producing or writing ANY task.
It is a real stop, not a checklist line you can skim. Decomposition that skips it is
a defect.

**DO NOT decompose, create, or write a single task until you have confirmed, out
loud with the user:**

- **Intent / done-criteria** [open] — what "done" actually looks like for this task.
- **Prior progress** [choice] — options: "Fresh start" / "Already begun". (Already-done work is not re-created.)
- **Shape** [choice] — options: "Single action" / "Multi-step". (A single action is NOT decomposed.)

Skip questions already answered by the user, the ticket, or TickTick — but still
CONFIRM these three, even when they seem obvious. If any is unresolved, ask; do not
infer and proceed. (Rationale: a mandated-but-skimmable step gets skipped — this is
the stop that prevents shredding work that was never understood.)

## Target day (shared)

Resolve which day you're planning before anything else:
- Explicit ("plan tomorrow", "plan today") wins — no question needed.
- [choice] Otherwise infer from time of day (evening → tomorrow, daytime → today) and confirm: options "Today" / "Tomorrow".

## Intake

Goal: understand the human shape of the work, then narrow hard to what to land on the target day.

**Frame the work**
- (Linear ID given) [choice] "Here's what <ID> says — still accurate, or has it drifted?" options: "Still accurate" / "Drifted (I'll explain)". Confirm scope before decomposing.
- (Described) [open] "Say a bit more about what 'done' looks like."
- [choice] "Fresh start, or already begun part of it?" options: "Fresh start" / "Already begun". (Same as the Hard gate prior-progress check.)

**Surface the real shape** (all [open] — unbounded)
- "Which parts are clear, which are still fuzzy?" (Fuzzy → a grooming/spike chunk first.)
- "Anything blocked, or needing a decision from someone else?"
- "A spike or investigation hiding in here before you can build?"
- "Riskiest / most uncertain part?" (More uncertainty → more slack, expect re-planning.)

**Narrow to the target day**
- [open] "What do you want to actually land that day?" Keep pulling until it's a small, concrete set.
- [choice, multiSelect] "Of those, which need deep focus vs are shallow?" (sets intensity; stage defaults seed it; activity is derived from stage)
- [choice, multiSelect] "Which will you do with AI?" (sets ai_discount; include a `review` stage when there are discounted build stages)
- [open] "What's the very first thing you'd touch?" (the first physical action)

**Confirm the shape** (once stages are proposed)
- [choice] present the proposed tree for sign-off. options: "Build as proposed" / "Adjust granularity" / "Fewer stages". Use previews to show the variants side by side when it helps.

**Estimate the target day's chunks** [open] (with the user, applying the AI discount)
- "Roughly how long if it goes normally?" Then sanity-check: mechanical/AI-amenable → trim; tracing/ambiguous/decision/review → don't trim.

Then read Calendar (Fixed duties), pack, review, confirm, write.

## Decompose

Goal: break down a task that ALREADY exists in TickTick (work or personal),
interview-first. Clear the **Hard gate** before any decomposition.

**Resolve the task**
- (Named) [choice] "Is this the one — '<title>' in <project>?" options: "Yes, that one" / "No, different task". Confirm the match before touching it.
- (Not named) [choice] "Here are tasks with no breakdown yet — which do you want to work through?" options: the undecomposed candidates (no `childIds`).

**Confirm context** (heuristics → Contexts)
- [choice] "That's in <project>, so <context> — treat it as <context>?" options: "Work" / "Personal".

**Already split?**
- [choice] "It already has these chunks: … refine, fill a gap, or leave it?" options: "Add missing chunks" / "Leave as is". Augment; never duplicate existing chunks.

**Then the Hard gate** (intent [open] / prior progress [choice] / single-vs-multi [choice]), then decompose per context:
- work → pipeline stages (use the Intake "surface the real shape" [open] + "narrow" [choice] questions for stages, intensity, AI, first action).
- personal → 2–4 free-form steps, or conclude it's a single action and just schedule/cue it (don't over-shred).

**Confirm, then write** [choice] — present the proposed chunks for sign-off ("Build as proposed" / "Adjust" / (personal) "Don't decompose, just remind") before writing: the existing task becomes the parent; create chunks as
children (`parentId`, kind TEXT, `ai` tag); re-read to confirm `childIds`. Offer the
next step (`butler:plan` for work, a light reminder for personal).

## Plan / reconcile

Goal: reconcile open work honestly without nagging, then commit the target day.

**Reconcile (capped, no-blame — see heuristics)**
- [choice] Default: re-surface each unfinished chunk with options "Keep" / "Park". Park = drop the date + `parked` tag, no "why" needed. One thread at a time — don't wall up every chunk.
- [open] Ask "what got in the way?" for at most the 1–2 most-slipped chunks. Route: blocked / underestimated / too vague / low-energy (heuristics → Reconciliation).
- [open] Only escalate to "want to look at why this one keeps slipping?" when a chunk has slipped repeatedly.
- [choice] "Anything you actually finished but didn't tick?" options "All ticked" / "Mark some done" (→ which).

**Commit the target day**
- [open] "What do you want to land?" Pull until it's a small, concrete set.
- [choice, multiSelect] Set must/should/want across the chosen chunks; respect the 3-musts flag.
- [choice, multiSelect] "Which need deep focus vs shallow?"

Then Fixed duties, pack, review, confirm, write the target day's blocks only.

## Reschedule

Goal: recompute the rest of *today* from where things actually are.

- [open] "Where are you right now — what's done, what's left?"
- [choice] "Anything new that has to happen today?" options "Nothing new" / "Add something" (→ then open: what).
- [choice] "Any blocks already passed we should drop or shrink?" options "Drop passed" / "Keep all" (→ which).

Then re-read remaining chunks + remaining commitments, pack with `now` = current
time, review (overflow cascades, musts never silently dropped), confirm, update.

## Fixed duties (shared)

Read the target day's timed Calendar events in the window first, then confirm and fill gaps:
- [choice] "I see <events> on your calendar — still on?" options "All still on" / "Adjust one" (→ open: which/when).
- [open] "Lunch or a break planned, roughly when?"
- [open] "Any commute or away-from-keyboard time?"
- [open] "Any family or personal time to protect?"

These become the packer's `fixed_commitments`. Default to remembered habits (e.g.
a usual lunch window) but confirm rather than assume.
