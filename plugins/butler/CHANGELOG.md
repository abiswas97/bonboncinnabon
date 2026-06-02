# Changelog

All notable changes to butler. Versioning follows [SemVer](https://semver.org).

## [0.8.0] - 2026-06-02

Calendar sourcing, reserve-only breaks, and a versioned config.

### Added
- **Versioned config.** `config.yaml` carries `config_version` (now `1`) and a new `schemas/config.schema.json` declares the shape the plugin expects (`configVersion`). Every skill runs a shared **config preflight** right after reading the config: versions equal → proceed; file behind → ask to migrate (additive defaults only, bump version, re-read); file ahead → error, don't run. The rule lives once in `template.md` → Config preflight; skills reference it.
- **Calendar sourcing block.** Top-level `calendar: { source, calendars }` (default `primary`). `plan` / `reschedule` detect a connected Google Calendar MCP and read the target day's events from the configured calendars as fixed commitments — the source lives in config, never re-asked. Non-blocking fallback ladder: no MCP → run calendar-blind but say so + suggest connecting one; events scattered across accounts → suggest consolidating.
- **Reserve-only breaks.** `contexts.work.breaks: { lunch_min: 45, decompress_min: 30 }`. Before packing, `plan` reserves lunch + one-or-more decompress breaks (scaled to load) as packer **fixed-commitments** placed around meetings, deferring any break that would interrupt an in-progress focus block. Breaks are constraints the packer subtracts, **never** materialized as TickTick tasks.

### Changed
- Folded the remaining 0.7.0 stage-in-title leftovers to verb-first + `#stage` (intake step 4, template calibration/calendar notes, README design principle).

### Notes
- No code change. Packer (26) + chunk-schema tests pass; `config.yaml` validates against `config.schema.json`.
- Spec: `config-versioning` (new) + `context-aware-scheduling` (modified). See `openspec/changes/butler-calendar-and-breaks`.

## [0.7.1] - 2026-06-02

Genericized for publication — no PII / personal context.

### Changed
- The plugin now reads as a generic tool (requires TickTick + Linear; calendar optional). `config.yaml` ships generic placeholder projects (`Work` / `Personal` / `Home` / `Health`), a placeholder `planning_project` and timezone — adopters edit these to their own TickTick lists. Worked examples, schema `description` fields, and changelog notes use neutral domains (`ABC-123`, `UserProfile`, "checkout") instead of real tickets/fields. Dropped the author email from `plugin.json` / marketplace owner.

### Notes
- No behavior change; docs/config/examples only. Packer + schema tests unchanged.

## [0.7.0] - 2026-06-02

Verb-first task titles; stage moves to a tag.

### Changed
- **Chunk titles are now verb-first next actions**, replacing the `Stage: qualifier` prefix. A chunk opens with a concrete physical-action verb and names the object (e.g. `Verify checkout end to end on both forms`). Free verb choice, but it must name a visible action (no "think about / look into / deal with"). **Reverses 0.6.0's "stage stays in the title prefix"** — validated by research (GTD, bullet-journal, productivity forums, ADHD task-initiation; McCrea et al. 2008 on concrete construal → earlier initiation).
- **Stage moves from the title prefix to a tag** (`#research`…`#deploy`), a managed family parallel to `#intensity`. Calibration groups by the stage tag (legacy title-prefix titles parse as a fallback); the packer still reads stage from packer-input at plan time, so ordering is unchanged.
- **Parents stay outcome nouns, not verb-first** (the GTD project-vs-action split). The title keeps the object and one disambiguating cue; the test-matrix / conditions / AC / links move to the body or subtasks.
- One-time setup gains the `#stage` tag family.

### Notes
- References + config + schema docs only (`task-contract.md`, `heuristics.md`, `template.md`, `config.yaml`, `chunk-task.schema.json`). No code; packer + schema tests unchanged.
- an example QA chunk + spike trees were migrated to the new convention as the reference example.
- Spec: `task-titles` (new) + `task-contexts` (modified). See `openspec/changes/butler-verb-first-task-titles`.

## [0.6.1] - 2026-06-02

### Changed
- **Plan never duplicates what already exists (new default).** `plan` now reconciles against open tasks AND recurring habits (`list_habits`) before scheduling: a routine already covered by a habit (reading, pet care, finance checks, the planning ritual) or an existing task is treated as already-handled and is NOT recreated. It schedules only the gap — net-new work, plus dateless existing tasks which get a date rather than a recreated copy. Added as a Core rule in `plan` + `reschedule` and the lead principle in `references/heuristics.md` → Reconciliation.

### Notes
- References/skills only; no code/schema/config change. (The `context-aware-scheduling` baseline spec can absorb this as a MODIFIED requirement in a later change.)

## [0.6.0] - 2026-06-02

Lean, human-first task descriptions.

### Changed
- **Chunk descriptions are now a launchpad, not a spec.** New form: a prose first action, an optional single `Done when …` line (no `Done:` heading), the estimate as `~60m`, and a Markdown link to the source ticket. Dropped the `Why / Where / Ref` labels and the `est0: … stage: … ai: …` footer. Detail and acceptance criteria stay on Linear (the system of record) instead of being duplicated.
- **`est0:` → `~60m`.** The estimate keeps its meaning (immutable, never overwritten on reschedule — the calibration anchor); only the cryptic label changes. Calibration is preserved.
- **Stage moves to the title prefix only** (`Backend: …`); `ai_discount` is no longer written into the description (it defaults from the stage). Calibration groups by stage.
- **Multi-criteria acceptance → real subtasks** (`butler:decompose`), never a `- [ ]` checklist inside a description. A single signal stays one `Done when …` line.
- Personal chunks use the same shape minus the link; parent work-units keep their `Linear / Ticket / Branch` header.

### Notes
- References-and-schema only (`task-contract.md`, `template.md`, `heuristics.md`, `chunk-task.schema.json` field docs). No code/config; packer + schema tests unchanged.
- an example QA subtree was retrofitted to the new format as the reference example.

## [0.5.0] - 2026-06-02

Completes the structured-interview rollout and makes the convention single-source.

### Added
- **`plan` and `reschedule` now use structured questions** too: target-day (today/tomorrow), per-chunk commitment (must/should/want), reconcile keep-or-park, and the fixed-duties calendar read-back are AskUserQuestion choices; "what got in the way?", "anything new today?", and off-calendar duty details stay prose.
- `[choice]`/`[open]` tags + inline option labels added to the Target day, Plan / reconcile, Reschedule, and Fixed duties banks.

### Changed
- **Single source of truth for the convention (DRY).** `references/interview.md` → Presentation is now the *only* place the choice/open mechanic is defined; it carries a canonical pointer sentence. All four skills (`intake`, `decompose`, `plan`, `reschedule`) reference the convention via that pointer + the banks' per-question tags instead of restating the AskUserQuestion mechanics. `AskUserQuestion` is named in exactly one file; changing how questions are asked is now a one-file edit.
- Refactored `intake`/`decompose` from their 0.4.0 inlined mechanics to the shared pointer (gate "do not proceed" salience preserved).

### Notes
- Presentation only — no task-model, schema, packer, config, or scheduling change. Conversational discipline (one thread, 4-question ceiling) and the prose fallback are unchanged.

## [0.4.0] - 2026-06-02

### Added
- **Structured interview questions.** `intake` and `decompose` now present discrete interview decisions as native AskUserQuestion choice cards instead of free-text prose — prior-progress (fresh/begun), shape (single-action/multi-step), stage/tree confirmation, and (decompose) the work-vs-personal context confirmation. Open-ended prompts (done-criteria, first physical action, blockers, estimates) stay free text.
- `references/interview.md` gains a "Presentation" convention: every question is tagged `[choice]` (AskUserQuestion, with suggested option labels listed inline) or `[open]` (prose).

### Notes
- Conversational discipline preserved: one main thread at a time, the 4-question batch is a ceiling not a target.
- Graceful degradation: every `[choice]` is phrased to remain answerable as prose on harnesses without AskUserQuestion — no hard dependency on the tool.
- Scope is `intake` + `decompose`; `plan`/`reschedule` interview forks are unchanged this release. No task-model, schema, packer, config, or scheduling change.

## [0.3.1] - 2026-06-02

Review-driven hardening of the 0.3.0 release. No behavior change to scheduling.

### Fixed
- Schema `$id`s corrected from the stale `abiswas97/butler` path to the real `abiswas97/bonboncinnabon` monorepo path; all four schemas now carry an explicit `version` pinned to the plugin release (answering "is the schema versioned?").
- `chunk-task` `reminder` now models `triggers` as a non-empty array, matching TickTick's `reminders[]` shape (was a single `trigger` string, which couldn't express "at due AND 15m before").
- Disambiguated the two `priority` fields with `$comment`s — parent-task = TickTick numeric priority (0/1/3/5); chunk-task = must/should/want commitment TAG — so the shared name can't be conflated.
- Tightened `intake` vs `decompose` trigger descriptions to remove overlapping bare verbs ("break this down" now belongs to decompose); trimmed a behavioral rule out of intake's description.
- Added reciprocal "keep stage enum in sync with config.yaml `contexts.work.pipeline`" notes on the duplicated stage enums (config is the SSOT).

### Added
- Packer tests for empty input, the >`max_musts` warning, `deep_first: false` ordering, and recharge-dropped-at-window-end (19 → 23 tests). `pack_schedule.py` itself is unchanged.

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
- A chunk with no `context` field is treated as `work` — existing 0.2.0 trees (e.g. ABC-123) work unchanged.

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
