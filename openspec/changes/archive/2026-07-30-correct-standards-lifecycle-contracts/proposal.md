## Why

The unreleased Standards lifecycle contract currently registers host events that
cannot safely carry its advisory response and omits delegated-agent delivery.
Correcting the contract before `0.1.0` is public keeps automatic guidance valid,
portable, and low-context across Claude Code and Codex.

## What Changes

- Generate purpose-specific Claude and Codex hook maps instead of identical maps.
- Deliver session guidance through `SessionStart`, including bounded Git context
  only when the source is `compact`.
- Deliver the exact commandments and precedence rule to newly started subagents.
- Retain plan and edit guidance through host-supported events while emitting only
  fields allowed for each registered event.
- **BREAKING** Remove the unreleased `complete` lifecycle and the invalid
  `PreCompact` and `Stop` advisory responses.
- Add an explicit Codex hook manifest path and deterministic host-contract tests.
- Add an authenticated, opt-in release smoke test without adding it to ordinary CI.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `engineering-standards`: Refine automatic session, compaction, planning,
  editing, and subagent delivery while removing completion-hook semantics.
- `plugin-portability-validation`: Validate intentionally different host hook
  maps, explicit Codex hook discovery, and authenticated lifecycle release smoke.

## Impact

This affects the Standards runtime adapters and resolver, generated host
manifests and hook maps, registry schemas and fixtures, portability validators,
tests, release documentation, and the `0.1.0` changelog. It adds no MCP server,
permission automation, forced continuation, language toolchain execution,
Windows support, Butler behavior, devlab behavior, or postgres behavior.
