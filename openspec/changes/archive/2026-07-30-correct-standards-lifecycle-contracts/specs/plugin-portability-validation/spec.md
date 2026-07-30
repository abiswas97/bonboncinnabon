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
- **THEN** validation fails before an installation smoke test

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

## ADDED Requirements

### Requirement: Authenticated lifecycle release smoke

The repository MUST provide an explicit opt-in macOS release command that
installs Standards into temporary Claude and Codex homes and uses authenticated
host calls to exercise startup, prompt, edit, subagent, compaction, and normal
shutdown. The Codex app-server phase MUST list hooks, trust only their exact
current hashes, verify lifecycle delivery, and record the `permission_mode`
observed by a real Plan-mode probe. This command MUST NOT run in ordinary CI.

#### Scenario: Maintainer runs authenticated release smoke

- **WHEN** a maintainer explicitly opts in with valid Claude and Codex credentials
- **THEN** both temporary installations exercise the required lifecycle and report
  evidence without printing or copying resolved secrets

#### Scenario: Ordinary CI runs

- **WHEN** the macOS or Ubuntu deterministic workflow executes
- **THEN** it does not make credentialed model calls or require hook trust state

## MODIFIED Requirements

### Requirement: Isolated dual-host installation smoke tests

CI MUST exercise marketplace addition and local plugin installation in isolated
temporary homes for both supported hosts without relying on the developer's
global configuration, caches, trust records, or credentials. These tests prove
installation shape only and MUST NOT be described as runtime hook delivery proof.

#### Scenario: Install repository-owned plugins in Claude

- **WHEN** the Claude smoke test adds the generated marketplace and installs Butler and Standards
- **THEN** the isolated host enumerates their expected commands, skills, and hooks

#### Scenario: Install repository-owned plugins in Codex

- **WHEN** the Codex smoke test adds the generated marketplace and installs Butler and Standards
- **THEN** the isolated host enumerates their expected skills, manifests, and hook configuration

#### Scenario: Verify external plugin filtering

- **WHEN** isolated hosts enumerate their generated marketplaces
- **THEN** Claude includes the preserved external entries and Codex contains only natively supported entries
