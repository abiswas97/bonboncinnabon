# devlab

A Claude Code plugin that bridges Dev Lab project repos with their Notion project pages.

## What it does

- **`/devlab:setup`** — Discover Notion page IDs for the current project and write config
- **`/devlab:sync`** — Push repo state (roadmap, version, features) to Notion
- **`/devlab:brainstorm [topic]`** — PM-style brainstorming that outputs a Feature entry to Notion
- **`/devlab:feature-task <feature>`** — Debate-driven task creation linked to a Feature
- **`/devlab:status`** — Quick terminal view of roadmap, features, and tasks from Notion

## Setup

1. Install the plugin in Claude Code
2. Ensure the [Notion plugin](https://github.com/anthropics/claude-plugins/tree/main/Notion) is installed and authenticated
3. Navigate to a project repo that has a corresponding Dev Lab page in Notion
4. Run `/devlab:setup` to discover and save Notion page IDs

## Per-Project Config

Lives at `.claude/devlab-notion.yaml` in each repo:

```yaml
project_name: Familiar
notion:
  project_page: 3154a243-be05-8085-a184-e50b2089c83e
  product_spec: 05e405de-650c-4609-8e6c-2fafe9d62c04
  features_db: 956f9882-1327-42c3-8104-35fef255ae2b
  tasks_db: 713f8ed9-13cd-4610-bcba-4dd80d83a67e
sync:
  sources:
    - CLAUDE.md
    - openspec/
    - docs/plans/
```

## Features Database

Central Features DB tracks feature ideas across all Dev Lab projects:

| Property | Type |
|---|---|
| Feature Name | Title |
| Status | Idea → Brainstormed → Specced → In Progress → Shipped / Parked |
| Project | Relation → Dev Lab |
| Tasks | Relation → Tasks DB (1:many) |
| Priority | P0–P3 |
| Area | Core, UX, Infrastructure, Performance, Growth, Integration, DX |
| Effort | XS, S, M, L, XL |
| Feature Key | Formula (e.g. FAM-1) |

## Brainstormer Agent

The `/devlab:brainstorm` command launches a PM-style brainstorming agent that:
1. Asks structured questions (problem, user impact, simplest version, alternatives, risks, success criteria)
2. Adapts to the conversation — one question at a time, multiple-choice when possible
3. Synthesizes the discussion into a Feature page in Notion with status "Brainstormed"
