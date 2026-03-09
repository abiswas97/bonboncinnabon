---
description: Quick view of roadmap, features, and tasks from Notion
---

You are showing the current project status from Notion. This is read-only — no writes.

## Prerequisites

Read `.claude/devlab-notion.yaml` to get Notion page IDs. If the config doesn't exist, tell the user to run `/devlab:setup` first.

## Display

### 1. Fetch project page

Fetch the project page from Notion. Extract and display:
- **Current version** from the Release & Distribution table
- **Roadmap summary** — count of Done/In Progress/Planned items

### 2. Fetch active features

If `features_db` is set, query the Features DB filtered by this project. Display a compact list:

```
Features:
  [in-progress] Pomodoro timer with cat reactions (P1)
  [brainstormed] Break & hydration nudger (P2)
  [idea] Mood system (P3)
```

### 3. Fetch open tasks

Query the Tasks DB filtered by this project, status not "Done". Display a compact list:

```
Open Tasks (5):
  [in-progress] Set up Pomodoro timer UI scaffold
  [to-do] Add timer state to Redux store
  [to-do] Design cat reaction animations
  ...
```

### 4. Format

Keep it concise — this is meant for a quick terminal glance, not a detailed report. Use markdown formatting for readability.
