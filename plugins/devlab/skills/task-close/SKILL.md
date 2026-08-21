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
    Accept: Issue Key (e.g. PRJ-12), task name search, or Notion URL.
    If ambiguous, show matches and ask user to pick.
  </step>

  <step name="check-children">
    Query Sub-issues relation for this task.

    If task.Level == "Epic":
      Filter children where Level == "Task" and Status not in [Done, Won't Do].
      If open children exist:
        Show them. Ask: "This Epic has N open Tasks:"
        [list them with Issue Key and Status]
        Options: (a) Close Epic only (leaves Tasks open), (b) Close all, (c) Cancel

    If task.Level == "Task":
      Filter children where Level == "Sub-task" and Status not in [Done, Won't Do].
      If open children exist:
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
      Fetch parent to determine its Level.
      Query all siblings (same Parent Issue).
      If ALL siblings are now Done or Won't Do:
        If parent.Level == "Epic":
          Ask: "All Tasks under Epic [parent Issue Key] ([parent name]) are complete. Close Epic too?"
        Else:
          Ask: "All sub-tasks of [parent Issue Key] are complete. Close parent too?"
        If yes: close the parent (Status: Done, End Date: today).
  </step>
</procedure>
