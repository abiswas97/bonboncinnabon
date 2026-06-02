## Context

`plan` was calendar-blind (caused a duplicate + conflicts) and handled breaks
inconsistently. butler's tenet is **state lives in TickTick + Calendar** — no side
store — so persistence here is `config.yaml` + reading TickTick/Calendar at run time.
This change adds calendar sourcing, reserve-only flexible breaks, and (since config is
now growing and adopter-edited) a versioned config with migrate-on-read.

## Goals / Non-Goals

**Goals:** read meetings from a calendar (config-driven, with fallback); reserve
lunch + flexible decompress as constraints (never tasks); version the config + check
it on every read (migrate behind / error ahead); fold the 0.7.0 stage-in-title
cleanup; realign the live ING-149 chunks.

**Non-Goals:** no Notion / plugin-data store (config + TickTick only); no packer code
change (breaks + meetings are `fixed_commitments`); no burnout/accommodations logic
(that's 0.9.0).

## Decisions

### D1: Calendar source = GCal MCP + a config `calendar` block

`plan`/`reschedule` detect a Google Calendar MCP; if present, read the target day's
events from the calendars named in `config.yaml` `calendar:` (default: primary). The
source persists in config (not re-asked). No MCP → calendar-blind but stated, with a
suggestion to connect one; scattered calendars → suggest consolidating to one account.
Events become packer `fixed_commitments` — packer unchanged.

### D2: Breaks are reserve-only, flexible, never tasks

`config.yaml` `contexts.work.breaks` = `{ lunch_min: 45, decompress_min: 30 }`. `plan`
reserves lunch + one-or-more decompress breaks as `fixed_commitments` placed around
meetings; decompress count scales to focus load (e.g. one per ~2 deep blocks); a break
that would interrupt an in-progress block is deferred. Never materialized as tasks
(the "mixing responsibilities" correction). Adjustable/skippable per plan.

### D3: Versioned config + migrate-on-read (single shared check)

Add `schemas/config.schema.json` — a JSON Schema for `config.yaml` carrying an integer
`version` (the current config version). `config.yaml` carries `config_version`. A
single shared "config preflight" (documented once in `references/template.md` →
Config, referenced by every skill's Config step):
- read `config.yaml`; compare `config_version` to the schema's `version`.
- **equal** → proceed silently.
- **behind** → state it, ASK to migrate; on yes apply the schema's defaults for any new
  fields, bump `config_version`, proceed; on no, proceed with caveat or stop.
- **ahead** → ERROR ("config newer than plugin — shouldn't happen"), don't run.
Migration is additive (new fields get schema defaults); the agent does it by editing
`config.yaml`, then re-reads. Start `config_version: 1` (the 0.8.0 shape); a config
with no version field is treated as v0 → offered migration to v1.

*Why a single shared check:* DRY — the rule lives once; all four skills reference it,
same as the interview-presentation convention.

### D4: Persistence stays config + TickTick-derived

No Notion, no `${CLAUDE_PLUGIN_DATA}`. Calendar source + break defaults + prefs live in
`config.yaml`; any history (load, calibration) is derived from TickTick at read time
(0.9.0). Honors the "state in TickTick + Calendar" tenet.

### D5: Fold 0.7.0 cleanup + realign ING-149

Reconcile the leftover "stage in title prefix" / "Title = stage + short qualifier"
lines to verb-first + `#stage`. Realign the live ING-149 chunk titles.

## Risks / Trade-offs

- **[Preflight friction]** → silent when equal; only prompts on behind/ahead (rare).
- **[Migration correctness]** → additive-defaults only; never drops user values; re-read after migrate to confirm.
- **[Calendar MCP variability]** → read-only, per-config calendar list; degrade to calendar-blind, stated.
- **[Break flexibility vague]** → defaults in config; scale heuristic documented in heuristics.md; user adjusts per plan.

## Migration Plan

- Additive config (`config_version`, `calendar`, `breaks`) + new `config.schema.json`.
  Existing user configs (no `config_version`) → preflight offers migration to v1.
- No code change; packer + schema tests stay green; add config-schema validity to the
  test/validate pass.
- Release: bump `plugin.json` + marketplace (equal), CHANGELOGs, `claude plugin tag`
  → `butler--v0.8.0`, push. Then sync/archive.

## Open Questions

- Decompress-count heuristic exact thresholds (one per N blocks) — tune in heuristics; defaults are conservative.
