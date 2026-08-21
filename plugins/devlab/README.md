# DevLab

DevLab is a Claude Code and Codex plugin for task-centric project management backed by an independently authenticated Notion connector.

## Install surfaces

- Claude Code exposes the eight skills through the plugin's `/devlab:<skill>` namespace.
- Codex exposes the same installed skills through its native skill selector.

Available skills: `setup`, `sync`, `dashboard`, `brainstorm`, `task`, `task-pick`, `task-close`, and `task-transition`.

## Configuration

Each project owns `.devlab/config.yaml`:

```yaml
schema_version: 1
project_name: "Example Project"
notion:
  project_page: "project-page-id"
  product_spec: null
  tasks_db: "tasks-database-id"
  task_template: "task-template-id"
sync:
  sources:
    - AGENTS.md
    - CLAUDE.md
    - openspec/
    - docs/plans/
```

Setup includes only sources that exist. Existing legacy configuration is previewed and migrated only after confirmation; it is never deleted automatically.

## Safety and portability

DevLab maps provider-neutral search, fetch, query, create, and update capabilities to the active authenticated Notion connector. It fails closed when a required capability is unavailable, never substitutes web access, and never stores credentials. All Notion writes require user confirmation.

The canonical plugin metadata is `plugin.json`. Bonboncinnabon's portability generator owns the Claude manifest, Codex manifest, skill UI metadata, and marketplace projections.

Supported hosts are Claude Code and Codex on macOS and Linux. Windows and public marketplace submission are outside this release.
