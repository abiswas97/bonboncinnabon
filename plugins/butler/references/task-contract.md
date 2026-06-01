# Task writing contract

Generated tasks are read and acted on by **you**, the human. They must read as
lean and natural, never as AI filler. Verbose, dramatic, or trivially-granular
tasks are clutter that makes the tool feel worse than no tool. Every word that
isn't load-bearing is activation energy you have to pay to start.

These rules are a hard contract. The JSON shapes are pinned in
`schemas/parent-task.schema.json` and `schemas/chunk-task.schema.json`.

## Title contract

Form: **`<imperative verb> <concrete object> [<done-signal / scope>]`**

- Start with ONE bare imperative verb. No gerund ("Investigating…"), no "should", no subject.
- The object is a real, specific thing: a symbol, file, component, endpoint, PR, ticket. Not "the code", "the system", "things".
- Optional single trailing clause for scope or done-signal: `…until tests pass`, `…in checkout flow`, `…behind a flag`.
- **Length:** aim ≤ 50 characters, hard ceiling 70. If it won't fit, the title is carrying description content — move it.
- **Casing:** sentence case. Capitalize the first word and proper nouns/identifiers only. Not Title Case (Title Case is itself an AI tell).
- **Punctuation:** no trailing period. No emoji, ever. No `[TICKET-123]` prefix — the id is metadata, not title text. Preserve code identifiers verbatim (`NeighborhoodLocation`, `POST /sessions`).

Approved verbs (pick the precise one): Trace, Wire, Add, Remove, Fix, Rename,
Extract, Move, Split, Merge, Review, Groom, Triage, Reproduce, QA, Deploy,
Revert, Bump, Profile, Cache, Log, Gate, Audit, Migrate, Backfill, Address,
Answer, Draft, Spike.

## Description contract

The description is a **tight key:value block, not prose.** A person scanning for
the one fact that unblocks action shouldn't have to read a paragraph. Fixed key
order means the eye always lands in the same place. Prose is where slop breeds,
so it is forbidden.

Allowed keys, fixed order, omit any that don't apply (never write `Notes: N/A`):

```
Why: <one clause, only if not obvious from the title>
Where: <file / symbol / endpoint; one per line>
Done: <one observable acceptance signal>
Ref: <PR / issue / ticket URL or id>
```

Parent work units use the metadata block instead (see `template.md`). The chunk
calibration line (`est0`) is appended per `template.md`.

Exclude from descriptions: narrative intros, restating the title, step-by-step
how-to, background essays, hedging, anything over ~5 lines. Deeper context lives
in the linked artifact via `Ref`, not pasted here.

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

| Slop | Lean |
|---|---|
| Dive deep into understanding the current field wiring to ensure a robust foundation | Trace where NeighborhoodLocation is read on the form |
| Seamlessly integrate and wire up the new analytics service to enhance tracking | Wire analytics client into checkout submit |
| Address and resolve all the valuable feedback on the pull request comprehensively | Address PR #482 review comments |
| Perform thorough and meticulous QA to validate, verify, and confirm the feature | QA signup flow on Safari iOS |
| Carefully orchestrate the deployment of the latest changes for a seamless rollout | Deploy v2.3 to prod behind flag |
| Investigate and delve into the root cause of the intricate session bug | Reproduce 500 on POST /sessions with empty body |
| Leverage best practices to refactor and streamline the auth module for scalability | Extract token refresh out of useAuth() |

Sources behind this contract: Wikipedia "Signs of AI writing" (the overused-vocabulary
cluster, hedging, rule-of-three, em-dash tell); GTD next-action guidance (verb-first,
done-signal); Content Credentials / C2PA (provenance as attached metadata, not stamped
into content).
