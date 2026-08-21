---
name: task-close
description: Close a task while preventing terminal parents from retaining non-terminal descendants.
---

# Close a task

1. Validate `.devlab/config.yaml`. Require `search`, `fetch`, `query`, and `update` using `../../domain/notion-capabilities.md`.
2. Resolve the task by issue key, name, or URL; ask the user to choose if ambiguous.
3. Query every descendant. If any is non-terminal, offer only: recursively mark the listed descendants Done, or cancel. Parent-only closure is invalid.
4. Show every affected issue key, current status, target status, and End Date before asking for confirmation.
5. After confirmation, close descendants from leaves upward and close the parent last. Stop on the first connector failure and report completed and remaining updates.
6. If the selected item has a parent and all siblings are terminal, offer a separate confirmed closure of that parent.

Done and Won't Do are terminal. A parent cannot become terminal while any descendant is not terminal.
