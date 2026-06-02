# Changelog — bonboncinnabon marketplace

Marketplace-level changes: plugin additions, structure, and conventions. Each
plugin keeps its own changelog (e.g. `plugins/butler/CHANGELOG.md`).

## 2026-06-02

### Added
- **butler** `0.3.0` — personal contexts (work | personal) + `butler:decompose` skill; intake interview hard-gate; context-aware `plan`/`reschedule` (work packed, personal light reminders). Release tag `butler--v0.3.0`. See `plugins/butler/CHANGELOG.md`.
- **butler** `0.3.1` — review-driven hardening: schema `$id`/versioning fix, `reminder.triggers` array, `priority` disambiguation, intake/decompose trigger tightening, +4 packer tests. Release tag `butler--v0.3.1`.
- **butler** `0.4.0` — intake/decompose interviews present discrete decisions as native AskUserQuestion choice cards (prior-progress, shape, stage/tree confirm, context), open prompts stay prose; graceful prose fallback. Release tag `butler--v0.4.0`.
- **butler** `0.5.0` — structured questions extended to plan/reschedule (target-day, must/should/want, keep-or-park, fixed-duties); the choice/open convention made single-source in `interview.md` (skills reference it, don't restate). Release tag `butler--v0.5.0`.

## 2026-06-01

### Added
- **butler** `0.1.0` — personal work planner (TickTick + Google Calendar + Linear), a local plugin at `./plugins/butler`. Release tag `butler--v0.1.0`. See `plugins/butler/CHANGELOG.md`.
- **butler** `0.2.0` — stage-based pipeline decomposition (`chunk_type` → `stage`). Release tag `butler--v0.2.0`.

### Changed
- Converted the marketplace to a monorepo: local utility plugins now live under `./plugins/`. `devlab` and `postgres` remain external GitHub sources.

## Earlier

- Updated the `devlab` entry description for v0.2.0.
- Renamed the marketplace from `claude-plugins` to `bonboncinnabon`.
- Added the `devlab` plugin.
- Initial marketplace with the `postgres` plugin.
