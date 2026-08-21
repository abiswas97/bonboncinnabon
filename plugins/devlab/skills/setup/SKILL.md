---
name: setup
description: Connect the current repository to its matching Notion project and persist a validated portable DevLab configuration.
---

# Set up DevLab

1. Read `../../domain/notion-capabilities.md` and require `search` and `fetch` from the authenticated Notion connector. Stop with its actionable compatibility error if either operation is unavailable.
2. If `.devlab/config.yaml` exists, validate its required fields and verify every referenced Notion object. Report drift; do not overwrite it automatically.
3. Read `reference/legacy-config.md`. If a legacy configuration is the only configuration present, run `scripts/migrate_config.py <legacy-file> .devlab/config.yaml` to produce a preview. Show the entire neutral configuration and ask for confirmation. Only after confirmation rerun with `--confirm`. Preserve the legacy file.
4. Otherwise search for the project by repository name, show ambiguous matches, and ask the user to choose.
5. Fetch the selected project, follow its Tasks relation to discover the shared Tasks database, and verify the properties in `../../domain/task.schema.json`. Never use a fixed database identifier.
6. Discover and verify the Task template and optional Product Spec page.
7. Show the complete proposed `.devlab/config.yaml`. After confirmation, create it with schema version 1 and only source paths that exist in the repository.

Repository source precedence is `AGENTS.md` for shared guidance, then `CLAUDE.md` for Claude-specific additions. Missing optional directories are ignored.
