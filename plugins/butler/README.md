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

1. **Day-at-a-time.** Build the whole tree once; only ever put times on the target day's chunks.
2. **Points are complexity, not time.** Never divide Linear story points into hours.
3. **Selective AI discount.** Discount AI-amenable build chunks; never discount ambiguous-spec resolution, cross-system debugging, decisions needing people, or reviewing AI output. Each AI-discounted build chunk is paired with a non-discounted verify chunk.
4. **Lean, human tasks.** Titles and descriptions follow a strict anti-slop contract (`references/task-contract.md`). AI-generated tasks carry the `ai` tag so they're filterable.
5. **State lives only in TickTick + Calendar.** No side files.

## Adoption

Everything user-specific lives in the config block at the top of each `SKILL.md`.
Edit that block (timezone, work window, project + tag names, capacity) to adopt.

## Setup

The skills create a few TickTick tags (`deep`, `shallow`, `comms`, `review`, `ai`,
`parked`) and expect a work list (default `Plate`) and a planning list (default
`Ops`). Resolve names → IDs at runtime; never hard-code IDs.
