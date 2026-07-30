## Context

Bonboncinnabon currently exposes a Claude marketplace containing one repository-owned plugin, Butler, plus two externally hosted Claude plugins. Butler's Claude manifest is hand-authored, the repository has no Codex marketplace projection, and there is no root build or validation workflow.

The change introduces a second repository-owned plugin, Standards, whose policy must remain identical across Claude Code and Codex CLI/Desktop while respecting the different manifest and hook contracts of each host. The implementation must support macOS and Linux, keep runtime dependencies small, preserve Butler's behavior, leave the external `devlab` and `postgres` entries intact for Claude, and avoid placing SAAF-specific policy in this repository.

The standards content is guidance for one developer rather than organization-wide enforcement. Version 1 therefore prioritizes portability, low context cost, explainable behavior, and reliable packaging over broad language-specific automation.

## Goals / Non-Goals

**Goals:**

- Establish one host-neutral source of truth for repository-owned marketplace and plugin metadata.
- Generate and commit valid Claude and Codex projections deterministically.
- Make Butler and Standards installable from the same repository in both hosts.
- Encode the ten approved commandments and portable supporting rules without SAAF-specific assumptions.
- Deliver lifecycle-aware, path-aware, and role-aware guidance with bounded output and no successful-hook noise.
- Provide repository overlays without allowing a project to silently rewrite the commandments.
- Validate generation, manifests, hook payload handling, installation, and release consistency on macOS and Linux.

**Non-Goals:**

- Windows support.
- Bundling or redesigning `devlab`, `postgres`, or any plugin maintained in another repository.
- Language-specific compiler, formatter, linter, or static-analysis orchestration for Rust, Python, Go, TypeScript, or other ecosystems.
- Automatic source formatting or mutation.
- Blocking edits, plans, commits, or session completion from hooks in version 1.
- Making Claude and Codex runtime behavior byte-for-byte identical where their lifecycle models differ.
- Replacing host-native repository instructions such as `CLAUDE.md` or `AGENTS.md`.

## Decisions

### 1. Use neutral JSON records and generated host projections

The canonical marketplace record will live at `marketplace/marketplace.json`. Each repository-owned plugin will have a canonical `plugins/<name>/plugin.json`. These records will contain shared identity, version, description, repository source, components, and explicit host eligibility.

A Node 22 standard-library generator at `tools/portability/sync-plugins.mjs` will produce:

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `plugins/<name>/.claude-plugin/plugin.json`
- `plugins/<name>/.codex-plugin/plugin.json`
- generated Codex skill UI metadata under each skill's `agents/openai.yaml`
- thin host-specific hook maps that reference shared scripts

Generated files will be committed and carry a generated-file marker where their format permits it. `--check` will regenerate in memory and fail on missing, stale, extra, or nondeterministically ordered projections.

JSON is preferred over YAML or executable configuration because Node can parse and validate it without runtime dependencies. Host projections remain separate because Claude and Codex schemas are genuinely different; forcing one manifest to masquerade as both would make host quirks part of the canonical model.

### 2. Project only plugins that are valid for a host

The canonical marketplace record will distinguish local repository-owned plugins from passthrough external entries and declare supported hosts. Claude generation will preserve `devlab` and `postgres` unchanged. Codex generation will omit those entries until their source repositories publish valid native Codex packages.

An unsupported plugin will be omitted with a deterministic diagnostic during generation, not represented by a broken placeholder. This preserves the current Claude marketplace while ensuring every Codex catalog entry can actually be installed.

### 3. Keep one marketplace with two cohesive local plugins

Butler remains a focused planning plugin. Standards is a separate plugin containing commandments, standards guidance, lifecycle hooks, and standards-related skills. The repository will not create one plugin per language or per commandment.

This keeps installation and release ownership understandable: users can install Butler, Standards, or both, while cross-language principles remain one coherent policy. Future language analyzers can become separate optional plugins only when they add substantial dependencies, executables, or independent release cadence.

### 4. Treat standards prose and rule metadata as different artifacts

