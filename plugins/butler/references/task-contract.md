# Task writing contract

Generated tasks are read and acted on by **you**, the human. They must read as
lean and natural, never as AI filler. Verbose, dramatic, or trivially-granular
tasks are clutter that makes the tool feel worse than no tool. Every word that
isn't load-bearing is activation energy you have to pay to start.

These rules are a hard contract. The JSON shapes are pinned in
`schemas/parent-task.schema.json` and `schemas/chunk-task.schema.json`.

## Title contract

This contract applies to **every generated task, in every context** (work and
personal). The `<Stage label>:` prefix below is **work-only** — personal titles use
a lean imperative verb + object with NO stage prefix (e.g. "Book the dentist
appointment", "Order cat food", "Renew passport") and still obey every other rule
here: sentence case, no emoji, no trailing period, ≤70 chars, no slop.

Work form: **`<Stage label>: <short qualifier>`**

A chunk's title is its pipeline stage plus a short qualifier that disambiguates it
in a flat list. The qualifier names *what* within the stage, not *how* — the
concrete first action lives in the body (`Where:`), not the title.

- **Stage label** comes from the pipeline (`config.yaml`): Research, DB, Backend, Frontend, PR + AI review, Address PR comments, QA, Deploy. Use the human label, lightly.
- **Qualifier** is a real, specific thing: a symbol, endpoint, component, area. Not "changes", "stuff", "the system". e.g. `Backend: pricer API + carry-back`, `QA: both portals, empty + set`, `Research: reproduce 500 on POST /sessions`.
- A bare stage with no qualifier is allowed only when the ticket has exactly one chunk in that stage and the parent makes it unambiguous.
- **Length:** aim ≤ 50 characters, hard ceiling 70. If the qualifier won't fit, it's carrying body content — move it to `Where:`/`Done:`.
- **Casing:** sentence case in the qualifier. Not Title Case (itself an AI tell).
- **Punctuation:** no trailing period. No emoji, ever. No `[TICKET-123]` prefix — the id is metadata (the parent carries it). Preserve code identifiers verbatim (`NeighborhoodLocation`, `POST /sessions`).

Qualifier verbs, when one helps (pick the precise one): trace, reproduce, wire,
add, remove, rename, extract, refactor, migrate, backfill, review, address, deploy.

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

Stage is carried by the title prefix (`Backend: …`), not the body. Do NOT write
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

| Slop | Lean (stage: qualifier) |
|---|---|
| Dive deep into understanding the current field wiring to ensure a robust foundation | Research: trace NeighborhoodLocation reads |
| Seamlessly integrate and wire up the new analytics service to enhance tracking | Backend: analytics client in checkout submit |
| Address and resolve all the valuable feedback on the pull request comprehensively | Address PR comments: #482 |
| Perform thorough and meticulous QA to validate, verify, and confirm the feature | QA: signup on Safari iOS |
| Carefully orchestrate the deployment of the latest changes for a seamless rollout | Deploy: v2.3 to prod behind flag |
| Investigate and delve into the root cause of the intricate session bug | Research: reproduce 500 on POST /sessions |
| Leverage best practices to refactor and streamline the auth module for scalability | Backend: extract token refresh from useAuth() |

Sources behind this contract: Wikipedia "Signs of AI writing" (the overused-vocabulary
cluster, hedging, rule-of-three, em-dash tell); GTD next-action guidance (verb-first,
done-signal); Content Credentials / C2PA (provenance as attached metadata, not stamped
into content).
