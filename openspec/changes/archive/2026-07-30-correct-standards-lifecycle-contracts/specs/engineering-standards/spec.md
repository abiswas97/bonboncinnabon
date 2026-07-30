## MODIFIED Requirements

### Requirement: Lifecycle-aware advisory guidance

Host adapters SHALL map native events into a shared lifecycle model for session
start, compacted continuation, planning, editing, and subagent start where the
host exposes a suitable event. Version 1 hooks MUST remain advisory and MUST NOT
deny a tool, approve a permission, or force a continuation loop.

#### Scenario: Start or resume a root session

- **WHEN** `SessionStart` has source `startup`, `resume`, or `clear`
- **THEN** the hook delivers the exact commandments, precedence rule, and
  supporting-rule index through an event-supported context field

#### Scenario: Continue after compaction

- **WHEN** `SessionStart` has source `compact`
- **THEN** the hook delivers the same guidance plus bounded secret-safe Git context

#### Scenario: Start a delegated subagent

- **WHEN** a supported host emits `SubagentStart`
- **THEN** the hook delivers the exact commandments and precedence rule without
  the supporting-rule index or Git context

#### Scenario: Plan has an evidence gap

- **WHEN** `UserPromptSubmit` reports `permission_mode: "plan"` or Claude invokes
  `ExitPlanMode`
- **THEN** the hook returns compact advisory guidance with applicable rule IDs
  and permits the plan to proceed

#### Scenario: Host exposes no equivalent lifecycle event

- **WHEN** one host lacks an event available in the other host
- **THEN** that guidance is omitted or delivered at the nearest safe lifecycle
  without fabricating blocking semantics

### Requirement: Low-context delivery

Standards MUST inject full commandments only at root `SessionStart` and
`SubagentStart`. Root session guidance MAY include the supporting index, while
subagent guidance MUST omit it. Later plan and edit feedback MUST use stable rule
IDs, deduplicate already-delivered rules when session state is available, and
respect defined output caps.

#### Scenario: Repeat an edit in the same scope

- **WHEN** the same applicable rule IDs were already delivered in the current session
- **THEN** a later edit event does not repeat them unless the event contains a new actionable condition

#### Scenario: Guidance exceeds an event budget

- **WHEN** applicable guidance would exceed six rule IDs or 2,500 characters outside session start
- **THEN** output is deterministically truncated with a pointer to the Standards skill for details

#### Scenario: Session guidance approaches its budget

- **WHEN** session-start content would exceed 7,000 characters
- **THEN** validation fails rather than silently dropping a commandment

### Requirement: Compact and safe Git context

Standards SHALL limit Git context to compacted-continuation guidance, which MAY
include repository root label, branch state, a capped changed-path summary, and a
short recent-commit summary. It MUST
NOT include raw diffs, source contents, commit bodies, remote URLs, environment
variables, resolved secrets, or an absolute developer path.

#### Scenario: Continue after compaction inside a Git repository

- **WHEN** `SessionStart` has source `compact` and Git commands finish within their timeout
- **THEN** guidance includes only the allowed capped repository context

#### Scenario: Start or resume without compaction

- **WHEN** `SessionStart` has source `startup`, `resume`, or `clear`
- **THEN** guidance omits Git context

#### Scenario: Git is absent or times out

- **WHEN** Git cannot provide context safely
- **THEN** the hook omits Git context, remains silent about internal failures unless diagnostic mode is enabled, and exits successfully
