---
name: dashboard
description: Query validated Notion task data and render deterministic project or cross-project terminal dashboards.
---

# DevLab dashboard

1. Validate `.devlab/config.yaml`. Read `../../domain/notion-capabilities.md` and require `fetch` and `query`.
2. Determine whether the user wants the current project or the active-project overview.
3. Query all relevant task fields, including hierarchy, points, status, dates, blockers, issue key, and project relation. Fetch project metadata needed by the chosen mode.
4. Construct one JSON document matching `../../domain/renderer.schema.json`. Include `mode`, `project_name`, `key`, tasks or projects, and an optional timezone-aware `as_of` timestamp for deterministic output.
5. Pass that document directly to `scripts/render.py` through standard input. Do not construct shell source from JSON or user text.
6. If validation fails, report stderr unchanged. Otherwise present the renderer output as preformatted text.

Only Task-level points contribute to planning and velocity. Sub-task points are displayed as decomposition and never added to the Task again.
