# Interview banks

Thorough but conversational. Ask, listen, adapt — never fire a wall of questions,
and skip anything already answered (by the user, the ticket, or TickTick). One
main thread at a time. The aim of every interview is a small, committed plan for
the **target day** (today when planning in the morning, tomorrow when planning in
the evening), not a multi-day schedule.

## Contents

- Target day (shared, ask first when ambiguous)
- Intake
- Plan / reconcile
- Reschedule
- Fixed duties (shared)

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
- "Of those, which are deep vs shallow/comms/review?" (mode tags)
- "Which will you do with AI?" (sets ai_discount; remember each discounted build gets a paired verify chunk)
- "What's the very first thing you'd touch?" (the first physical action)

**Estimate the target day's chunks** (with the user, applying the AI discount)
- "Roughly how long if it goes normally?" Then sanity-check: mechanical/AI-amenable → trim; tracing/ambiguous/decision/review → don't trim.

Then read Calendar (Fixed duties), pack, review, confirm, write.

## Plan / reconcile

Goal: reconcile open work honestly without nagging, then commit the target day.

**Reconcile (capped, no-blame — see heuristics)**
- Default: re-surface unfinished chunks with "keep or park?". Park = drop the date + `parked` tag, no "why" needed.
- Ask "what got in the way?" for at most the 1–2 most-slipped chunks. Route: blocked / underestimated / too vague / low-energy (heuristics → Reconciliation).
- Only escalate to "want to look at why this one keeps slipping?" when a chunk has slipped repeatedly.
- "Anything you actually finished but didn't tick?"

**Commit the target day**
- "What do you want to land?" Set must/should/want; respect the 3-musts flag.
- "Which are deep vs shallow/comms/review?"

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
