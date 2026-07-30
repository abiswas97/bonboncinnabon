## ADDED Requirements

### Requirement: Canonical portable marketplace metadata
The repository MUST define one host-neutral canonical marketplace record and one canonical record for each repository-owned plugin. Shared identity, version, description, source, component declarations, and host eligibility MUST NOT be independently authored in generated Claude and Codex manifests.

#### Scenario: Shared metadata changes
- **WHEN** a maintainer changes a local plugin version or description in its canonical record
- **THEN** regeneration updates every eligible host projection from that value

#### Scenario: Generated metadata is edited directly
- **WHEN** a committed host projection differs from the canonical records
- **THEN** check mode fails and identifies the stale projection

### Requirement: Deterministic host projections
The generator SHALL produce deterministic Claude and Codex marketplace catalogs, local plugin manifests, hook maps, and Codex skill metadata using Node 22 without plugin runtime dependencies.

#### Scenario: Repeated generation
- **WHEN** generation runs twice against unchanged canonical inputs
- **THEN** the second run produces no file changes

#### Scenario: Unsupported operating system
- **WHEN** generation runs on a platform other than macOS or Linux
- **THEN** it exits with an actionable unsupported-platform error

### Requirement: Honest host eligibility
Each generated marketplace SHALL contain only entries that have an installable package for that host. External Claude entries MUST remain unchanged in the Claude projection and MUST be absent from the Codex projection until their source repositories provide native Codex packages.

#### Scenario: Generate the Claude catalog
- **WHEN** the canonical catalog includes the existing external `devlab` and `postgres` Claude entries
- **THEN** the generated Claude marketplace preserves their source definitions

#### Scenario: Generate the Codex catalog
- **WHEN** an external entry declares Claude support but no Codex package
- **THEN** the Codex marketplace omits it and generation reports a deterministic informational diagnostic

### Requirement: Dual-host Butler packaging
`butler@bonboncinnabon` MUST be discoverable and installable through both generated marketplaces while retaining its existing Claude namespace, skills, command behavior, and product specifications.

#### Scenario: Install Butler in Claude
- **WHEN** a user adds the generated Claude marketplace and installs Butler
- **THEN** Claude discovers Butler's existing commands and skills under the expected namespace

#### Scenario: Install Butler in Codex
- **WHEN** a user adds the generated Codex marketplace and installs Butler
- **THEN** Codex discovers the corresponding Butler skills from its native plugin manifest

#### Scenario: Run existing Butler tests
- **WHEN** Butler receives its portable packaging
- **THEN** its existing behavioral test suite passes without changing planning semantics

### Requirement: Separate cohesive Standards plugin
`standards@bonboncinnabon` SHALL be a repository-owned plugin separate from Butler and SHALL contain the canonical standards content, standards skills, shared hook implementation, and host adapters.

#### Scenario: Install only Standards
- **WHEN** a user installs Standards without Butler
- **THEN** all standards content, skills, and hooks function without a Butler dependency

#### Scenario: Install both local plugins
- **WHEN** a user installs Butler and Standards from the same marketplace
- **THEN** the plugins retain independent namespaces, versions, data directories, and release identities

### Requirement: Direct marketplace consumption
Committed generated catalogs and packages MUST be usable directly by Claude Code, Claude Desktop Code, Codex CLI, and Codex Desktop without requiring consumers to clone the repository or run the generator.

#### Scenario: Add marketplace by repository reference
- **WHEN** a user follows the documented add-marketplace command or desktop flow
- **THEN** the host can enumerate eligible local plugins from the committed projection

#### Scenario: Refresh a cached marketplace
- **WHEN** a published plugin version changes
- **THEN** documentation provides the host-specific refresh, reload, trust, and cache behavior needed to observe the new version

### Requirement: Supported platform boundary
Repository-owned plugins and their installation validation MUST support current macOS and Linux environments with Node 22 available. The packages MUST NOT claim Windows support in version 1.

#### Scenario: Install on a supported platform
- **WHEN** a local plugin is installed in an isolated macOS or Linux home
- **THEN** its generated manifest, skills, and executable hook scripts resolve without developer-machine absolute paths

#### Scenario: Read supported-platform documentation
- **WHEN** a user evaluates the marketplace requirements
- **THEN** macOS and Linux are listed as supported and Windows is explicitly deferred
