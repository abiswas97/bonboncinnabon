# context-aware-scheduling Specification

## Purpose

Defines how `butler:plan` and `butler:reschedule` route scheduling by context.
Work chunks go through the packer exactly as in 0.2.0; personal chunks bypass the
packer and receive light scheduling (a due time plus reminder) chosen
conversationally from a live read of the target day.

## Requirements

### Requirement: plan routes scheduling by context

`butler:plan` SHALL reconcile and commit a target day across contexts, routing each
task by its context. Work chunks SHALL go through the packer exactly as in 0.2.0.
Personal chunks SHALL bypass the packer entirely. A single "plan the day" flow
SHALL handle both, presenting the two contexts visually separated in the proposal.

#### Scenario: Work and personal handled in one plan run

- **WHEN** the user plans a day that has both work and personal tasks
- **THEN** work chunks are packed via `pack_schedule.py` and personal chunks are scheduled lightly
- **AND** the proposal shows the work blocks and the personal items in clearly separated sections

#### Scenario: Work packing unchanged

- **WHEN** only work chunks are planned
- **THEN** the packer input, ordering, focus cap, and buffers are identical to 0.2.0 behavior

### Requirement: Personal tasks get light scheduling only

Personal-context tasks SHALL be scheduled as a due time + reminder, never as a
packed focus block. They SHALL NOT consume the focus cap, SHALL NOT use
`deep_first`, intensity, or activity ordering, and SHALL NOT contend for the work
focus window.

#### Scenario: Personal item scheduled as time plus reminder

- **WHEN** a personal task is committed for the target day
- **THEN** it receives a due time and a reminder
- **AND** it does not appear in the packer input and does not reduce work focus capacity

### Requirement: Personal "when" is chosen conversationally, defaulted from a live read of the day

The personal due time SHALL be chosen conversationally with the user. When the user
defers, the system SHALL derive a sensible time from a live read of the target day —
querying TickTick for the day's existing timed items and reading the day's Google
Calendar events — rather than a fixed configured default. It SHALL place the
reminder in an open slot that does not stack on an existing anchor or collide with a
commitment. The system SHALL NOT invent a separate personal focus window.

#### Scenario: Ask for a time, derive from a live read on defer

- **WHEN** a personal task needs a time and the user has not specified one
- **THEN** the skill asks for a preferred time
- **AND** if the user defers, it reads the target day's existing TickTick timed items and Calendar events and picks an open, sensible time that avoids stacking or collisions
- **AND** it does not create a personal focus-window construct
- **AND** it does not read a hardcoded default time from config

#### Scenario: Avoid stacking on an existing anchor

- **WHEN** the target day already has timed items clustered around a time (e.g. several reminders late morning)
- **THEN** a deferred personal reminder is placed in a clearer part of the day rather than added to the cluster

### Requirement: reschedule recomputes work, keeps personal reminders

`butler:reschedule` SHALL recompute today's remaining WORK blocks from the current
time via the packer (as in 0.2.0). Personal items SHALL NOT be repacked; their
reminders SHALL be kept or adjusted, not recomputed into focus blocks.

#### Scenario: Reschedule moves work blocks only

- **WHEN** the user reschedules a slipped day
- **THEN** remaining work blocks are repacked from `now`
- **AND** personal items keep their reminders (optionally adjusted) and are not packed

### Requirement: plan sources fixed commitments from a calendar

`plan` and `reschedule` SHALL source the target day's meetings as fixed commitments
from a calendar when one is available, and SHALL persist the calendar source in
`config.yaml` (not re-ask each run). When a Google Calendar MCP is connected, they
read the target day's events from the calendars named in config (default: the primary
calendar). The source is config, never a side store.

#### Scenario: Calendar MCP connected

- **WHEN** a Google Calendar MCP is connected and `config.yaml` names the calendars to read
- **THEN** plan/reschedule read the target day's events from those calendars and pass them to the packer as fixed commitments

#### Scenario: No calendar available — non-blocking fallback

- **WHEN** no calendar MCP is connected
- **THEN** plan still runs (calendar-blind) but explicitly states it is unaware of meetings, and suggests connecting a calendar MCP
- **AND** if the user's events are scattered across multiple calendars/accounts, it suggests consolidating to one account (or a multi-calendar tool)

#### Scenario: Source persisted in config

- **WHEN** the calendar source has been set
- **THEN** it is stored in `config.yaml` and reused on later runs without re-asking

### Requirement: plan reserves breaks as constraints, never as tasks

`plan` SHALL reserve a default lunch and one or more decompress breaks as packer
fixed-commitments placed around the day's meetings, and SHALL NOT materialize them as
TickTick tasks. Break durations come from `config.yaml` (`contexts.work.breaks`:
`lunch_min`, `decompress_min`); the number/length of decompress breaks scales to the
focus load; a break that would interrupt an in-progress focus block is deferred.
Breaks are adjustable or skippable per plan.

#### Scenario: Breaks reserved as gaps, not tasks

- **WHEN** plan builds the day
- **THEN** lunch and decompress are subtracted as fixed commitments (free gaps) and work packs around them
- **AND** no "Lunch" or "Decompress" task is created in TickTick

#### Scenario: Breaks flex around meetings and load

- **WHEN** the day has meetings and several focus blocks
- **THEN** lunch is placed around the meetings (not over them) and decompress break(s) are inserted between focus stretches, scaled to the load

#### Scenario: Defer a break that would break flow

- **WHEN** a scheduled break would interrupt an in-progress focus block
- **THEN** the break is deferred rather than forced
