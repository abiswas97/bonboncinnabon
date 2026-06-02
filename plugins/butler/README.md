# butler

A personal work planner for Claude Code. It turns a unit of work into human,
session-sized chunks and time-boxes **one day at a time** in TickTick, scheduling
around fixed commitments read from Google Calendar. Built for executive-function
support: a durable plan you build once, a small committed day (today *or*
tomorrow) you can actually start.

Part of the `bonboncinnabon` marketplace. Namespace: `butler:`.

## Skills

| Skill | Use it to |
|---|---|
| `butler:intake` | Turn a Linear ticket (explicit ID) or described work into a durable task tree. Idempotent: re-running on the same ticket resumes, never duplicates. |
| `butler:plan` | Reconcile open work and time-box a **target day** — today when run in the morning, tomorrow when run in the evening. |
| `butler:reschedule` | Recompute the rest of *today* from now when things slip. |

## How it's wired

- **TickTick** is the single source of truth (task tree, completion, focus history).
- **Google Calendar** is read-only — supplies fixed commitments.
- **Linear** is read-only and touched *only* when you name an explicit ticket ID.
- **`scripts/pack_schedule.py`** does deterministic block placement (stdlib Python).
- **`schemas/`** pins the task + packer contracts as JSON Schema.

## Design principles

1. **Stage-based, hybrid decomposition.** Chunks are stages from a config-defined `pipeline` (research → db → backend → frontend → review → address-comments → qa → deploy). Intake picks the applicable ones (skip the rest), titles each as a verb-first next action with the stage on a `#stage` tag, and may add ad-hoc chunks. A predictable template removes the "what are my chunks?" decision.
2. **Day-at-a-time.** Build the whole tree once; only ever put times on the target day's chunks.
3. **Points are complexity, not time.** Never divide Linear story points into hours.
4. **Selective AI discount.** Discount AI-amenable build stages; never discount ambiguous-spec resolution, cross-system debugging, decisions needing people, or reviewing AI output. Verification is its own `review` stage (submit PR + AI-assisted review), included whenever there are discounted build stages.
5. **Lean, human tasks.** Titles and descriptions follow a strict anti-slop contract (`references/task-contract.md`). AI-generated tasks carry the `ai` tag so they're filterable.
6. **State lives only in TickTick + Calendar.** No side files.

## Adoption

Run **`/butler:setup`** — it interviews you and writes your config to
`${CLAUDE_PLUGIN_DATA}/config.yaml`: a global, machine-wide file (the same in every
project) that persists across plugin updates and is never committed. It holds
everything user-specific: timezone, work window, project + tag names, capacity, the
`pipeline`, breaks, and pacing. The repo ships `config.example.yaml` as the generic
template; re-run `/butler:setup` anytime to update individual fields.

## Setup

`/butler:setup` resolves your TickTick lists and writes the config. The skills use a
few TickTick tags — `deep`/`shallow` (intensity), the `#stage` family
(research…deploy), `ai`, `parked` — and expect a work list (default `Work`) and a
planning list (default `Planning`). Stage rides a `#stage` tag; activity
(build/verify/comms/admin) is derived from it — neither is hand-set. Resolve names →
IDs at runtime; never hard-code IDs.
