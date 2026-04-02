---
description: PM-style brainstorm that outputs a Task entry to Notion
argument-hint: '[topic]'
---

You are launching a brainstorming session for a new feature idea.

<prerequisites>
  <gate name="config">
    Read `.claude/devlab-notion.yaml`. Extract tasks_db, project_page.
    If missing: STOP. Tell user to run `/devlab:setup`.
  </gate>
</prerequisites>

Launch the `brainstormer` agent with:
- **Topic**: $ARGUMENTS
- **Project config**: contents of `.claude/devlab-notion.yaml`
- **Project context**: read `CLAUDE.md` for architecture and current state
- **Tasks DB ID**: from config (for writing output)

Tell the user: "Starting a brainstorm session. I'll ask questions to refine
the idea, then write a Task entry to Notion when we're done."
