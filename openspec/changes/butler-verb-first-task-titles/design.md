## Context

butler renders a work chunk's title as `Stage: qualifier` (`Backend: pricer API`,
`QA: both portals, set + empty`). The stage prefix did double duty: it labeled the
pipeline stage AND served as the calibration reference class (heuristics parse the stage
back out of the title to group estimate-vs-actual drift). In practice the qualifier slot
collects a comma-separated test-matrix instead of the object under test, producing titles
that are unreadable at a glance — the trigger for this change was `QA: both portals, set +
empty, end to end`, where the actual subject (Neighborhood Location) is missing.

0.6.0 (`butler-lean-task-descriptions`) deliberately kept "stage in the title prefix" so it
would survive the footer cleanup. This change reverses that, having validated verb-first
through research rather than taste.

## Goals / Non-Goals

**Goals:**
- Chunk titles read as concrete verb-first next actions that name the object.
- Preserve stage as a first-class, machine-readable axis (calibration, packer ordering)
  by moving it from the title prefix to a tag.
- Keep parent titles as outcome nouns (they are projects, not actions).
- Change references + config + schema only — no packer code change, tests stay green.

**Non-Goals:**
- Changing the pipeline stage menu, the intensity tags, or the priority tags.
- Re-deriving estimates or touching the `~Nm` calibration anchor (immutable, from 0.6.0).
- Bulk-migrating historical TickTick tasks (the demo tasks were migrated by hand; old
  titles remain readable as a fallback).

## Decisions

- **D1 — Verb-first chunks, free but concrete verb.** Chunk titles open with a physical,
  visible verb naming the object. The verb is free choice (GTD forums favor any concrete
  verb over a closed list) but excludes non-actionable verbs ("think about", "look into",
  "deal with") that fail the done-test. Evidence: GTD next-action rule; Todoist/Asana
  "start with an action word"; McCrea et al. 2008 (concrete construal → earlier
  initiation, causal). Free verb chosen over a curated list per the user and GTD-forum
  consensus.
- **D2 — Parents are outcome nouns, not verb-first.** GTD splits action naming (verb-first)
  from project/outcome naming (noun: "Report submitted"). A parent work-unit is an
  outcome, so it keeps a noun/outcome title (`Rules-to-checklist mapping (spike)`), while
  its chunks are verb-first. This is the one carve-out from a blanket verb-first rule.
- **D3 — Stage becomes a tag, like intensity.** Removing the prefix would orphan the
  calibration reference class and the packer's stage ordering. So stage is rendered as a
  managed tag family (`#research…#deploy`), parallel to `#intensity` (deep/shallow).
  Calibration groups by the stage tag; the packer still receives stage via packer-input at
  plan time (unchanged), and reads the tag — not the title — when grouping completed work.
  This is more consistent with the existing design (everything else — `ai`, intensity,
  priority — is already a tag).
- **D4 — Don't hollow the title; keep the load-bearing cue.** The object must stay in the
  title (a bare "Verify" or "QA" re-creates the vague-item paralysis). The single
  disambiguating when/where cue stays inline (implementation-intention research: the
  trigger aids initiation); only the elaboration — test-matrix, conditions, AC, why,
  links — moves to the body or subtasks.
- **D5 — Tag-write fragility is tolerated.** The TickTick tag-write endpoint is
  undocumented and can 500 (already noted in template.md). A stage tag attaches as a label
  on first use even if `create_tag` fails, so the convention degrades gracefully; setup
  tries to create the colored sidebar tags but never blocks on it.

## Risks / Trade-offs

- **Flat-list grouping weakens.** Without the `Stage:` prefix, a flat title list no longer
  visually clusters by stage. Mitigation: the stage tag renders as a chip and is
  filterable; grouping moves from title-string to tag, which is stronger, not weaker.
- **Two stage sources during transition.** Historical tasks carry stage in the title;
  new tasks carry it in the tag. Calibration reads the tag first and falls back to
  title-prefix parsing for legacy tasks — accepted, and self-healing as old tasks age out.
- **Reversal cost.** This undoes a 0.6.0 decision one release later. Accepted: 0.6.0 kept
  the prefix on convenience grounds; this change is evidence-backed and the prefix was the
  source of the unreadable titles.
