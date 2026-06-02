# burnout-detection

## Purpose

Give butler a standing instinct to catch sustained overcommitment before it
becomes burnout, using behavioral data it already has (TickTick completion
history), and to raise it in an autonomy-preserving, non-punitive way. Grounded
in the Maslach overload-without-recovery model, JD-R, Siegrist ERI, and SDT
(`docs/research/butler-accommodations-evidence.md`).

## ADDED Requirements

### Requirement: plan computes a rolling-window overload signal

plan SHALL compute an overload signal from a rolling 5–7 day window of TickTick-derived history (planned load + completed tasks), using the user's OWN baseline (e.g. their ~30-day median/quartile), and SHALL NOT use absolute hour thresholds. The signal's components are a packed-day streak and a mandatory no-recovery-day flag (no day below ~50% of median load). Completion rate is NOT a gate: it is read only to TUNE the prompt's wording (finishing-everything vs falling-behind), never to suppress detection — the packed-but-behind user is the higher-risk profile and must not be excluded.

#### Scenario: Window has a packed streak with no light day

- WHEN the last 5–7 days show ≥4–5 packed days (above the user's own top-quartile load) and no day below ~50% of median
- THEN the overload signal is active, regardless of completion rate

#### Scenario: Window includes a recovery day

- WHEN any day in the window is below ~50% of the user's median load
- THEN the no-recovery flag is false and the overload signal does NOT fire (recovery-absence is mandatory)

#### Scenario: Baseline is personal

- WHEN computing "packed"
- THEN it is measured against the user's own rolling baseline, never a fixed hour count

### Requirement: Anti-nag via stateless rising-edge firing

plan SHALL surface the burnout prompt only on the RISING EDGE of the signal — when the current consecutive packed-day streak first reaches `min_packed_streak` (with at most one day of grace for a skipped planning day) AND there is no recovery day in the window. It SHALL stay silent for longer streaks. This needs no persisted state. Because firing is tied to the crossing day, if the user does not run plan on that day the prompt is SKIPPED, not deferred — failing safe to silence, consistent with never-nag. A single busy day SHALL NOT trigger it. The soft work-window memory is honored (a late evening alone is not overload).

#### Scenario: Streak just crossed the threshold

- WHEN the current consecutive packed-day streak first reaches `min_packed_streak` (or one day past, if no plan ran on the crossing day) and the other conditions hold
- THEN the prompt fires once

#### Scenario: Streak is well beyond the threshold

- WHEN the streak is longer than the fire band (the rising edge has already passed)
- THEN no prompt fires — it is assumed already surfaced or accepted, with no stored state

#### Scenario: One crunch day

- WHEN only a single day is packed
- THEN no prompt fires

#### Scenario: Crossing day was not planned

- WHEN the streak grew past the fire band on a day the user did not run plan
- THEN the prompt is skipped, not replayed later (fail-safe to silence)

### Requirement: The prompt is autonomy-preserving and never adds work

When the signal fires, plan SHALL ask (not tell) whether the user wants to keep the next day lighter, and SHALL act only on a yes (offer to lighten, defer, or protect a recovery block, or offer low-energy mode). It SHALL NOT add a task, auto-insert a rest/break block, or reschedule unasked. The framing is observational and non-punitive (no "you're burning out / doing too much").

#### Scenario: Signal fires during planning

- WHEN the overload signal is active as plan reconciles the day
- THEN plan surfaces one no-blame observation and asks if the user wants a lighter next day
- AND if the user declines, nothing is changed and no task is added
