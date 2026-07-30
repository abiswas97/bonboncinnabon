## ADDED Requirements

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
Generated Claude and Codex marketplace catalogs, plugin manifests, skills, command frontmatter, hook maps, and executable references MUST pass repository contract checks and the pinned host validators where available.

#### Scenario: Claude command contains invalid frontmatter
- **WHEN** strict validation encounters malformed YAML or a missing required command field
- **THEN** CI fails with the command path and validation error

#### Scenario: Host manifest references a missing component
- **WHEN** a generated manifest points to an absent skill, command, hook file, or executable
- **THEN** validation fails before an installation smoke test

### Requirement: Native payload contract fixtures
Tests MUST cover representative Claude and Codex payload fixtures for each supported lifecycle and tool event, including malformed, incomplete, multi-path, moved-path, non-repository, and oversized input.

#### Scenario: Parse a recorded host payload
- **WHEN** an adapter receives a supported fixture
- **THEN** it produces the expected neutral event and bounded native response

#### Scenario: Parse malformed input
- **WHEN** an adapter receives invalid JSON or missing optional fields
- **THEN** it exits successfully with no unsafe action or blocking host decision

### Requirement: Output safety and budget validation
Automated tests MUST prove that hook output remains within its lifecycle budget, successful hooks are silent, commands use timeouts and output caps, and emitted context contains no raw diff, file content, remote URL, absolute developer path, environment value, or secret-like fixture.

#### Scenario: Secret fixture appears in repository state
- **WHEN** a fixture contains a token-like value in an environment variable, remote URL, diff, or file
- **THEN** no hook output or state file contains that value

#### Scenario: No rule is actionable
- **WHEN** a lifecycle fixture resolves no new applicable guidance
- **THEN** stdout is empty and the adapter exits successfully

### Requirement: Isolated dual-host installation smoke tests
CI MUST exercise marketplace addition and local plugin installation in isolated temporary homes for both supported hosts without relying on the developer's global configuration, caches, trust records, or credentials.

#### Scenario: Install repository-owned plugins in Claude
- **WHEN** the Claude smoke test adds the generated marketplace and installs Butler and Standards
- **THEN** the isolated host enumerates their expected commands, skills, and hooks

#### Scenario: Install repository-owned plugins in Codex
- **WHEN** the Codex smoke test adds the generated marketplace and installs Butler and Standards
- **THEN** the isolated host enumerates their expected skills, manifests, and hook configuration

#### Scenario: Verify external plugin filtering
- **WHEN** isolated hosts enumerate their generated marketplaces
- **THEN** Claude includes the preserved external entries and Codex contains only natively supported entries

### Requirement: macOS and Linux CI coverage
The validation workflow MUST run generation, unit, fixture, path-handling, existing Butler, and isolated installation checks on current macOS and Ubuntu runners using Node 22.

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
