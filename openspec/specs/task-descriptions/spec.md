# task-descriptions

## Purpose

Define the body of a generated task: a lean launchpad — a concrete first action, an
optional single `Done when …` signal, the estimate as `~<n>m`, and a link to the
source of record — rather than a spec that duplicates the ticket. Detail and
acceptance criteria stay in the linked system of record (Linear).

## Requirements

### Requirement: Chunk descriptions are a lean launchpad, not a spec

Generated chunk descriptions SHALL contain only: a concrete first physical action
(prose, no field label), an optional single `Done when …` line, the estimate as
`~<minutes>m`, and — for work chunks — a Markdown link to the source ticket. They
SHALL NOT use `Why:` / `Where:` / `Ref:` labels or a `stage` / `ai` footer. Detail
and full acceptance criteria SHALL live in the linked system of record (Linear), not
be duplicated into the description.

#### Scenario: Work chunk description renders lean

- **WHEN** a work chunk's description is written
- **THEN** it contains the first action in prose, an optional `Done when …` line, `~<n>m`, and a `[TICKET ↗](url)` link
- **AND** it contains no `Why:`/`Where:`/`Ref:` labels and no `stage`/`ai` footer

#### Scenario: Acceptance criteria are not duplicated from Linear

- **WHEN** the source ticket already defines acceptance criteria
- **THEN** the description links to the ticket rather than copying its AC

### Requirement: The estimate is shown as `~Nm` and remains the calibration anchor

The estimate SHALL be rendered as `~<minutes>m` (e.g. `~60m`), replacing the `est0:`
label. It SHALL remain immutable — set once at intake and never overwritten on
reschedule — so it stays the anchor for estimate-vs-actual calibration. The `stage`
SHALL be conveyed by the title prefix rather than the description footer, and
`ai_discount` SHALL NOT be written into the description.

#### Scenario: Estimate legible and immutable

- **WHEN** a chunk carries an estimate
- **THEN** the description shows `~<n>m` (not `est0: <n>m`)
- **AND** reschedule does not overwrite that value

#### Scenario: Stage and ai_discount absent from the footer

- **WHEN** a work chunk description is written
- **THEN** the stage is reflected in the title prefix and not repeated in the description
- **AND** `ai_discount` does not appear in the description

### Requirement: Multi-criteria acceptance becomes subtasks, not a description checklist

When acceptance has more than one observable signal, the chunk SHALL be split into
real subtasks (each a child task) rather than carrying a `- [ ]` checklist inside the
description. A single observable signal SHALL stay a one-line `Done when …`.

#### Scenario: Several acceptance signals

- **WHEN** a chunk has multiple independent acceptance signals
- **THEN** they are modeled as child subtasks, not a checklist in the description

#### Scenario: Single acceptance signal

- **WHEN** a chunk has exactly one observable signal
- **THEN** it is a single `Done when …` line, with no subtasks and no checklist

### Requirement: Personal chunks and parent units follow the model

Personal-context chunk descriptions SHALL use the same lean shape minus the ticket
link (a first action, optional `Done when …`, optional `~<n>m`). Parent work-units
SHALL keep their metadata header (`Linear` / `Ticket` / `Branch`) as the unit's
record.

#### Scenario: Personal chunk has no source link

- **WHEN** a personal chunk description is written
- **THEN** it has a first action and optional `Done when …`/`~<n>m`, and no Linear link

#### Scenario: Parent retains its record header

- **WHEN** a parent work-unit is written
- **THEN** it keeps the `Linear` / `Ticket: <ID>` / `Branch` metadata block
