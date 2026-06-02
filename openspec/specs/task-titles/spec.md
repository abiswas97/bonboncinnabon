# task-titles Specification

## Purpose

Defines the contract for a generated task's TITLE: verb-first concrete-object next
actions for chunks, outcome nouns for parent work-units, and stage carried as a tag
rather than a title prefix. The title is the action trigger that lowers activation
energy to start; detail and conditions live in the body or in subtasks, never in the
title.

## Requirements

### Requirement: Work chunk titles are verb-first next actions

A work chunk's title SHALL open with a concrete, physical verb that names the action,
followed by the object the verb acts on. The verb MAY be any imperative verb but SHALL
name a physical, visible action; non-actionable verbs ("think about", "look into", "deal
with") SHALL NOT be used as the title's action. The title SHALL NOT carry a `Stage:`
prefix.

#### Scenario: Work chunk title leads with a concrete verb and names the object

- **WHEN** a work chunk title is generated
- **THEN** it starts with a physical-action verb and names the object (e.g. `Verify Neighborhood Location end to end on both pricers`)
- **AND** it does not begin with a `Stage:` prefix (no `QA:` / `Backend:` lead)

#### Scenario: Non-actionable verbs are rejected

- **WHEN** the candidate title would open with "think about", "look into", or "deal with"
- **THEN** the title is rewritten to a physical-action verb that names the concrete next step

### Requirement: Parent work-units are outcome-named, not verb-first

A parent work-unit's title SHALL be an outcome/noun phrase describing the unit of work,
NOT a verb-first next action. The verb-first rule applies to chunks (actions), not to
parents (outcomes).

#### Scenario: Parent keeps an outcome noun title

- **WHEN** a parent work-unit title is generated
- **THEN** it is an outcome noun phrase (e.g. `Rules-to-checklist mapping (spike)`), not a verb-first imperative

#### Scenario: Chunks under an outcome parent are verb-first

- **WHEN** chunks are created under an outcome-named parent
- **THEN** each chunk title is a verb-first next action

### Requirement: Stage is carried as a tag, not in the title

A work chunk's pipeline stage SHALL be represented as a stage tag (`research`, `db`,
`backend`, `frontend`, `review`, `address-comments`, `qa`, `deploy`) on the task, in a
managed tag family parallel to `intensity`. Stage SHALL NOT be encoded in the title text.

#### Scenario: Work chunk carries a stage tag

- **WHEN** a work chunk is written
- **THEN** it carries exactly one stage tag (e.g. `qa`) alongside its intensity and `ai` tags
- **AND** the stage does not appear as a title prefix

### Requirement: The title keeps the object and the load-bearing cue; detail moves to the body

The title SHALL retain the object and the single disambiguating when/where cue needed to
act. It SHALL NOT be hollowed to a bare verb or bare stage. The test-matrix, conditions,
acceptance criteria, rationale, and links SHALL live in the body or in subtasks, not in
the title.

#### Scenario: Test-matrix moves out of the title

- **WHEN** a task has multiple conditions or a test-matrix (e.g. both portals, set + empty)
- **THEN** the title names the object and action and the conditions live in the body or subtasks (e.g. `Verify Neighborhood Location end to end on both pricers`, with set/empty cases as subtasks)

#### Scenario: Title is not hollowed

- **WHEN** a title is generated
- **THEN** it still names the object (not a bare `Verify` or `QA`), keeping the action concrete
