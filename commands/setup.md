---
description: Discover Notion page IDs for the current project and write .claude/devlab-notion.yaml
argument-hint: '[project-name]'
---

You are setting up the DevLab Notion integration for the current project.

## Steps

1. **Read existing config** — check if `.claude/devlab-notion.yaml` already exists. If so, show the current config and ask if the user wants to reconfigure.

2. **Determine project name** — use `$ARGUMENTS` if provided, otherwise read the project name from `CLAUDE.md` or `package.json`, or ask the user.

3. **Search Notion** — use the Notion MCP `notion-search` tool to find the project in the Dev Lab database. Search for the project name. If multiple results, ask the user to pick.

4. **Discover page IDs** — fetch the project page to find:
   - The project page ID itself
   - The Product Spec sub-page ID (look for a child page named "Product Spec")
   - The Tasks database ID (look for a relation property or a linked database view)

5. **Find Features DB** — the Features DB already exists at `collection://956f9882-1327-42c3-8104-35fef255ae2b`. Verify it by fetching its schema. If for some reason it's missing, tell the user it needs to be created in Notion with a relation to Dev Lab + Tasks.

6. **Find Tasks DB** — the central Tasks DB is at `collection://713f8ed9-13cd-4610-bcba-4dd80d83a67e`. Verify via the project's Tasks relation property.

7. **Write config** — write `.claude/devlab-notion.yaml` with the discovered IDs:

```yaml
project_name: <name>
notion:
  project_page: <id>
  product_spec: <id or null>
  features_db: 956f9882-1327-42c3-8104-35fef255ae2b
  tasks_db: 713f8ed9-13cd-4610-bcba-4dd80d83a67e
sync:
  sources:
    - CLAUDE.md
    - openspec/
    - docs/plans/
```

7. **Confirm** — show the written config and confirm success. If any IDs couldn't be found, note them as null and explain what the user needs to do.
