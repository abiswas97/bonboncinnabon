# engineering-standards Specification

## Purpose

Define portable, low-context engineering guidance, repository overlays, and
advisory lifecycle delivery for the Standards plugin across supported hosts.

## Requirements

### Requirement: Canonical engineering commandments

Standards MUST contain one canonical human-readable definition of the ten approved engineering commandments and their precedence rule. Generated files, commands, skills, and hook code MUST reference that definition rather than maintaining divergent copies.

#### Scenario: Load standards at session start

- **WHEN** a supported host starts a session with Standards enabled
- **THEN** the host receives all ten commandments and the precedence rule from the canonical definition

#### Scenario: Resolve a conflict between tenets

- **WHEN** two commandments point toward different implementation choices
- **THEN** the guidance asks the agent to state the trade-off, use evidence, and minimize long-term change cost while preserving correctness, safety, and explicit requirements

### Requirement: Structured supporting rule registry

Supporting standards MUST use stable rule IDs and machine-readable metadata for title, compact summary, guidance class, lifecycle applicability, path applicability, role applicability, and detailed reference. The registry MUST reject duplicate IDs and invalid metadata.

#### Scenario: Select rules for a source edit

- **WHEN** an edit event contains one or more affected paths
- **THEN** the resolver returns only rules whose lifecycle, path, and role selectors apply

#### Scenario: Explain a compact rule citation

- **WHEN** lifecycle feedback cites a rule ID
- **THEN** the Standards skill can resolve that ID to its canonical title and detailed guidance

#### Scenario: Guide comments on a source edit

- **WHEN** a supported source file is edited
- **THEN** the applicable guidance asks the agent to preserve only current,
  non-obvious constraints, contracts, safety rationale, or required API behavior
  and to remove comments that merely narrate work history or obvious code

### Requirement: Repository standards overlays

Standards SHALL resolve an optional `.standards/standards.json` repository overlay. An overlay MAY extend the defaults, add supporting rules, narrow applicability, or replace supporting defaults, but MUST NOT remove or redefine the commandments.

#### Scenario: Extend the default registry

- **WHEN** an overlay declares `extends: "default"` and adds a valid repository rule
- **THEN** the effective registry contains the commandments, default supporting rules, and repository rule

#### Scenario: Replace supporting defaults

- **WHEN** a valid overlay omits `extends`
- **THEN** the effective registry contains the immutable commandments and overlay supporting rules but not default supporting rules

#### Scenario: Attempt to override a commandment

- **WHEN** an overlay reuses a reserved commandment ID or otherwise attempts to redefine a commandment
- **THEN** validation fails with the offending location and no partial overlay is applied

#### Scenario: Host-native instruction conflicts with a default

- **WHEN** an explicit repository instruction conflicts with portable supporting guidance
- **THEN** the explicit instruction takes precedence and the conflict is reported concisely

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
- **THEN** that guidance is omitted or delivered at the nearest safe lifecycle without fabricating blocking semantics

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

### Requirement: Safe per-session delivery state

Deduplication state MUST contain only host identifier, session identifier, delivered rule IDs, and timestamps. State writes MUST be atomic, prefer the host-provided plugin data directory, prune entries older than seven days, and degrade without failing the host when storage is unavailable.

#### Scenario: Plugin data directory is writable

- **WHEN** a hook delivers rule IDs for a stable host session
- **THEN** it atomically records only the minimal delivery metadata for that session

#### Scenario: Plugin data directory is unavailable

- **WHEN** a hook cannot read or write delivery state
- **THEN** it still returns correct bounded guidance and exits successfully

### Requirement: Compact and safe Git context

Standards SHALL limit Git context to compacted-continuation guidance, which MAY
include repository root label, branch state, a capped changed-path summary, and a
short recent-commit summary. It MUST NOT include raw diffs, source contents,
commit bodies, remote URLs, environment variables, resolved secrets, or an
absolute developer path.

#### Scenario: Continue after compaction inside a Git repository

- **WHEN** `SessionStart` has source `compact` and Git commands finish within their timeout
- **THEN** guidance includes only the allowed capped repository context

#### Scenario: Start or resume without compaction

- **WHEN** `SessionStart` has source `startup`, `resume`, or `clear`
- **THEN** guidance omits Git context

#### Scenario: Git is absent or times out

- **WHEN** Git cannot provide context safely
- **THEN** the hook omits Git context, remains silent about internal failures unless diagnostic mode is enabled, and exits successfully

### Requirement: Cross-host affected-path extraction

Claude and Codex adapters MUST extract every affected path exposed by supported write, edit, patch, delete, and move payloads, normalize it relative to the repository root, and pass it to the shared resolver.

#### Scenario: Codex patch changes multiple files

- **WHEN** an `apply_patch` payload adds, updates, deletes, or moves several files
- **THEN** every patch header path is considered for applicable standards

#### Scenario: Path escapes repository root

- **WHEN** a payload names a path outside the resolved repository root
- **THEN** repository-scoped rules are not applied to that path and the adapter does not read the target

### Requirement: Standards discovery skills

Standards MUST provide a skill that explains effective rules and a skill that proposes a minimal repository overlay. Overlay creation MUST require explicit confirmation before writing.

#### Scenario: Inspect effective standards

- **WHEN** a user invokes the Standards skill with a task or path
- **THEN** it reports applicable commandments and supporting rules with stable IDs and precedence

#### Scenario: Initialize repository standards

- **WHEN** a user invokes the initialization skill
- **THEN** it inspects the repository, proposes the smallest valid overlay, and makes no write until the user confirms

### Requirement: Language-neutral version 1

Version 1 standards MUST express portable engineering behavior applicable to Rust, Python, Go, TypeScript, and other languages without invoking language-specific formatters, compilers, linters, or regex security scans.

#### Scenario: Edit a supported-language repository

- **WHEN** the repository uses any programming language
- **THEN** the default plugin applies language-neutral architecture, clarity, safety, and evidence guidance without requiring that language's toolchain
