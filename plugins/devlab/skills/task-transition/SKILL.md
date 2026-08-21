---
name: task-transition
description: >
  Move a task to a new status with validation and automatic date management.
user-invocable: false
---

# Transition Task Status

<prerequisites>
  <gate name="config">
    Read `.claude/devlab-notion.yaml`. Extract tasks_db.
    If missing: STOP. Tell user to run `/devlab:setup`.
  </gate>
</prerequisites>

<procedure>
  <step name="identify">
    Parse $ARGUMENTS for: task identifier + target status.
    Example inputs: "PRJ-12 in-review", "Fix tooltip blocked", "PRJ-9 done"
    Find the task via Issue Key, name search, or URL.
  </step>

  <step name="validate">
    Show current status and valid transitions:

    ```
    Backlog -> To Do -> In Progress -> In Review -> Done
                           |                        |
                           +-> Blocked               +-> Won't Do
    ```

    <validation-rules>
      <rule>Backlog -> Done: warn "Skipping all intermediate states. Confirm?"</rule>
      <rule>Done -> any: warn "Reopening a closed task. Confirm?"</rule>
      <rule>Won't Do -> any: warn "Reopening a canceled task. Confirm?"</rule>
      <rule>Any -> Blocked: prompt for Blocked By relation</rule>
    </validation-rules>

    If transition is unusual, ask for confirmation. Normal transitions proceed.
  </step>

  <step name="apply">
    Update Status via Notion MCP.

    <side-effects>
      <effect when="target is In Progress AND Start Date is empty">
        Set Start Date to today.
      </effect>
      <effect when="target is Done OR target is Won't Do">
        Set End Date to today.
      </effect>
      <effect when="target is Blocked">
        Ask: "Blocked by which task?" Search Tasks DB for the blocker.
        Set Blocked By relation.
      </effect>
    </side-effects>

    Confirm: "[Issue Key] transitioned from [old] to [new]."
  </step>
</procedure>
