---
description: Debate-driven task creation linked to a Feature
argument-hint: '<feature-url-or-name>'
---

You are creating tasks for a Feature through interactive debate.

## Prerequisites

Read `.claude/devlab-notion.yaml` to get the Tasks DB and Features DB IDs. If the config doesn't exist, tell the user to run `/devlab:setup` first.

## Process

### 1. Find the Feature

If `$ARGUMENTS` is a Notion URL or ID, fetch it directly. Otherwise, search the Features DB for a matching feature name. If ambiguous, ask the user to pick.

### 2. Read the Feature

Fetch the Feature page content. Extract:
- Problem statement
- Proposed solution
- Scope (in/out)
- Key decisions
- Open questions

Also read `CLAUDE.md` and relevant `openspec/` or `docs/plans/` files for technical context.

### 3. Debate task breakdown

This is interactive. Walk through the feature with the user:
- "What's the smallest first task here?"
- "Is this really one task or should we split it?"
- "What depends on what? Can anything be parallelized?"
- "What's the acceptance criteria for each task?"

Push back on tasks that are too large (>2 days) or too vague. Ask clarifying questions.

One question at a time. Build the task list incrementally.

### 4. Create tasks

Once the user approves the task list, create each task in the Tasks DB via Notion MCP:
- Set the Feature relation to link back to the parent Feature
- Set status to "To Do"
- Set priority based on the discussion
- Write a concise description with acceptance criteria in the page body

### 5. Update Feature status

If the Feature was in "brainstormed" status, update it to "specced" now that tasks exist.

### 6. Confirm

Show the user a summary: how many tasks created, linked to which feature, with links.
