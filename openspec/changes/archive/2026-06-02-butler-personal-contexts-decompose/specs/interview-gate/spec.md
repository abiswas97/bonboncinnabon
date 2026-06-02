## ADDED Requirements

### Requirement: Decomposition is gated behind a blocking interview

`intake` and `decompose` SHALL complete a blocking interview before producing or
writing any task tree. The interview SHALL establish intent / done-criteria, prior
progress (fresh vs already begun), blockers, and whether the work is multi-step or
a single action. The skill SHALL NOT decompose, create, or write any task until the
interview is complete. This is a hard gate, not an advisory checklist line.

#### Scenario: Intake stops to interview before building a tree

- **WHEN** the user invokes `intake` on a ticket or described work
- **THEN** the skill conducts the interview first
- **AND** it produces no chunks and writes nothing to TickTick until intent, prior progress, and shape are established

#### Scenario: Decompose stops to interview before splitting

- **WHEN** the user invokes `decompose` on an existing task
- **THEN** the skill conducts the interview before generating any chunk
- **AND** no task is created or modified until the interview is complete

### Requirement: Skills carry an explicit do-not-proceed red-flags block

`intake` and `decompose` SHALL each contain an explicit "do not proceed until X"
red-flags block naming the interview as a required stop. A skipped or skimmed
interview SHALL be treated as a defect.

#### Scenario: Red-flags block present and enforced

- **WHEN** the skill is read
- **THEN** it contains a red-flags / "do not proceed until X" block that lists completing the interview as a precondition for decomposition

### Requirement: The interview skips answered questions but always confirms the gate

The interview SHALL skip questions already answered by the user, the ticket, or
TickTick, but SHALL still confirm the three gate elements (intent, prior progress,
single-vs-multi-step) before proceeding, even when they seem obvious.

#### Scenario: Pre-answered details are not re-asked

- **WHEN** the ticket or the user already states done-criteria
- **THEN** the skill does not re-ask that question
- **AND** it still confirms prior progress and whether the work is one action or several before decomposing