The full commandments will live in a canonical human-readable document at `plugins/standards/standards/commandments.md`. Supporting rules will live in `plugins/standards/standards/registry.json` with stable IDs, title, compact summary, guidance class, lifecycle phases, path selectors, role selectors, and a reference document.

The ten commandments are:

1. Architecture over local expedience.
2. One authoritative representation.
3. Proportional blast radius.
4. Make variation explicit.
5. Prepare for evidenced change.
6. Legible structure.
7. Optimize for recovery of understanding.
8. Explicit effects, contract-tested seams.
9. Evidence over confidence.
10. Model the domain; make invalid states unrepresentable.

Correctness, safety, and explicit requirements take precedence over the commandments. When commandments compete, guidance will ask the agent to state the trade-off, prefer evidence, and minimize long-term change cost.

The prose is not encoded as XML. Stable Markdown headings and IDs are sufficient for human and model navigation; JSON supplies the machine-readable structure. This avoids XML token overhead and duplicated representations while retaining unambiguous sections.

### 5. Use layered standards resolution with immutable commandments

The default registry applies everywhere. A repository can add `.standards/standards.json` with `extends: "default"` and rule entries keyed by stable ID. Repository rules can add guidance, narrow applicability, or override supporting rule text. Omitting `extends` creates a supporting-rule replacement layer.

The commandments and their precedence rule are always included and cannot be removed or redefined by an overlay. Unknown fields, duplicate IDs, invalid selectors, attempts to replace commandments, and unsupported schema versions fail validation with an actionable location.

Host-native instructions remain a later layer of context and are not generated or rewritten. If an explicit repository instruction conflicts with a supporting default rule, the explicit repository instruction wins; hooks report the conflict instead of pretending both can be satisfied.

### 6. Share behavior, adapt lifecycle events

Shared Node modules will parse host input into a neutral event containing host, lifecycle, session ID, repository root, affected paths, tool category, and optional plan/completion context. Small Claude and Codex entry points will translate native payloads into that event and render native output.

Lifecycle behavior will be:

- Session start: inject the full commandments, precedence rule, and a compact index of core supporting rules once.
- Compaction/session resume: re-inject the same durable policy plus compact Git context because earlier context may have been summarized away.
- Planning: surface only applicable planning rule IDs and short corrective guidance.
- Editing: extract all affected paths and surface only newly relevant path/role rule IDs.
- Completion: remind the agent of missing verification evidence when the host exposes a suitable event.

Claude-specific events such as `PreToolUse` for `ExitPlanMode` will not be invented in Codex. Codex-specific tool payloads will not leak into shared policy. Unsupported lifecycle events degrade to no output.

All version 1 hooks are advisory: they will not return a deny, ask, or continue-loop decision. CI validation is the only hard gate.

### 7. Bound output and deduplicate within a session

Successful hooks produce no output. Session-start output is capped at 7,000 characters; all other lifecycle output is capped at 2,500 characters and at six cited rule IDs. Longer details are referenced by stable ID and skill path rather than repeated.

Per-session delivery state will be stored as small atomic JSON files under the host-provided plugin data directory, preferring `PLUGIN_DATA` and accepting `CLAUDE_PLUGIN_DATA` as a compatibility alias. State is keyed by host and host-provided session ID, contains no prompts, source, diffs, or secrets, and records only delivered rule IDs and timestamps. Entries older than seven days are pruned opportunistically.

When no stable session ID or writable data directory exists, hooks remain correct but may repeat guidance. They must not fail the host session merely because deduplication is unavailable.

### 8. Make compact Git context the only dynamic repository sensor

Session and compaction hooks may report repository root, branch, detached-head state, a capped list/count of changed paths, and a short recent-commit summary. They will not include raw diffs, file contents, commit bodies, untracked file contents, remote URLs, environment variables, or resolved credentials.

Commands use argument arrays, timeouts, capped stdout/stderr, and graceful fallbacks when Git is absent or the directory is not a repository. This keeps useful orientation from the prior Cloak setup without reintroducing noisy formatter, TODO, test-reminder, search-reminder, or regex-security hooks.

### 9. Expose standards through skills, with thin Claude command wrappers

Standards will provide two canonical skills:

