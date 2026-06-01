# Changelog

All notable changes to butler. Versioning follows [SemVer](https://semver.org).

## [0.1.0] - 2026-06-01

Initial release.

### Added
- `butler:intake` — break a Linear ticket (explicit ID) or described work into a durable, idempotent task tree in TickTick.
- `butler:plan` — reconcile open work and time-box a target day: today when run in the morning, tomorrow in the evening. Schedules around Google Calendar.
- `butler:reschedule` — recompute today's remaining blocks from the current time.
- Deterministic stdlib packer (`scripts/pack_schedule.py`): focus cap, day slack, transition + recharge buffers, intensity-first ordering, and `chunk_type`-derived activity clustering. 18 unit tests.
- JSON Schemas for the parent/chunk task and packer I/O contracts.
- Anti-slop task writing contract; the `ai` tag marks generated tasks for filtering.
- Selective AI discount with auto-paired verify chunks; immutable `est0` line for calibration.
- `config.yaml` as the sole adopter surface.
