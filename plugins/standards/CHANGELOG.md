# Changelog

## [0.1.0] - 2026-07-30

### Added

- Ten canonical engineering commandments and precedence rule.
- Structured supporting-rule registry and repository overlays.
- Advisory host-specific Claude and Codex lifecycle hooks with bounded, deduplicated output.
- Automatic root-session, compacted-continuation, plan, edit, and subagent delivery.
- Safe compact Git context and minimal seven-day delivery state.
- `standards` and `standards-init` skills with native host metadata.
- Dual-host manifests and isolated installation validation.
- Authenticated opt-in lifecycle release smoke for real host execution.

### Changed

- Removed the unreleased completion lifecycle and invalid `PreCompact`/`Stop`
  advisory responses before the initial release.
- Codex declares its hook map explicitly and pins host validation to `0.146.0`.

Release tag: `standards--v0.1.0`.
