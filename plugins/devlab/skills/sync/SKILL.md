---
name: sync
description: Compare repository state with Notion project documentation and apply only confirmed section-level updates.
---

# Sync DevLab

1. Validate `.devlab/config.yaml`. Read `../../domain/notion-capabilities.md` and require `fetch` and `update`.
2. Read configured sources that currently exist. `AGENTS.md` is authoritative shared guidance; `CLAUDE.md` adds host-specific context without overriding it. Also use package versions, recent commits, and release tags when present.
3. Fetch the project page and optional Product Spec. Preserve editorial sections: Mission Statement, Core Problem, Competitive Positioning, Original Ideation, and Use-cases unless the user explicitly includes them.
4. Build a section-level diff. Show old and new content for every changed section, list sections already synchronized, and list Notion-only sections that will remain unchanged.
5. Ask for confirmation immediately before updating. If declined, make no writes.
6. Apply only the approved section updates and report connector results.

Roadmap data comes from shared repository guidance and archived changes. Feature synchronization is additive: never delete a Notion feature merely because a configured source omits it.
