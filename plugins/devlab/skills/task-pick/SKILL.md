---
name: task-pick
description: Rank executable unblocked work and start the user-selected task through a confirmed Notion update.
---

# Pick the next task

1. Validate `.devlab/config.yaml`. Require `search`, `fetch`, `query`, and `update` using `../../domain/notion-capabilities.md`.
2. Resolve an optional Epic scope and reject it unless the record is an Epic.
3. Query Backlog and To Do records for the configured project. Exclude Epics and anything with an active blocker.
4. Rank by Urgent, High, Medium, Low priority, then by ascending Task story points. Sub-tasks may be shown as decomposition but do not alter parent ranking points.
5. Present the top three candidates and ask the user to choose.
6. Show the exact transition to In Progress and request confirmation. Set Start Date only if absent, then report the connector result.
