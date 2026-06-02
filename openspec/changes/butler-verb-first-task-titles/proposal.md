## Why

butler work-chunk titles are `Stage: qualifier` (e.g. `QA: both portals, set + empty,
end to end`). The qualifier ends up cramming a test-matrix instead of naming the object
under test, so at a glance you cannot tell what the task is. Research across GTD,
bullet-journal rapid-logging, productivity forums (r/gtd, r/productivity, HN), and
ADHD/executive-function task-initiation converges on **verb-first, concrete-object**
titles. The causal anchor — McCrea, Liberman, Trope & Sherman 2008 (*Psychological
Science*) — shows a concrete (how/execution) construal makes people **start sooner**,
independent of the task's difficulty, importance, or attractiveness. That is exactly the
activation-energy / time-blindness problem butler exists to reduce.

## What Changes

- **Work chunk titles become verb-first next actions** (concrete physical verb + named
  object), replacing the `Stage: qualifier` prefix. **BREAKING** convention change:
  reverses the 0.6.0 "stage stays in the title prefix" decision.
- **Stage moves to a tag** (`#research`/`#db`/`#backend`/`#frontend`/`#review`/`#qa`/
  `#deploy`), a managed family like `#intensity`. The stage tag becomes the calibration
  grouping key (read from the tag, not parsed from the title) and the packer's stage
  input on read-back.
- **Parent work-units stay outcome-named** (nouns), explicitly NOT verb-first — the GTD
  project-vs-action naming split.
- **Verb guardrail**: free choice of verb, but it SHALL name a physical/visible action
  (no "think about", "look into", "deal with").
- **Don't hollow the title / keep the cue**: the object stays in the title and the one
  load-bearing when/where cue stays inline; only the test-matrix, conditions, AC, why,
  and links move to the body.
- **Personal titles** are already verb-first; the contract now states the rule uniformly
  (no context uses a `stage:` prefix).
- **One-time setup** gains the `stage` tag family.
- **0.7.0 release**: version bump + marketplace entry, both CHANGELOGs, tag, push.

## Capabilities

### New Capabilities

- `task-titles`: the contract for a generated task's TITLE — verb-first concrete-object
  next actions for chunks, outcome nouns for parents, the don't-hollow and keep-the-cue
  rules, and the rule that stage is carried as a tag rather than a title prefix.

### Modified Capabilities

- `task-contexts`: the anti-slop title requirement is updated so titles are verb-first
  across all contexts with no `stage:` prefix (work or personal), and stage is
  additionally carried as a managed tag that is the calibration grouping key.

## Impact

- **References**: `references/task-contract.md` (Title contract rewritten to verb-first
  chunks + outcome parents; before/after table updated; the `QA: both portals, empty +
  set` example removed; don't-hollow + keep-the-cue rules added), `references/heuristics.md`
  (Calibration reads the stage tag, not the title prefix; Decomposition "Title = stage +
  qualifier" → verb-first + stage tag; Time-blocking activity derived from the stage tag),
  `references/template.md` (chunk title mapping, tags gain the stage tag, one-time setup
  stage-tag family).
- **Config**: `config.yaml` — stage-tag family in one-time setup (the pipeline stage keys
  already exist as the decomposition menu; they now also seed the tags).
- **Schema**: `schemas/chunk-task.schema.json` — `stage` stays a field; its description
  notes it renders as a tag, not a title prefix; title-pattern guidance updated.
- **No code**: `pack_schedule.py` untouched (stage still arrives via packer-input); packer
  and schema tests stay green.
- **Live data**: the ING-165 QA chunk and the three LOS spike trees were already migrated
  by hand this session (verb-first titles + `#stage` tags) as the demo.
- **Release**: `plugin.json` + marketplace entry + both CHANGELOGs + `butler--v0.7.0`.
- **Compatibility**: existing old-style `Stage:` titles still parse on read; the stage tag
  is the calibration source going forward, with the title prefix as a read-only fallback
  for historical tasks.
