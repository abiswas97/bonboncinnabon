# task-contexts Specification

## Purpose

Defines how butler tasks are classified into contexts (`work`, `personal`),
where that classification is declared, and how the context shapes a task's data
model, decomposition style, and scheduling. Contexts are the single source of
truth that lets one set of skills behave differently for work versus personal
work without hardcoding policy.

## Requirements

### Requirement: Contexts are declared in config

The system SHALL define task `contexts` in `config.yaml` as the single source of
truth. Each context SHALL declare its member TickTick `projects`, its
`decomposition` style, its `axes`, and its `scheduling` style. At minimum the
`work` and `personal` contexts SHALL exist. No context behavior SHALL be hardcoded
in a skill; a skill SHALL read context membership and policy from config.

#### Scenario: Two contexts present in config

- **WHEN** a skill loads `config.yaml`
- **THEN** it finds a `contexts` map containing `work` and `personal`
- **AND** `work` lists its projects (e.g. `Plate`), `decomposition: pipeline`, `axes: [stage, intensity, ai_discount]`, `scheduling: packed`
- **AND** `personal` lists its projects (e.g. `Life, Photo, Finance, Relationships, Medical, Projects`), `decomposition: free-form`, `axes: [priority]`, `scheduling: light`

#### Scenario: Packer defaults preserved under the work context

- **WHEN** the `work` context configuration is read
- **THEN** `pipeline`, `work_window`, `capacity`, and `default_project` are present under `contexts.work` with their 0.2.0 values
- **AND** the generated packer input is identical to 0.2.0, so work scheduling behavior is unchanged

### Requirement: Context is derived from project, then confirmed

The system SHALL derive a task's context from its TickTick project membership and
SHALL confirm that context with the user before acting on it. Context detection
SHALL never be silent.

#### Scenario: Derived context confirmed

- **WHEN** a task belongs to a project mapped to `personal` (e.g. `Life`)
- **THEN** the skill states the derived context and asks the user to confirm (e.g. "This is in Life, so personal — treat it as personal?")
- **AND** it proceeds only after the user confirms or corrects

#### Scenario: Project not mapped to any context

- **WHEN** a task's project is not listed under any context in config
- **THEN** the skill SHALL ask the user which context applies rather than guessing

### Requirement: Personal tasks use a lightweight model

Personal-context tasks SHALL NOT carry `stage`, `intensity`, or `ai_discount`.
A personal chunk SHALL carry only `title`, `context`, optional `priority`
(must/should/want), optional `est0_min`, an optional `reminder` when scheduled,
and the `ai` tag.

#### Scenario: Personal chunk omits work axes

- **WHEN** a personal task is decomposed or written
- **THEN** its chunks have no `stage`, `intensity`, or `ai_discount`
- **AND** each chunk may carry `priority` and `est0_min` and a reminder, and carries the `ai` tag

### Requirement: Chunk schema encodes context with conditional axes

`chunk-task.schema.json` SHALL include a `context` enum of `[work, personal]` and
SHALL conditionally require the work axes. When `context` is `work`, `stage`,
`intensity`, `ai_discount`, and `est0_min` SHALL be required. When `context` is
`personal`, those axes SHALL be omitted; `priority`, `est0_min`, and `reminder`
are optional. The packer input schema SHALL remain unchanged.

#### Scenario: Work chunk validates with full axes

- **WHEN** a chunk has `context: work` and includes `stage`, `intensity`, `ai_discount`, `est0_min`, `kind: TEXT`, `ai_generated: true`
- **THEN** it validates against the schema

#### Scenario: Work chunk missing an axis fails

- **WHEN** a chunk has `context: work` but is missing `stage`
- **THEN** schema validation fails

#### Scenario: Personal chunk validates without work axes

- **WHEN** a chunk has `context: personal`, `title`, `kind: TEXT`, `ai_generated: true`, and no `stage`/`intensity`/`ai_discount`
- **THEN** it validates against the schema

### Requirement: Missing context defaults to work

A chunk with no `context` field SHALL be treated as `work`. This preserves all
existing 0.2.0 work trees, which were created before the field existed.

#### Scenario: Legacy chunk read as work

- **WHEN** a skill reads an existing chunk that has no `context` field (e.g. the ING-165 tree)
- **THEN** it treats the chunk as `work` and applies the full work model

### Requirement: Anti-slop task contract applies to all contexts

Every generated task in any context SHALL follow the anti-slop task contract
(`references/task-contract.md`): lean imperative verb + object, sentence case, no
emoji, no trailing period, ≤70 chars. Personal titles SHALL follow the contract
but SHALL NOT use the `stage:` prefix.

#### Scenario: Personal title obeys the contract without a stage prefix

- **WHEN** a personal chunk title is generated (e.g. "Book the dentist appointment")
- **THEN** it is sentence case, has no emoji or trailing period, is ≤70 chars, and has no `stage:` prefix
