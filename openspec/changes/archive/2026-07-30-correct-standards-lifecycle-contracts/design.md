## Context

Standards is intended to be automatic and advisory. The first portable
implementation generated the same hook map for Claude and Codex, used a generic
`additionalContext` response for every lifecycle, and modeled a `complete`
lifecycle through `Stop`. Current host contracts do not make that response
model-visible on every event, while delegated subagents receive no automatic
standards at all.

The correction must land before the unreleased `0.1.0` contract becomes public.
Claude Code and Codex CLI/Desktop remain the supported hosts on macOS and Linux.

## Goals / Non-Goals

**Goals:**

- Register only lifecycle events whose response contracts Standards uses.
- Keep root sessions, compacted continuations, and subagents automatically covered.
- Keep later plan and edit guidance bounded and deduplicated.
- Generate host-specific artifacts from one neutral source.
- Prove deterministic contracts in CI and real host delivery in an opt-in smoke.

**Non-Goals:**

- Blocking completion, auto-approving permissions, or forcing continuation.
- Adding MCP, language-specific tooling, Windows support, Butler, devlab, or
  postgres behavior.
- Treating a copied plugin directory as evidence that a host executed its hooks.

## Decisions

### Register a smallest useful host event set

Both hosts register `SessionStart`, `UserPromptSubmit`, `PostToolUse`, and
`SubagentStart`. Claude additionally registers `PreToolUse` for `ExitPlanMode`.
This preserves the proven plan fallback without pretending Codex exposes the same
tool boundary. `PreCompact` and `Stop` are removed because their response
contracts do not support the advisory context Standards was emitting.

### Route compaction through SessionStart source

`SessionStart` with `startup`, `resume`, or `clear` emits the exact commandments,
precedence rule, and supporting-rule index. Source `compact` emits the same
guidance plus bounded secret-safe Git context. This uses the host-supported
post-compaction session boundary rather than responding to `PreCompact`.

### Give subagents a deliberately smaller automatic payload

`SubagentStart` emits the exact commandments and precedence rule, with neither
the supporting index nor Git context. This covers delegated work at a predictable
cost while keeping repository-wide detail in the root session.

### Construct native output per event

The adapter maps only registered events and has an allowlist of context-capable
events. It creates native output after lifecycle resolution rather than wrapping
every result in one generic shape. Unregistered events and normal irrelevant
events remain silent.

### Remove completion before release

The neutral `complete` lifecycle is removed from schemas, registry records,
validators, fixtures, skills, and specifications. Verification advice remains in
`plan` and/or `edit`, while deterministic validation is the release hard gate.

### Separate deterministic CI from authenticated host proof

Ordinary CI runs schema, generator, unit, replay, installation, and Butler tests
on macOS and Ubuntu. A separate opt-in command installs into temporary host homes
and makes authenticated model calls to exercise lifecycle delivery. Codex
app-server trust is limited to the exact hashes returned by its current hook list.

## Risks / Trade-offs

- **A Codex surface omits `permission_mode: "plan"`** → Session guidance remains
  the portable baseline; the live release probe records the observed value.
- **Subagents receive fewer supporting details** → They receive all immutable
  commandments and precedence while avoiding repeated index and Git token cost.
- **Host hook schemas change** → Pinned host validation and authenticated smoke
  make the drift visible before release.
- **Live smoke is credentialed and nondeterministic** → It is explicit opt-in,
  secret-safe, and excluded from ordinary CI.

## Migration Plan

1. Add failing contract tests for the corrected host maps and outputs.
2. Update the neutral runtime, schemas, generator, and canonical registry.
3. Regenerate and validate both host projections.
4. Add documentation and opt-in live smoke coverage.
5. Sync the delta requirements to the main specifications and archive this change.

Rollback is the focused follow-up commit; no public released contract or stored
user data requires migration.

## Open Questions

None. Host confirmation prompts remain explicitly owned by each installed host.
