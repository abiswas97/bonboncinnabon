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
  <step name="parse-args">
    If $ARGUMENTS contains --epic <key>:
      Fetch the Epic page by Issue Key.
      If not found or Level != "Epic": STOP with error.
      Store epic_url for query filter.
    Otherwise: epic_filter = null.
  </step>

  <step name="query">
    Query Tasks DB via Notion MCP. Filter:
    - Project matches current project
    - Level != "Epic" (Epics are not pickable work items)
    - Status in ["Backlog", "To Do"]
    - Blocked By is empty (not blocked)
    - If epic_filter: Parent Issue == epic_url

    Sort results by:
    1. Priority: Urgent > High > Medium > Low
    2. Story Points: ascending (smallest unblocked first)
  </step>

  <step name="present">
    Show top 3 candidates in a table:

    ```
    NEXT UP (under PRJ-5: Epic Name)  <- only if --epic set
    ┌─────┬──────────────────────────┬──────┬──────┬──────────┐
    │  #  │ Task                     │ Level│ Pts  │ Priority │
    ├─────┼──────────────────────────┼──────┼──────┼──────────┤
    │  1  │ PRJ-15 Example task      │ Task │  2   │ High     │
    │  2  │ PRJ-16 Another task      │ Task │  3   │ Medium   │
    │  3  │ PRJ-18 Third task        │ Task │  1   │ Medium   │
    └─────┴──────────────────────────┴──────┴──────┴──────────┘
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
