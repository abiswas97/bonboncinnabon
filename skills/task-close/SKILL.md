---
name: task-close
description: >
  Close a task, cascade to sub-tasks, and prompt to close parent if all siblings done.
user-invocable: false
---

# Close Task

<prerequisites>
  <gate name="config">
    Read `.claude/devlab-notion.yaml`. Extract tasks_db.
    If missing: STOP. Tell user to run `/devlab:setup`.
  </gate>
</prerequisites>

<procedure>
  <step name="identify">
    Find the task from $ARGUMENTS.
    Accept: Issue Key (e.g. FAM-12), task name search, or Notion URL.
    If ambiguous, show matches and ask user to pick.
  </step>

  <step name="check-subtasks">
    Query Sub-issues relation for this task.
    If open sub-tasks exist (Status not in [Done, Won't Do]):
      Show them in a list.
      Ask: "These sub-tasks are still open. Close them too, or just the parent?"
      Options: (a) Close all, (b) Just the parent, (c) Cancel
  </step>

  <step name="close">
    For each task being closed:
    - Set Status to "Done"
    - Set End Date to today

    Confirm what was closed.
  </step>

  <step name="cascade-parent">
    If this task has a Parent Issue:
      Query all sibling sub-tasks (same Parent Issue).
      If ALL siblings are now Done or Won't Do:
        Ask: "All sub-tasks of [parent Issue Key] are complete. Close parent too?"
        If yes: close the parent (Status: Done, End Date: today).
  </step>
</procedure>
