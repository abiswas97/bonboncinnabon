# Changelog — bonboncinnabon marketplace

Marketplace-level changes: plugin additions, structure, and conventions. Each
plugin keeps its own changelog (e.g. `plugins/butler/CHANGELOG.md`).

## 2026-06-02

### Added
- **butler** `0.3.0` — personal contexts (work | personal) + `butler:decompose` skill; intake interview hard-gate; context-aware `plan`/`reschedule` (work packed, personal light reminders). Release tag `butler--v0.3.0`. See `plugins/butler/CHANGELOG.md`.
- **butler** `0.3.1` — review-driven hardening: schema `$id`/versioning fix, `reminder.triggers` array, `priority` disambiguation, intake/decompose trigger tightening, +4 packer tests. Release tag `butler--v0.3.1`.
- **butler** `0.4.0` — intake/decompose interviews present discrete decisions as native AskUserQuestion choice cards (prior-progress, shape, stage/tree confirm, context), open prompts stay prose; graceful prose fallback. Release tag `butler--v0.4.0`.
- **butler** `0.5.0` — structured questions extended to plan/reschedule (target-day, must/should/want, keep-or-park, fixed-duties); the choice/open convention made single-source in `interview.md` (skills reference it, don't restate). Release tag `butler--v0.5.0`.
- **butler** `0.6.0` — lean, human-first task descriptions (first action + `Done when …` + `~60m` + Linear link; dropped labels/jargon; `est0`→`~60m` keeps calibration; multi-criteria → subtasks). Release tag `butler--v0.6.0`.
- **butler** `0.6.1` — plan never duplicates existing tasks/habits: reconciles against open tasks + `list_habits`, schedules only the gap, dates dateless-existing rather than recreating. Release tag `butler--v0.6.1`.
- **butler** `0.7.0` — verb-first task titles (chunks lead with a concrete verb + object; parents stay outcome nouns); stage moves from the title prefix to a `#stage` tag (calibration + packer read the tag). Reverses 0.6.0's title-prefix decision; research-backed. Release tag `butler--v0.7.0`.
- **butler** `0.7.1` — genericized for publication: PII/personal-context scrubbed from config, worked examples, schema docs, and changelog notes (generic projects + neutral example domains; author email dropped). Release tag `butler--v0.7.1`.
- **butler** `0.8.0` — calendar sourcing (`plan`/`reschedule` read configured Google Calendars via MCP as fixed commitments, with a non-blocking fallback ladder); reserve-only breaks (lunch + scaled decompress reserved as packer constraints, never tasks); versioned config (`config_version` + `schemas/config.schema.json` + a shared migrate-on-read preflight). Release tag `butler--v0.8.0`.
- **butler** `0.9.0` — research-grounded accommodations layer (single-source evidence-tagged `<accommodations>`: action-first, if-then-cue, mastery+pleasure, flexibility-with-spine, non-punitive, tone, + a do-not list; five literature reviews behind it); burnout detection (rolling-window, rising-edge, personal-baseline, asks-never-acts, never adds a task); low-energy reduced mode; `pacing` config block (`config_version` 1 → 2). Release tag `butler--v0.9.0`.
- **butler** `0.10.0` — **BREAKING:** config moves to the global, update-surviving `${CLAUDE_PLUGIN_DATA}/config.yaml` (off the ephemeral plugin root; never committed); in-repo config becomes `config.example.yaml` (template); new `/butler:setup` interviews + writes + validates the global config (idempotent). Backed by live-docs + real-plugin research. Release tag `butler--v0.10.0`.
- **butler** `0.10.1` — patch: add the missing `commands/setup.md` wrapper so the setup skill surfaces as the namespaced `/butler:setup` (0.10.0 shipped the skill without a command wrapper, leaving it as a bare `/setup`). Release tag `butler--v0.10.1`.

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
