# Changelog

## [0.1.0] - 2026-10-09

### Added

- Six skills for Claude Code and Codex: `setup`, `onboard`, `sync`, `backup`,
  `configure` and `cheats`.
- One profile shared by both hosts at
  `${XDG_CONFIG_HOME:-~/.config}/bonboncinnabon/gaming/profile.json`, written
  only by `scripts/gaming_profile.py` with validation, history copies and
  atomic replacement.
- Frontend baselines with a drift check, scripted library checks, a
  non-destructive tree sync, read-only device snapshots and DAT-based ROM
  verification, all standard-library Python with tests.
- Shared references for the library layout, verification, device
  installation, frontend baselines, RetroArch and ES-DE.

Release tag: `gaming--v0.1.0`.
