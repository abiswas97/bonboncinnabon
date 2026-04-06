---
name: dashboard
description: >
  Terminal dashboard showing project health, velocity, and task status.
  Queries Notion databases and renders ASCII art via bundled Python script.
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash
---

# DevLab Dashboard

<prerequisites>
  <gate name="config">
    Read `.claude/devlab-notion.yaml`. Extract all IDs.
    If missing: STOP. Tell user to run `/devlab:setup`.
  </gate>

  <gate name="mode">
    If $ARGUMENTS contains "all" or "overview": mode = cross-project.
    Otherwise: mode = per-project (current repo).
  </gate>
</prerequisites>

<per-project-mode>
  <step name="query-tasks">
    Query Tasks DB via Notion MCP:
    - Filter: Project matches current project
    - Fetch all items (Tasks, Sub-tasks, and Epics). Group Epics separately.
    - Include: Task Name, Status, Story Points, Priority, Type, Level, Labels,
      Start Date, End Date, Created, Parent Issue, Sub-issues, Blocked By, Issue Key
  </step>

  <step name="query-project">
    Fetch the Dev Lab project page:
    - Extract: Key, Status, Resources, Courses, Papers and Notes, Videos
  </step>

  <step name="render">
    Construct a JSON object matching the shape in templates/project.md.
    Pipe it to the render script:

    ```bash
    echo '<json_data>' | python3 ${CLAUDE_SKILL_DIR}/scripts/render.py --mode project --name "<project_name>" --key "<project_key>"
    ```

    Present the script's stdout output to the user as-is (it is pre-formatted ASCII).
  </step>
</per-project-mode>

<cross-project-mode>
  <step name="query-all-projects">
    Query the Dev Lab DB via Notion MCP:
    - Fetch all projects with Status "In Progress"
    - For each project, query its tasks from Tasks DB
  </step>

  <step name="query-knowledge">
    Count totals across all projects:
    - Resources, Courses, Papers and Notes, Tech Stack Items
  </step>

  <step name="render">
    Construct a JSON object matching the shape in templates/overview.md.
    Pipe all data as JSON to the render script:

    ```bash
    echo '<json_data>' | python3 ${CLAUDE_SKILL_DIR}/scripts/render.py --mode overview
    ```

    Present stdout to the user.
  </step>
</cross-project-mode>
