## Why

Two gaps surfaced while dogfooding `plan`: (1) butler scheduled **calendar-blind** —
no way to read meetings — which produced a duplicate (a "PR reviews" task over an
existing calendar block) and two hard conflicts (work over a standup, work over a
check-in). (2) The user needs **lunch and breaks** protected, but butler treated them
inconsistently and even mis-created them as tasks. Both are the same thing: the day
has fixed structure (meetings, meals, breaks) that `plan` must respect as
**constraints**, not invent as tasks.

Persistence is config-only by design: butler's standing tenet is that **state lives
in TickTick + Calendar** (no side store). So the calendar source and break defaults
live in `config.yaml`; anything historical (load, calibration) is **derived from
TickTick** at read time, not stored. No Notion, no plugin data store.

## What Changes

- **Calendar sourcing for `plan`/`reschedule`.** Read the target day's meetings as
  fixed commitments:
  1. If a **Google Calendar MCP is connected**, read the target day's events from the
     calendars named in config.
  2. `config.yaml` gains a `calendar` block (which calendars to read; default to the
     primary). The source is **persisted in config**, not re-asked each run.
  3. **Fallback ladder, non-blocking:** no MCP → say so and suggest connecting one;
     events scattered across many calendars → suggest consolidating to one account (or
     a multi-calendar tool). With no calendar, `plan` runs calendar-blind as today but
     states it.
- **Reserve-only breaks, flexible & multiple.** `config.yaml` `contexts.work.breaks`
  holds defaults (`lunch_min: 45`, `decompress_min: 30`). `plan` reserves a lunch and
  one-or-more decompress breaks as **packer commitments** placed around the day's
  meetings — **never materialized as tasks** — scaling break count/length to the
  focus load and **deferring a break that would interrupt an in-progress block**.
  Adjustable/skippable per plan.
- **Versioned config + migrate-on-read.** Give `config.yaml` a versioned schema
  (`schemas/config.schema.json`, with an integer `config_version`, parallel to the
  task schemas). `config.yaml` carries `config_version`. **Every time a skill reads
  config**, it compares the installed `config_version` to the plugin's current schema
  version: **equal** → proceed; **behind** → tell the user and **ask to migrate**
  (apply defaults for new fields, then proceed); **ahead** → surface an error (the
  config is newer than the plugin — shouldn't happen; don't silently run). This is a
  single shared check all four skills reference.
- **Fold the 0.7.0 cleanup.** Reconcile leftover "stage in the title prefix" /
  "Title = stage + short qualifier" references (intake step 4, template.md, worked
  example) to the verb-first + `#stage`-tag convention.
- **Realign live tasks.** Migrate the ING-149 chunks (still `Stage: qualifier`) to
  verb-first titles + `#stage` tags.

## Capabilities

### New Capabilities
- `config-versioning`: `config.yaml` has a versioned schema (`config_version` +
  `schemas/config.schema.json`); every config read compares installed vs current
  version and proceeds / offers migration (behind) / errors (ahead).

### Modified Capabilities
- `context-aware-scheduling`: add how `plan`/`reschedule` source fixed commitments
  from a calendar (config-driven source + fallback ladder), and that they reserve
  default lunch + flexible/multiple decompress breaks as packer commitments the packer
  subtracts — never as tasks, deferring around in-progress focus.

## Impact

- **Config**: `config.yaml` gains a top-level `config_version`; `contexts.work` gains a
  `breaks` block (`lunch_min`, `decompress_min`); a top-level `calendar` block (source +
  calendar names) is added as a template placeholder. New `schemas/config.schema.json`
  (versioned) defines the config shape + current version.
- **Skills**: `plan`/`reschedule` — calendar-sourcing step (detect MCP → read per
  config → fallback) + reserve breaks as commitments before packing.
- **References**: `heuristics.md` (Fixed-duties/Buffering: breaks reserved not
  materialized, scale-to-load, defer-in-flow; meetings from calendar), `template.md`
  (Calendar mapping + the 0.7.0 stage-in-title cleanup), `intake` SKILL (0.7.0
  stale-line cleanup).
- **Live data**: ING-149 chunk titles realigned to verb-first + `#stage`.
- **No code, no new store**: `pack_schedule.py` unchanged (breaks + meetings are
  `fixed_commitments`); persistence stays config + TickTick. Packer + schema tests
  stay green.
- **Release**: `plugin.json` + marketplace + CHANGELOGs + `butler--v0.8.0`.
