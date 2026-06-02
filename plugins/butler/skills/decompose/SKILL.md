---
name: decompose
description: Use when the user wants to break down, decompose, scope, or think through a task that ALREADY exists in TickTick — "break down this task", "decompose <task>", "scope the thing in Life", "help me think through <existing task>", or names/points at a captured task to split. Context-aware (work → pipeline stages, personal → free-form or none). For NEW work or a Linear ticket not yet in TickTick, use butler:intake instead.
---

# Decompose an existing task

Talk through breaking down a task that is **already in TickTick** into human,
session-sized chunks — interview-first and context-aware. The existing task becomes
the parent; this skill never creates a new top-level work unit (that is
`butler:intake`). Idempotent: re-running augments an already-split task, never
duplicates chunks.

## Config

Read `${CLAUDE_PLUGIN_ROOT}/config.yaml`. Resolve TickTick names → ids at runtime
(`list_projects` / `list_tags`). Load deferred MCP tools (TickTick; Google Calendar
only when placing a personal reminder) with tool_search.

## Core rules

1. **Interview is a HARD GATE.** Do NOT decompose or write anything until you have confirmed intent / prior progress / single-vs-multi-step (`${CLAUDE_PLUGIN_ROOT}/references/interview.md` → Hard gate). A skimmed interview is a defect.
2. **Existing task only.** Operate on a task already in TickTick. New work / a Linear ticket not yet captured → route to `butler:intake`.
3. **Context, derived then confirmed.** Derive the task's context from its project and confirm before decomposing (`${CLAUDE_PLUGIN_ROOT}/references/heuristics.md` → Contexts). Never silent.
4. **Default to NOT over-shredding.** Personal tasks are usually a single action — leave them whole unless genuinely multi-step. Augment, never duplicate, an already-split task.
5. **Lean, human tasks.** Follow `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md`. Tag every created task `ai`.
6. **Confirm before writing.**

## Red flags — do not proceed until cleared

STOP and resolve before creating or modifying ANY task:

- Haven't resolved + confirmed which exact task this is → confirm the match first.
- Haven't confirmed the context (work vs personal) → derive and ask.
- Haven't cleared the Hard gate (done-criteria / prior progress / multi-step vs single action) → a single action is not shredded.
- Task already has children and you're about to re-create them → augment the gaps only.

## Procedure

```
Conduct the interview per `references/interview.md` → Decompose (honor each question's
[choice]/[open] tag — see → Presentation). One thread at a time, never a wall of cards.

- [ ] 1. RESOLVE the task:
        - From args → search TickTick (search_task / filter_tasks), present the best
          match, and confirm it (interview.md → Decompose, "Resolve the task").
        - No task named → list undecomposed candidates (active tasks with no childIds)
          and let the user pick.
- [ ] 2. DERIVE + CONFIRM context from the task's project (heuristics → Contexts):
        Plate/Promo Track → work; Life/Photo/Finance/Relationships/Medical/Projects →
        personal; unmapped → ask. State it and confirm.
- [ ] 3. ALREADY SPLIT? Re-read the task (get_task_by_id) for childIds. If it has
        children, read them, talk through gaps, and ADD only what's missing — never
        duplicate an existing chunk.
- [ ] 4. HARD GATE — clear the interview (references/interview.md → Hard gate, then
        Decompose) before any decomposition. Do NOT decompose until intent / prior progress /
        single-vs-multi are confirmed.
- [ ] 5. DECOMPOSE per context:
        - work → pick stages from contexts.work.pipeline (heuristics → Decomposition
          (work)): 2–6 chunks, title = verb-first action + stage tag, context: work, stage default
          intensity + ai_discount (override per chunk), set est0 now.
        - personal → 2–4 free-form session steps (no stage/intensity/ai_discount; title
          per task-contract (verb-first, no stage tag); optional priority + light est0),
          OR conclude it's a single action and do NOT decompose — offer to schedule/cue
          it instead.
- [ ] 6. CONFIRM the proposed chunks (interview.md → Decompose, "Confirm, then write").
        On yes, the existing task becomes the PARENT
        (optionally tidy its title/content to parent form — confirm any rewrite). Create
        each chunk as a child (parentId set, kind TEXT, `ai` tag) per references/template.md.
        RE-READ the parent and assert childIds linked — the create response is stale.
        Leave chunks dateless; scheduling is butler:plan (work) / a light reminder (personal).
- [ ] 7. OFFER NEXT: butler:plan for work; set a light reminder (due time + reminder,
        time asked or derived from a live read of the day) for personal.
```

## References

- `${CLAUDE_PLUGIN_ROOT}/references/heuristics.md` — Contexts, Decomposition (work), Personal.
- `${CLAUDE_PLUGIN_ROOT}/references/interview.md` — Hard gate, Decompose.
- `${CLAUDE_PLUGIN_ROOT}/references/task-contract.md` — the lean task writing contract (all contexts).
- `${CLAUDE_PLUGIN_ROOT}/references/template.md` — task template + TickTick field mappings (work + personal).
- `${CLAUDE_PLUGIN_ROOT}/schemas/` — JSON Schema for tasks.

New work with no TickTick task yet → use `butler:intake`. Scheduling the day → `butler:plan`.
