## 1. Root Toolchain and Contracts

- [x] 1.1 Add the Node 22 root `package.json`, exact development-only Claude/Codex validator versions, lockfile, and scripts for generation, checking, tests, host validation, and full CI validation.
- [x] 1.2 Add JSON schemas and fixture tests for the canonical marketplace, local plugin record, standards registry, and repository overlay contracts, including field-level diagnostics for invalid and unsupported versions.
- [x] 1.3 Add canonical `marketplace/marketplace.json` and `plugins/butler/plugin.json` records that reproduce the current Claude marketplace, preserve the external `devlab` and `postgres` definitions, and declare honest host eligibility.

## 2. Deterministic Host Projection

- [x] 2.1 Write failing tests for deterministic ordering, host filtering, missing/stale/extra output detection, unsupported platforms, and preservation of unrelated worktree files.
- [x] 2.2 Implement `tools/portability/sync-plugins.mjs` with explicit generated targets, macOS/Linux validation, atomic writes, and non-mutating `--check` behavior.
- [x] 2.3 Generate Claude and Codex marketplace catalogs, per-host plugin manifests, hook maps, and per-skill Codex UI metadata from canonical records.
- [x] 2.4 Add generated-file markers where schemas permit them and document canonical-versus-generated ownership for contributors.
- [x] 2.5 Verify a second generation is a no-op and `npm run plugins:check` detects a controlled projection drift without modifying the worktree.

## 3. Portable Butler

- [x] 3.1 Bump Butler's canonical version for portable packaging and add its Codex component declarations without changing Butler's skills, commands, or planning semantics.
- [x] 3.2 Quote or otherwise repair the existing `commands/setup.md` frontmatter description so it passes strict Claude validation.
- [x] 3.3 Add or generate Butler's `.codex-plugin` manifest and skill `agents/openai.yaml` files, then verify Claude keeps the existing `butler:` namespace.
- [x] 3.4 Run the existing Butler Python test suite and add a regression assertion that portable generation does not alter its product specifications.

## 4. Standards Content and Resolution

- [x] 4.1 Add `plugins/standards/plugin.json` at version `0.1.0` and the canonical Markdown definition of all ten commandments, precedence rule, and conflict guidance.
- [x] 4.2 Add the default supporting-rule registry with stable IDs, compact summaries, guidance classes, lifecycle selectors, path selectors, role selectors, and detailed Markdown references.
- [x] 4.3 Write failing resolver tests for default inheritance, supporting-rule replacement, added and narrowed rules, unknown fields, duplicate IDs, invalid selectors, and attempted commandment overrides.
- [x] 4.4 Implement repository discovery and resolution of `.standards/standards.json`, keeping commandments immutable and returning actionable diagnostics without partially applying invalid overlays.
- [x] 4.5 Add conflict reporting for explicit host-native repository instructions that supersede default supporting guidance.

## 5. Shared Hook Runtime

- [x] 5.1 Define the neutral lifecycle event and response contracts and add native Claude/Codex fixtures for session, compaction or resume, planning, edit, move, delete, multi-file patch, completion, malformed, incomplete, oversized, and non-repository cases.
- [x] 5.2 Implement Claude and Codex input adapters that normalize repository roots and extract every affected in-repository path without reading paths outside the repository.
- [x] 5.3 Implement lifecycle resolution so session and compaction receive full commandments while planning, editing, and completion receive only applicable compact rule IDs.
- [x] 5.4 Implement deterministic output budgets, six-rule event caps, successful-hook silence, and advisory-only native responses that never deny, ask, or force continuation.
- [x] 5.5 Implement minimal per-session delivery state with atomic writes, `PLUGIN_DATA`/`CLAUDE_PLUGIN_DATA` resolution, seven-day pruning, and graceful stateless fallback.
- [x] 5.6 Implement compact Git context with argument-array execution, timeouts, output caps, safe detached/non-repository fallbacks, and no raw diffs, contents, commit bodies, remotes, environment values, or secrets.
- [x] 5.7 Add security and token-budget tests proving secret-like fixtures, absolute developer paths, unsafe Git data, and oversized guidance never reach hook output or state.

## 6. Standards Skills and Host Wiring

- [x] 6.1 Create the canonical `standards` skill to explain commandments, precedence, and effective supporting rules for a task, role, or path.
- [x] 6.2 Create the canonical `standards-init` skill to inspect a repository and propose the smallest valid overlay while requiring explicit confirmation before writing.
- [x] 6.3 Add thin Claude command wrappers and generate Codex skill UI metadata without duplicating standards prose.
- [x] 6.4 Wire shared handlers into native Claude and Codex hook maps only for lifecycle events each host actually supports, and verify unsupported events emit nothing.
- [x] 6.5 Generate both Standards plugin manifests and verify Standards installs and operates independently of Butler.

## 7. Validation and Installation

- [x] 7.1 Add repository validators for component existence, executable resolution, command frontmatter, host eligibility, output budgets, prohibited absolute paths, generated ownership, and external-entry filtering.
- [x] 7.2 Add strict validation commands using the pinned Claude Code and Codex CLIs, with captured diagnostics for invalid manifests and missing components.
- [x] 7.3 Add deterministic package-shape tests for Claude marketplace entries, manifests, commands, skills, and hooks.
- [x] 7.4 Add deterministic package-shape tests for Codex marketplace entries, manifests, skills, and hooks.
- [x] 7.5 Assert that Claude preserves external entries while Codex omits plugins without native Codex packages.
- [x] 7.6 Add a GitHub Actions Node 22 matrix on current Ubuntu and macOS runners covering generation checks, schemas, unit and payload fixtures, path handling, Butler regressions, strict host validation, and isolated installs.

## 8. Documentation and Release Readiness

- [x] 8.1 Update the root and plugin documentation with exact add-marketplace, install-plugin, reload, trust, refresh, cache, uninstall, and troubleshooting flows for Claude Code, Claude Desktop Code, Codex CLI, and Codex Desktop.
- [x] 8.2 Document macOS/Linux and Node 22 support, the Windows and polyglot-analyzer deferrals, advisory-only hook behavior, overlay precedence, data retention, and the deliberate Codex exclusion of unsupported external plugins.
- [x] 8.3 Add independent Butler and Standards changelog entries and release-tag conventions, then implement a consistency check across canonical records, projections, version-bearing marketplace entries, changelogs, and intended tags.
- [x] 8.4 Run the full `npm run validate` workflow on macOS, confirm CI passes on macOS and Linux, and manually install both plugins in clean Claude and Codex homes before marking the change implementation complete.
