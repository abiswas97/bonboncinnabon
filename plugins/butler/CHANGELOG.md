# Changelog

All notable changes to butler. Versioning follows [SemVer](https://semver.org).

## [0.2.0] - 2026-06-01

### Changed
- **Decomposition is now stage-based and hybrid.** Chunks are stages from a config-defined `pipeline` (research / db / backend / frontend / review / address-comments / qa / deploy) instead of freeform "cognitive arc" steps. Intake picks applicable stages (skips the rest), titles them `stage: qualifier`, and may add ad-hoc chunks. Predictable template, less AI over-specification.
- `chunk_type` → `stage` across schemas, packer, and docs. Calibration and the derived activity bucket now key off `stage` (a better reference class). Added a low-priority `STAGE_RANK` tiebreak so same-bucket chunks read in pipeline order.
- Per-stage defaults for `intensity` and `ai_discount` live in `config.yaml` `pipeline`; overridable per chunk.
- `est0` is set at intake (clarified; was ambiguously "at first scheduling").

### Removed
- The auto-paired verify chunk (`verify_of`). The `review` stage (submit PR + AI-assisted review) absorbs AI-output verification.

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
