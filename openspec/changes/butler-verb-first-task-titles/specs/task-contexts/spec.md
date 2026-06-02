## MODIFIED Requirements

### Requirement: Anti-slop task contract applies to all contexts

Every generated task in any context SHALL follow the anti-slop task contract
(`references/task-contract.md`): sentence case, no emoji, no trailing period, ≤70 chars,
no slop vocabulary. Chunk titles (actions) in every context SHALL be verb-first — a
concrete physical-action verb plus the object — and SHALL NOT use a `stage:` prefix.
Parent work-units (outcomes) SHALL be outcome-named, not verb-first. For work chunks, the
pipeline stage SHALL be carried as a stage tag rather than a title prefix, and the stage
tag SHALL be the reference class used for estimate-vs-actual calibration.

#### Scenario: Work chunk title is verb-first with no stage prefix

- **WHEN** a work chunk title is generated (e.g. "Verify Neighborhood Location end to end on both pricers")
- **THEN** it leads with a physical-action verb and names the object, is sentence case, has no emoji or trailing period, is ≤70 chars
- **AND** it has no `stage:` prefix; the stage is carried as a tag (e.g. `qa`)

#### Scenario: Personal title obeys the contract without a stage prefix

- **WHEN** a personal chunk title is generated (e.g. "Book the dentist appointment")
- **THEN** it is verb-first, sentence case, has no emoji or trailing period, is ≤70 chars, and has no `stage:` prefix

#### Scenario: Calibration groups by the stage tag

- **WHEN** completed work chunks are grouped for calibration
- **THEN** the reference class is read from the stage tag, not parsed from the title prefix
- **AND** legacy chunks that still encode stage in the title remain readable as a fallback
