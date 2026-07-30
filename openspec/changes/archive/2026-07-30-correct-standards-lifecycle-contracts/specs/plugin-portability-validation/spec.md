## MODIFIED Requirements

### Requirement: Strict host contract validation

Generated Claude and Codex artifacts MUST pass repository contract checks and
the pinned host validators where available, including marketplace catalogs,
plugin manifests, skills, command frontmatter, purpose-specific hook maps, and
executable references.
The Codex manifest MUST explicitly declare its hook map path, and validation MUST
assert that each host receives only its intended registrations.

#### Scenario: Host hook capabilities differ

- **WHEN** generated artifacts are validated
- **THEN** Claude alone contains the `ExitPlanMode` `PreToolUse` registration and
  both hosts contain only their supported shared registrations

#### Scenario: Codex manifest references hook configuration

- **WHEN** the Codex plugin manifest is generated
- **THEN** its explicit hook path resolves to the generated Codex hook map

#### Scenario: Generated command invokes plugin code

- **WHEN** generated command frontmatter is validated
- **THEN** it uses that host's plugin-root environment variable and required timeout shape

#### Scenario: Claude command contains invalid frontmatter

- **WHEN** strict validation encounters malformed YAML or a missing required command field
- **THEN** CI fails with the command path and validation error

#### Scenario: Host manifest references a missing component

- **WHEN** a generated manifest points to an absent skill, command, hook file, or executable
- **THEN** validation fails before release

### Requirement: Native payload contract fixtures

Tests MUST cover representative Claude and Codex payload fixtures for every
registered lifecycle and tool event, including startup and compact session
sources, normal and plan prompts, Claude `ExitPlanMode`, multi-path patches,
subagent start, malformed input, traversal paths, deduplication, and oversized
input. Tests MUST also reject the former `PreCompact` and `Stop`
`additionalContext` responses.

#### Scenario: Parse a registered host payload

- **WHEN** an adapter receives a supported fixture
- **THEN** it produces the expected neutral event and exactly the native output
  fields allowed for that registered event

#### Scenario: Parse an unregistered or malformed payload

- **WHEN** an adapter receives `PreCompact`, `Stop`, invalid JSON, or missing optional fields
- **THEN** it exits successfully without `additionalContext`, unsafe action, or blocking decision

## MODIFIED Requirements

### Requirement: Deterministic dual-host package validation

CI MUST validate generated Claude and Codex marketplace entries, manifests,
skills, commands, and hooks without relying on developer configuration, caches,
credentials, or trust state.

#### Scenario: Validate repository-owned plugin packages

- **WHEN** deterministic package validation runs
- **THEN** declared components exist and host-specific filtering is correct
