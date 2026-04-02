---
name: task-pick
description: >
  Suggest the next task to work on based on priority, blockers, and story points.
user-invocable: false
---

# Pick Next Task

<prerequisites>
  <gate name="config">
    Read `.claude/devlab-notion.yaml`. Extract tasks_db, project_page.
    If missing: STOP. Tell user to run `/devlab:setup`.
  </gate>
</prerequisites>

<procedure>
  <step name="query">
    Query Tasks DB via Notion MCP. Filter:
    - Project matches current project
    - Status in ["Backlog", "To Do"]
    - Blocked By is empty (not blocked)

    Sort results by:
    1. Priority: Urgent > High > Medium > Low
    2. Story Points: ascending (smallest unblocked first)
  </step>

  <step name="present">
    Show top 3 candidates in a table:

    ```
    NEXT UP
    ┌─────┬──────────────────────────┬──────┬──────────┐
    │  #  │ Task                     │ Pts  │ Priority │
    ├─────┼──────────────────────────┼──────┼──────────┤
    │  1  │ FAM-15 Settings persist  │  2   │ High     │
    │  2  │ FAM-16 Plugin loading    │  3   │ Medium   │
    │  3  │ FAM-18 Fix tooltip       │  1   │ Medium   │
    └─────┴──────────────────────────┴──────┴──────────┘
    ```

    Include any useful context: recently unblocked, sub-task count, labels.
  </step>

  <step name="pick">
    Ask: "Which one? (number, or describe what you'd rather work on)"

    When user picks:
    - Update Status to "In Progress" via Notion MCP
    - Set Start Date to today (if not already set)
    - Confirm: "Picked [Issue Key]: [name]. Status set to In Progress."
  </step>
</procedure>
