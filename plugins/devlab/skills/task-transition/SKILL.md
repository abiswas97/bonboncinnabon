---
name: task-transition
description: Validate a task status transition and apply its date and blocker side effects after any required confirmation.
---

# Transition a task

1. Validate `.devlab/config.yaml`. Require `search`, `fetch`, and `update` using `../../domain/notion-capabilities.md`.
2. Resolve the task and target status. Read the canonical table at `../../domain/transitions.json`.
3. Reject any target absent from both the source state's `normal` and `confirmation` arrays. Ask for confirmation only when the target is in `confirmation`.
4. Entering Blocked requires a valid blocker relation selected through connector search. Leaving Blocked clears the active blocker relation.
5. First entry into In Progress sets Start Date if absent. Entry into Done or Won't Do sets End Date. Reopening clears End Date.
6. Before setting a parent to a terminal status, query all descendants and reject the transition if any is non-terminal.
7. Apply the complete property update as one connector operation and report the result.
