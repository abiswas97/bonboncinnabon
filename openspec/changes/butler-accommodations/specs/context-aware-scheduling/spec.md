# context-aware-scheduling

## ADDED Requirements

### Requirement: plan applies the accommodations layer

plan SHALL apply `references/accommodations.md` at the points where it speaks to the user — reconciliation (non-punitive miss-handling), selection (mastery+pleasure blend, partial-completion framing), and the committed first action (action-first if-then cue) — without restating the principles.

#### Scenario: Reconciling slipped work under accommodations

- WHEN plan re-surfaces a slipped chunk
- THEN it follows the non-punitive principle: neutral event + keep-or-park + a small next step, no blame language

#### Scenario: Committing a block under accommodations

- WHEN plan commits a block
- THEN the surfaced next step is the action-first if-then cue ("when [trigger], start by [action]")

### Requirement: plan runs the burnout check at reconciliation

plan SHALL run burnout-detection during reconciliation, before committing the day, and surface its prompt when the signal fires. The check never blocks planning and never adds work on its own.

#### Scenario: Planning while overloaded

- WHEN plan reconciles the day and the overload signal is active (and not already prompted this window)
- THEN plan surfaces the no-blame burnout prompt and proceeds based on the user's answer

#### Scenario: Planning while not overloaded

- WHEN the overload signal is inactive
- THEN plan proceeds normally with no burnout prompt

### Requirement: plan offers and accepts low-energy mode

plan SHALL accept a user low-energy signal at any point and switch to reduced mode (~one mastery + one pleasure, smallest first step), and SHALL offer reduced mode as one option (never auto-apply) when burnout detection fires.

#### Scenario: User declares low energy mid-plan

- WHEN the user says they are low-energy while planning
- THEN plan switches to the reduced day rather than the full list

#### Scenario: Burnout fires and user wants to lighten

- WHEN the burnout prompt fires and the user opts to lighten
- THEN reduced mode is one of the offered options, applied only on the user's choice
