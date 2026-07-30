## Why

Bonboncinnabon is currently a Claude-only marketplace with manually duplicated plugin metadata, while the desired standards behavior must work consistently in Claude Code and Codex CLI/Desktop without copying host-specific logic or importing SAAF-specific policy. A neutral source model and generated host projections will make Butler portable and provide one maintainable home for the approved personal engineering commandments and standards.

## What Changes

- Add a host-neutral marketplace and plugin metadata model that deterministically generates the committed Claude and Codex marketplace catalogs, plugin manifests, skill UI metadata, and host-specific hook maps.
- Make `butler@bonboncinnabon` installable through both Claude and Codex while preserving its existing behavior and Claude namespace.
- Add `standards@bonboncinnabon` with the ten approved engineering commandments, portable supporting standards, path and role scoping, repository overlays, and advisory lifecycle guidance.
- Inject the complete commandments once at session start and after compaction, then use compact rule IDs for plan, edit, and completion feedback.
- Support macOS and Linux with Node 22 standard-library tooling; defer Windows and polyglot compiler/linter orchestration to later changes.
- Add deterministic generation, schema/contracts, strict host validation, isolated install smoke tests, and release/version drift checks.
- Preserve the existing external `devlab` and `postgres` Claude marketplace entries unchanged and exclude them from the Codex projection until their repositories publish native Codex packages.

## Capabilities

### New Capabilities

- `portable-plugin-marketplace`: Canonical marketplace/plugin metadata, generated Claude and Codex projections, and dual-host installation of local plugins.
- `engineering-standards`: The commandments, supporting rule registry, repository overlays, skills, and advisory lifecycle behavior for Claude and Codex.
- `plugin-portability-validation`: Deterministic generation checks, host contract validation, isolated installation tests, and release/version consistency.

### Modified Capabilities

None. Butler's planning behavior and existing product specifications remain unchanged; this change only adds a second packaging/runtime surface.

## Impact

- Adds a root Node 22 development toolchain and generated-artifact workflow.
- Replaces Butler's hand-authored Claude manifest metadata with generated Claude and Codex projections from one canonical record.
- Adds a new local `plugins/standards` package with command/skill surfaces and command-hook scripts.
- Adds `.agents/plugins/marketplace.json`, `.codex-plugin` manifests, per-skill `agents/openai.yaml`, host-specific hook definitions, tests, and GitHub Actions validation.
- Updates marketplace and plugin documentation with exact Claude Code, Claude Desktop Code, Codex CLI, and Codex Desktop installation/reload/trust behavior.
