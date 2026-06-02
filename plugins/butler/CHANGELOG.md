# Changelog

All notable changes to butler. Versioning follows [SemVer](https://semver.org).

## [0.3.0] - 2026-06-02

### Added
- **Personal contexts.** `config.yaml` now defines `contexts` (work | personal). A task's context is derived from its TickTick project and confirmed with the user (never silent); an unmapped project prompts. Work keeps the full pipeline model; personal drops the `stage`/`intensity`/`ai_discount` axes and carries only `priority` + `est0` + a reminder.
- **`butler:decompose`** — break down a task that ALREADY exists in TickTick, interview-first and context-aware. Resolves the task by name/search or pick-from-undecomposed, derives + confirms context, augments an already-split task without duplicating, then splits work into pipeline stages or personal into free-form steps (or not at all). The existing task becomes the parent.
- **Light personal scheduling.** `plan` schedules personal items as a due time + reminder (never a packed focus block). On defer, the time is derived from a live read of the day — the day's existing TickTick timed items + Calendar — placed in an open slot. Work and personal are shown as separated sections.
- `chunk-task.schema.json`: a `context` enum and a `reminder` object, with conditional axes — `stage`/`intensity`/`ai_discount`/`est0_min` required only for work and forbidden for personal (`if`/`then`/`else`).

### Changed
- **The intake interview is now a HARD GATE** (was mandated but skippable): intake and decompose must confirm intent / prior progress / single-vs-multi-step before producing any tree, with an explicit "do not proceed until X" red-flags block.
- Folded work scheduling config (`work_window`, `pipeline`, `capacity`, `intensity_tags`, `recharge_tag`, `executes_with_ai`, `points_calibration`) under `contexts.work`; renamed `work_project` → `contexts.work.default_project`. Cross-context infrastructure (`planning_project`, `priority_tags`, `ai_tag`, `parked_tag`, `ritual`) stays top-level. The packer script and its 19 tests are unchanged.
- `plan` / `reschedule` are context-aware: work via the packer (unchanged), personal as light reminders not repacked.

### Compatibility
- A chunk with no `context` field is treated as `work` — existing 0.2.0 trees (e.g. ING-165) work unchanged.

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
