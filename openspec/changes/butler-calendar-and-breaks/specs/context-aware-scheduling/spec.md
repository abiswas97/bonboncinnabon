## ADDED Requirements

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
