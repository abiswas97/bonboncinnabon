# Changelog — bonboncinnabon marketplace

Marketplace-level changes: plugin additions, structure, and conventions. Each
plugin keeps its own changelog (e.g. `plugins/butler/CHANGELOG.md`).

## 2026-06-01

### Added
- **butler** `0.1.0` — personal work planner (TickTick + Google Calendar + Linear), a local plugin at `./plugins/butler`. Release tag `butler--v0.1.0`. See `plugins/butler/CHANGELOG.md`.

### Changed
- Converted the marketplace to a monorepo: local utility plugins now live under `./plugins/`. `devlab` and `postgres` remain external GitHub sources.

## Earlier

- Updated the `devlab` entry description for v0.2.0.
- Renamed the marketplace from `claude-plugins` to `bonboncinnabon`.
- Added the `devlab` plugin.
- Initial marketplace with the `postgres` plugin.
