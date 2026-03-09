---
description: PM-style brainstorm that outputs a Feature entry to Notion
argument-hint: '[topic]'
---

You are launching a brainstorming session for a new feature idea.

## Prerequisites

Read `.claude/devlab-notion.yaml` to get the Features DB ID. If the config doesn't exist or `features_db` is null, tell the user to run `/devlab:setup` first and ensure the Features DB is created.

## Process

Launch the `brainstormer` agent with the following context:

- **Topic**: `$ARGUMENTS` (if provided)
- **Project config**: contents of `.claude/devlab-notion.yaml`
- **Project context**: read `CLAUDE.md` for architecture and current state
- **Features DB ID**: from the config, for writing the output

The agent handles the full brainstorming conversation and writes the Feature to Notion when done.

Tell the user: "Starting a brainstorm session. I'll ask questions to refine the idea, then write a Feature entry to Notion when we're done."
