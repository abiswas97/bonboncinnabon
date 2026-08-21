---
description: Discover Notion page IDs for the current project and write .claude/devlab-notion.yaml
argument-hint: '[project-name]'
---

You are setting up the DevLab Notion integration for the current project.

<procedure>
  <step name="check-existing">
    Read `.claude/devlab-notion.yaml`. If it exists, show current config
    and ask: "Reconfigure, or keep existing?"
  </step>

  <step name="project-name">
    Determine project name from (in order):
    1. `$ARGUMENTS` if provided
    2. `CLAUDE.md` project name
    3. `package.json` name field
    4. Ask the user
  </step>

  <step name="search-notion">
    Use Notion MCP `notion-search` to find the project in the Dev Lab database.
    If multiple results, ask the user to pick.
  </step>

  <step name="discover-ids">
    Fetch the project page. Discover:
    - **project_page**: the page ID itself
    - **product_spec**: child page named "Product Spec" (null if not found)
    - **tasks_db**: `713f8ed9-13cd-4610-bcba-4dd80d83a67e` (verify via project's Tasks relation)
    - **task_template**: fetch the Tasks DB, find the template named "Task Template" in its templates list. Extract its page ID.
  </step>

  <step name="write-config">
    Write `.claude/devlab-notion.yaml`:

    ```yaml
    project_name: <name>
    notion:
      project_page: <uuid>
      product_spec: <uuid or null>
      tasks_db: 713f8ed9-13cd-4610-bcba-4dd80d83a67e
      task_template: <uuid>
    sync:
      sources:
        - CLAUDE.md
        - openspec/
        - docs/plans/
    ```
  </step>

  <step name="confirm">
    Show the written config. Note any null values and explain what the user
    needs to do in Notion to fix them.
  </step>
</procedure>
