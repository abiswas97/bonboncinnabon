# Changelog

## [0.1.2] - 2026-07-31

### Added

- Added bounded, edit-time guidance for durable source comments, including
  legitimate contracts and safety exceptions without heuristic scoring or
  automatic comment removal.

Release tag: `standards--v0.1.2`.

## [0.1.1] - 2026-07-31

### Fixed

- Restored Claude's conventional `hooks/hooks.json` package layout and moved
  the Codex hook map to the explicitly declared `hooks/codex-hooks.json`, so
  Claude no longer auto-discovers and runs the Codex commands alongside its own.

Release tag: `standards--v0.1.1`.

## [0.1.0] - 2026-07-30

### Added

- Ten canonical engineering commandments and precedence rule.
- Structured supporting-rule registry and repository overlays.
- Advisory host-specific Claude and Codex lifecycle hooks with bounded, deduplicated output.
- Automatic root-session, compacted-continuation, plan, edit, and subagent delivery.
- Safe compact Git context and minimal seven-day delivery state.
- `standards` and `standards-init` skills with native host metadata.
- Dual-host manifests and deterministic package-shape validation.

### Changed

- Removed the unreleased completion lifecycle and invalid `PreCompact`/`Stop`
  advisory responses before the initial release.
- Codex declares its hook map explicitly and pins host validation to `0.146.0`.

Release tag: `standards--v0.1.0`.
