# devlab

A Claude Code plugin for task-centric project management. Syncs Dev Lab repos with Notion.

## Commands

| Command | Purpose |
|---------|---------|
| `/devlab:setup` | Discover Notion IDs, write `.claude/devlab-notion.yaml` |
| `/devlab:sync` | Push repo state to Notion |
| `/devlab:dashboard` | Terminal dashboard (default: project, `all` for cross-project) |
| `/devlab:brainstorm [topic]` | PM-style brainstorm, outputs a Task or Epic to Notion |
| `/devlab:task [topic] [--epic <key>]` | Debate-driven task creation with proposer + critic agents |
| `/devlab:task-pick [--epic <key>]` | Suggest next task by priority and story points |
| `/devlab:task-close <key>` | Close task with sub-task cascade |
| `/devlab:task-transition <key> <status>` | Move task status with validation |

## Setup

1. Install the plugin in Claude Code
2. Ensure the [Notion plugin](https://github.com/anthropics/claude-plugins/tree/main/Notion) is installed and authenticated
3. Navigate to a project repo with a corresponding Dev Lab page in Notion
4. Run `/devlab:setup` to discover and save Notion page IDs

## Per-Project Config

Lives at `.claude/devlab-notion.yaml` in each repo:

```yaml
project_name: Example Project
notion:
  project_page: <uuid>
  product_spec: <uuid or null>
  tasks_db: <uuid>
  task_template: <uuid>
sync:
  sources:
    - CLAUDE.md
    - openspec/
    - docs/plans/
```

## Task Hierarchy

```
Epic (container)
  Task (deliverable, default)
    Sub-task (leaf, one level deep)
```

- **Epic**: strategic container grouping related Tasks. Not directly workable.
- **Task**: deliverable work item. Can be standalone or nested under an Epic.
- **Sub-task**: granular step under a Task. Must have a Parent Issue.

Use `--epic <key>` with `/devlab:task` and `/devlab:task-pick` to scope to an Epic.

## Architecture

```
commands/    -> User-invocable thin wrappers (/devlab:*)
skills/      -> Logic + templates + scripts
agents/      -> Personas spawned by skills (proposer, critic, brainstormer)
```
