# plugin-portability-validation Specification

## Purpose

Define validation, test, CI, and release gates that keep portable plugin
artifacts correct, deterministic, safe, and installable on both supported hosts.

## Requirements

### Requirement: Canonical schema validation

Validation MUST reject malformed canonical marketplace, plugin, registry, and overlay records before producing host projections. Diagnostics MUST identify the file and field or rule ID responsible.

#### Scenario: Canonical plugin record omits a required field

- **WHEN** validation encounters a local plugin without a valid name, version, source, or host declaration
- **THEN** it exits nonzero with an actionable field-level diagnostic and writes no projections

#### Scenario: Overlay uses an unsupported schema version

- **WHEN** an overlay declares a schema version the installed Standards plugin cannot interpret
- **THEN** validation rejects the overlay without partially applying it

### Requirement: Generated artifact drift check

The repository MUST provide a check mode that computes every expected projection without modifying the worktree and fails for stale, missing, extra, or nondeterministic generated artifacts.

#### Scenario: Generated repository is current

- **WHEN** check mode runs after a clean generation
- **THEN** it exits successfully and leaves the worktree unchanged

#### Scenario: Generated manifest contains a manual edit

- **WHEN** a committed projection no longer matches canonical input
- **THEN** check mode exits nonzero and names the affected file

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

### Requirement: Output safety and budget validation

Automated tests MUST prove that hook output remains within its lifecycle budget, successful hooks are silent, commands use timeouts and output caps, and emitted context contains no raw diff, file content, remote URL, absolute developer path, environment value, or secret-like fixture.

#### Scenario: Secret fixture appears in repository state

- **WHEN** a fixture contains a token-like value in an environment variable, remote URL, diff, or file
- **THEN** no hook output or state file contains that value

#### Scenario: No rule is actionable

- **WHEN** a lifecycle fixture resolves no new applicable guidance
- **THEN** stdout is empty and the adapter exits successfully

### Requirement: Deterministic dual-host package validation

CI MUST validate the generated Claude and Codex marketplace entries, manifests,
skills, commands, and hook paths without invoking authenticated hosts or relying
on developer configuration, caches, credentials, or trust state.

#### Scenario: Validate repository-owned plugin packages

- **WHEN** deterministic package validation runs
- **THEN** every declared component exists, every generated path resolves inside
  its plugin package, and host-specific marketplace filtering is correct

### Requirement: macOS and Linux CI coverage

The validation workflow MUST run generation, unit, fixture, path-handling,
existing Butler, and package-shape checks on current macOS and Ubuntu runners
using Node 22.

#### Scenario: Platform-specific path behavior regresses

- **WHEN** a hook or generator works on one supported operating system but fails on the other
- **THEN** the corresponding CI matrix job fails before release

### Requirement: Release and version consistency

Each repository-owned plugin's canonical version MUST agree with both generated manifests, every version-bearing generated marketplace entry, changelog release metadata, and the intended independent release tag. A Codex marketplace entry, whose native schema has no version field, MUST resolve to the matching version-bearing Codex plugin manifest.

#### Scenario: Version drifts in one projection

- **WHEN** Butler or Standards has inconsistent version metadata
- **THEN** release validation fails and lists every mismatched location

#### Scenario: Release one local plugin

- **WHEN** a maintainer releases Butler or Standards
- **THEN** the other plugin's version and release identity remain unchanged unless its canonical content also changed

### Requirement: Existing behavior regression gates

Portability validation MUST include the existing Butler test suite and MUST verify that unrelated tracked or untracked workspace files are not consumed as canonical inputs or modified by generation.

#### Scenario: Run the full repository validation

- **WHEN** portable packaging is validated
- **THEN** existing Butler behavior tests pass alongside the new portability tests

#### Scenario: Unrelated files exist in the worktree

- **WHEN** generation runs with unrelated user files present
- **THEN** it reads only declared canonical inputs and modifies only declared generated targets