- `standards`: explain the commandments and show effective rules for the current task or path.
- `standards-init`: inspect a repository and propose a minimal `.standards/standards.json` overlay, writing it only after explicit confirmation.

Claude slash-command files will be thin wrappers around these skills. Codex discovery metadata will be generated beside the canonical skills. Commands will not duplicate the standards prose.

### 10. Use Node 22 without runtime packages; pin validation CLIs

Generators, hook handlers, validators, and tests will use Node 22 built-ins. A root `package.json` will define the engine and scripts. Exact Claude Code and Codex CLI versions used for strict validation will be development dependencies recorded in the lockfile, not plugin runtime dependencies.

This gives reproducible CI contracts while keeping installed plugins self-contained. The project will update pinned host validators deliberately when host schemas change.

### 11. Commit projections and validate on both supported operating systems

Committed projections make marketplace URLs directly consumable without asking users to run a build and make release diffs reviewable. CI will run an Ubuntu/macOS matrix for generation checks, unit and fixture tests, path handling, and isolated home-directory installation smoke tests.

Strict host commands will validate the generated Claude and Codex packages when the host exposes such validation. Repository validators will additionally enforce contracts not covered by host CLIs, including external-entry filtering, output budgets, no absolute developer paths, no secrets, and version consistency.

### 12. Version local plugins independently

Butler will receive a minor version bump for its new Codex packaging while preserving behavior. Standards will begin at `0.1.0`. Canonical records are authoritative; generated manifests, version-bearing marketplace entries, changelog headings, and release tags must agree. Codex marketplace entries do not carry a version in the native schema, so their referenced `.codex-plugin/plugin.json` is the version-bearing contract.

The existing Butler command frontmatter will be made valid under strict Claude validation as part of the packaging migration, without changing command behavior.

## Risks / Trade-offs

- **[Host schemas and hook payloads evolve independently]** → Pin validator versions, keep adapters thin, retain captured payload fixtures, and fail generation when a projection cannot express a canonical capability.
- **[Committed generated files can be edited manually]** → Mark them as generated, provide one sync command, and make `--check` mandatory in CI.
- **[Advisory hooks can be ignored]** → Keep version 1 non-disruptive, measure usefulness through focused fixtures and real use, and promote only deterministic checks to enforcement in a later change.
- **[Full commandments consume session context]** → Inject them only at session start and compaction, use compact IDs afterward, cap output, and keep supporting prose on demand.
- **[Repository overlays create policy ambiguity]** → Validate precedence explicitly, keep commandments immutable, and expose the resolved rule set through the `standards` skill.
- **[Session state can become stale or unwritable]** → Store only non-sensitive delivery metadata, write atomically, prune old entries, and treat state as an optimization rather than a correctness dependency.
- **[External Claude plugins make the neutral catalog appear asymmetric]** → Model host eligibility explicitly and document why unsupported external entries are absent from Codex.
- **[Pinned host CLIs increase development install size]** → Keep them development-only and isolate plugin runtime tests from validator installation.
- **[Codex CLI and Desktop may share package semantics but differ in refresh UX]** → Document install, reload, trust, and cache behavior separately and smoke-test the package contract rather than assuming UI parity.

## Migration Plan

1. Add the root Node toolchain, canonical schemas, generator, and tests without changing the published Claude projection.
2. Import Butler metadata into the canonical record, generate both manifests, fix strict frontmatter validation, and prove its existing Python tests and Claude behavior still pass.
3. Add the Standards canonical content, registry, overlay resolver, shared hook core, host adapters, skills, and fixtures.
4. Generate and commit both marketplace projections and all local plugin projections.
5. Add macOS/Linux CI, isolated marketplace/plugin install smoke tests, documentation, changelogs, and version consistency checks.
6. Release Butler and Standards independently after installing each from the repository in clean Claude and Codex homes.

Rollback consists of reverting the generated Codex catalog and new Standards entry, restoring the previous Claude marketplace projection, and releasing corrected plugin versions. Existing installed plugin versions remain cacheable and independently addressable; rollback must not rewrite an already published tag.

## Open Questions

None for version 1. Language-specific analyzers, stronger enforcement, Windows support, and native packaging of external plugins require separate evidence and proposals.
