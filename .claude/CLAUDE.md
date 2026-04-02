# DevLab Plugin

Claude Code plugin for task-centric project management. Syncs Dev Lab repos with Notion.

## Architecture

```
commands/    -> User-invocable thin wrappers (/devlab:*)
skills/      -> Logic + templates + scripts (user-invocable: false)
agents/      -> Personas spawned by skills (proposer, critic, brainstormer)
```

- Commands invoke skills. Skills hold all procedure + reference knowledge.
- Only promote to a skill when supporting files (scripts, templates, reference docs) are needed.
- XML tags for logic gates and flow control in skill/agent content.

## Notion Integration

- Tasks DB is the single work unit. No Features DB.
- Sub-tasks: one level deep only. Always link Project relation.
- Story Points: number field (1, 2, 3, 5). Not select.
- Task Template has AI-guiding gray callouts under each section.
- Schema/template changes are manual (via Notion AI prompts), never programmatic.

## Commands

| Command | Purpose |
|---------|---------|
| `/devlab:setup` | Discover Notion IDs, write .claude/devlab-notion.yaml |
| `/devlab:sync` | Push repo state to Notion |
| `/devlab:dashboard` | ASCII terminal dashboard (default: project, `all` for cross-project) |
| `/devlab:brainstorm` | PM-style brainstorm, writes Task to Notion |
| `/devlab:task` | GAN debate: proposer + critic + user sprint planning |
| `/devlab:task-pick` | Suggest next task by priority/points |
| `/devlab:task-close` | Close task with sub-task cascade |
| `/devlab:task-transition` | Move task status with validation |

## Model Selection (for /devlab:task debate)

| Story Points | Model | Effort |
|---|---|---|
| 1 | sonnet | low |
| 2 | sonnet | medium |
| 3 | sonnet | high |
| 5 | opus | medium |

## Config

Per-project config lives at `.claude/devlab-notion.yaml`:

```yaml
project_name: <string>
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
