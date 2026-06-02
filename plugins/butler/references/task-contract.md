# Task writing contract

Generated tasks are read and acted on by **you**, the human. They must read as
lean and natural, never as AI filler. Verbose, dramatic, or trivially-granular
tasks are clutter that makes the tool feel worse than no tool. Every word that
isn't load-bearing is activation energy you have to pay to start.

These rules are a hard contract. The JSON shapes are pinned in
`schemas/parent-task.schema.json` and `schemas/chunk-task.schema.json`.

## Title contract

This contract applies to **every generated task, in every context** (work and
personal). Two shapes, by the task's role:

- **Chunks (next actions) — verb-first.** A chunk title opens with a concrete,
  physical-action verb and names the object it acts on: "Verify checkout
  end to end on both forms", "Wire signup to the welcome-email flow". The
  verb is free choice, but it must name a *visible* action — never "think about",
  "look into", or "deal with" (they fail the done-test). No `Stage:` prefix; the stage
  rides a tag (`#backend`, `#qa` — see `template.md`).
- **Parents (work units) — outcome nouns.** A parent is an outcome, not an action, so
  it takes a noun/outcome title ("Rules-to-checklist mapping (spike)", "Draft
  Application Invite (V1)"), NOT a forced verb. This is the GTD project-vs-action split.

Every title, both shapes, obeys: sentence case, no emoji, no trailing period, ≤70
chars (aim ≤50), no slop, code identifiers verbatim (`UserProfile`,
`POST /sessions`), no `[TICKET-123]` prefix (the id is metadata on the parent).

**Name the object; don't hollow the title.** The title keeps the object and the one
disambiguating when/where cue you need to act ("on both forms", "on dev"). A bare
verb or bare stage ("Verify", "QA") re-creates the vague-item paralysis the verb is
meant to cure. Everything else — the test-matrix, conditions, acceptance criteria,
why, links — lives in the body or in subtasks, never crammed into the title.

Verbs that tend to fit (pick the precise one, not a fixed list): verify, trace,
reproduce, wire, add, remove, rename, extract, refactor, migrate, backfill, decide,
design, define, review, address, merge, deploy.

## Description contract

The description is a **launchpad, not a spec** — the one thing that gets you moving
plus a link to where the detail lives. The system of record (Linear) holds the full
context and acceptance criteria; never copy them here. Markdown renders in TickTick.

A chunk description, omitting any line that doesn't apply:

```
<first physical action — imperative, 1–2 lines; `inline code` for files/symbols/endpoints>
Done when <one observable signal>.

~<minutes>m · [<TICKET> ↗](<linear-url>)
```

- **First action** — the concrete thing you'd touch first (the startability win). Prose, no `Where:` label; keep code identifiers verbatim in `` `inline code` ``.
- **`Done when …`** — a SINGLE observable signal, no `Done:` heading. Omit it when the title already implies success. More than one signal → split into subtasks (`butler:decompose`), never a `- [ ]` checklist in the description.
- **`~<n>m`** — the estimate, and the immutable calibration anchor (set once at intake, never overwritten). Replaces the old `est0:` label.
- **Link** — `[<TICKET> ↗](url)` to the source ticket; detail/AC live there. Personal chunks (no ticket) omit the link.

Stage is carried by a stage tag (`#backend`), not the title or the body. Do NOT write
`stage` or `ai_discount` into the description. Parent work units use the metadata
header instead (see `template.md`).

Exclude: `Why:`/`Where:`/`Ref:` labels, narrative intros, restating the title,
step-by-step how-to, background essays, hedging, copied acceptance criteria, anything
beyond ~3 lines + the footer.

## Slop blacklist (never use, in titles or descriptions)

- **Puffery verbs:** leverage, streamline, delve, dive deep, unlock, empower, facilitate, utilize, harness, spearhead, orchestrate, enhance, optimize (unless it is literally a perf task), showcase, foster, elevate.
- **Padding adjectives:** robust, seamless, comprehensive, holistic, scalable, cutting-edge, powerful, rich, intricate, meticulous, crucial, pivotal, vital, essential, key, proper, solid, clean (filler), thorough (filler), foundational.
- **Hedging / preamble:** it's worth noting, it's important to, keep in mind, simply, just, basically, essentially, make sure to, be sure to, don't forget to, in order to (use "to").
- **Inflation nouns:** foundation, groundwork, alignment, synergy, ecosystem, landscape, journey, deep dive, source of truth (unless it is the literal artifact name).
- **Structural tells:** rule-of-three ("verify, validate, and confirm" → one verb), "not just X but Y", em-dashes for drama, gerund-stack titles, fake urgency (critical/ASAP unless objectively true).

## AI-generated marker

Every butler-created task carries the **`ai` tag**. Rationale: a tag is a
first-class filterable dimension (build one "hide #ai" filter and forget it),
renders as a small chip outside the title, and costs zero title width. Provenance
belongs in metadata, not stamped into the visible title. Do NOT mark with a title
prefix or emoji.

## Before / after

| Slop | Lean (verb-first; stage = tag) |
|---|---|
| Dive deep into understanding the current field wiring to ensure a robust foundation | Trace UserProfile reads · `#research` |
| Seamlessly integrate and wire up the new analytics service to enhance tracking | Wire the analytics client into checkout submit · `#backend` |
| Address and resolve all the valuable feedback on the pull request comprehensively | Address PR 482 review comments · `#address-comments` |
| Perform thorough and meticulous QA to validate, verify, and confirm the feature | Verify signup on Safari iOS · `#qa` |
| Carefully orchestrate the deployment of the latest changes for a seamless rollout | Deploy v2.3 to prod behind the flag · `#deploy` |
| Investigate and delve into the root cause of the intricate session bug | Reproduce the 500 on POST /sessions · `#research` |
| Leverage best practices to refactor and streamline the auth module for scalability | Extract token refresh from useAuth() · `#backend` |

Sources behind this contract: Wikipedia "Signs of AI writing" (the overused-vocabulary
cluster, hedging, rule-of-three, em-dash tell); GTD next-action guidance (verb-first,
done-signal); Content Credentials / C2PA (provenance as attached metadata, not stamped
into content).
