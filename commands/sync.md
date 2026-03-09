---
description: Push repo state to Notion (dashboard + Product Spec)
---

You are syncing the current project's repo state to its Notion project page.

## Prerequisites

Read `.claude/devlab-notion.yaml` to get Notion page IDs. If the config doesn't exist, tell the user to run `/devlab:setup` first.

## Sync Process

### 1. Gather repo state

Read these sources to build a picture of the project's current state:
- `CLAUDE.md` — architecture, conventions, change plan, version
- `openspec/changes/archive/` — completed features (each directory = one shipped change)
- `docs/plans/` — implementation plans
- `package.json` or `tauri.conf.json` — current version
- `git log --oneline -20` — recent commits
- `git tag --sort=-creatordate | head -5` — recent releases

### 2. Build content for each Notion section

**Entry page (project_page):**
- **Overview paragraph** — synthesize from CLAUDE.md's architecture section + current version + what's been built recently
- **Roadmap table** — derive from CLAUDE.md's Change Plan. Map each item to Done/In Progress/Planned based on the plan and openspec archive (archived = Done)
- **Release & Distribution table** — version from package config, platforms, distribution method from CLAUDE.md
- **Last Updated property** — today's date

**Product Spec sub-page (product_spec):**
- **Key Features** — derive from CLAUDE.md architecture + openspec archive (each archived change = a shipped feature)
- **Vision and Scope** — from CLAUDE.md or existing Notion content (update only if repo has diverged)
- **Competitive Positioning** — leave unchanged unless user explicitly asks to update (this is editorial content)

### 3. Diff and confirm

Fetch the current Notion page content. Compare section by section against what you've built. Show the user a summary of what will change:
- Sections that will be updated (show old → new)
- Sections that are already in sync (skip)
- Sections that exist in Notion but not in repo sources (leave unchanged)

Ask for confirmation before pushing any changes.

### 4. Push to Notion

Use the Notion MCP `notion-update-page` tool to apply the changes. Update properties and content as confirmed.

Report what was updated and what was skipped.
