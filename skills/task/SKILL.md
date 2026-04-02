---
name: task
description: >
  GAN debate-driven task creation with sub-task scoping.
  Orchestrates proposer and critic agents in a sprint planning ceremony.
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash, Agent
---

# Task Creation: Sprint Planning Debate

<prerequisites>
  <gate name="config">
    Read `.claude/devlab-notion.yaml`.
    If missing: STOP. Tell user to run `/devlab:setup` first.
    Extract: tasks_db, task_template, project_page, project_name.
  </gate>

  <gate name="context">
    Read `CLAUDE.md` for architecture and current state.
    Run `git log --oneline -10` for recent activity.
  </gate>

  <gate name="existing-tasks">
    Query the Tasks DB via Notion MCP filtered by current project.
    Fetch tasks with Status not in [Done, Won't Do].
    This prevents duplicate work and informs the debate.
  </gate>

  <gate name="topic">
    The user's input is in $ARGUMENTS. If empty, ask:
    "What task do you want to plan? Describe it in a sentence."
  </gate>
</prerequisites>

<debate-protocol>
  <overview>
    You orchestrate a sprint planning ceremony with three voices:
    - **Proposer** (green agent): drafts and expands scope
    - **Critic** (red agent): challenges and reduces scope
    - **User**: decides, approves, or redirects

    Each round: proposer speaks, critic responds, user decides.
    Sections lock when the user approves them.
  </overview>

  <sections lock-on-approval="true">
    <section name="description" required="true">
      What is this task and why does it matter?
      Include user story format: "As a [who], I want [what], so that [why]"
    </section>

    <section name="story-points" required="true" values="1,2,3,5">
      Fibonacci subset. Debate the size early so model selection can adjust.
      1 = trivial (under an hour), 2 = small (a few hours),
      3 = medium (a day), 5 = large (multiple days, likely needs sub-tasks).
    </section>

    <section name="goals-nongoals" required="true">
      Goals: what is in scope (bulleted deliverables).
      Non-Goals: what is explicitly out of scope (link sibling tasks if they exist).
    </section>

    <section name="acceptance-criteria" required="true">
      Testable checkboxes grouped by functional area.
      Each criterion must be verifiable: "X happens when Y" not "X works correctly".
    </section>

    <section name="sub-tasks" required="false">
      Only needed for 3+ point tasks.
      One level deep. Each sub-task gets: name, points, brief description.
      If a sub-task exceeds 3 points, it should be its own task.
    </section>

    <section name="references" required="false">
      Links to related Notion tasks, docs, PRs, external resources.
      Discovered during debate or from existing-tasks query.
    </section>
  </sections>

  <round-protocol>
    For each unlocked section:

    1. Spawn the proposer agent (via Agent tool) with:
       - The section name and requirements
       - Project context from prerequisites
       - Any prior debate context for this section
       Pass model override based on story points (see model-selection below).

    2. Present the proposer's draft to the conversation.

    3. Spawn the critic agent (via Agent tool) with:
       - The proposer's draft
       - The section requirements
       - Project context
       Same model override as proposer.

    4. Present the critic's challenge to the conversation.

    5. Ask the user:
       "Approve this section, request changes, or redirect?"
       - If approved: lock section, move to next
       - If changes requested: incorporate feedback, run another round
       - If redirected: shift topic as directed
  </round-protocol>

  <model-selection>
    <rule when="story-points == 1">
      Override agents with: model: sonnet, effort: low
    </rule>
    <rule when="story-points == 2">
      Override agents with: model: sonnet, effort: medium
    </rule>
    <rule when="story-points == 3">
      Override agents with: model: sonnet, effort: high
    </rule>
    <rule when="story-points == 5">
      Override agents with: model: opus, effort: medium
    </rule>
    <rule when="unknown">
      Default: model: sonnet, effort: medium.
      If any section exceeds 3 rounds, escalate to sonnet/high.
      User can override at any time.
    </rule>
  </model-selection>
</debate-protocol>

<write-to-notion>
  Once all required sections are locked:

  <step name="confirm">
    Present the complete task summary to the user.
    Show: Task Name, Story Points, Priority, Type, Labels, all page body sections.
    Ask for final confirmation before writing to Notion.
  </step>

  <step name="create-parent">
    Create a page in the Tasks DB via Notion MCP `notion-create-pages`:
    - Parent: `{ type: "data_source_id", data_source_id: "collection://[tasks_db]" }`
    - Properties:
      - Task Name: from debate
      - Status: "To Do"
      - Priority: from debate (Urgent/High/Medium/Low)
      - Story Points: from debate (1/2/3/5)
      - Type: from debate (Feature/Bug/Chore/Spike/Docs)
      - Labels: from debate
      - Project: relation to project_page URL
      - Notes: one-liner summary
    - Content: formatted using the story-output template
      (read `${CLAUDE_SKILL_DIR}/templates/story-output.md` for structure)
  </step>

  <step name="create-subtasks" condition="sub-tasks exist">
    For each sub-task, create a Tasks DB entry:
    - Task Name: sub-task name
    - Status: "To Do"
    - Story Points: sub-task points
    - Parent Issue: relation to parent task URL
    - Labels: inherited from parent
    - Project: same as parent
    - Notes: sub-task description
  </step>

  <step name="report">
    Show the user:
    - Parent task link with Issue Key
    - Sub-task links with Issue Keys
    - Total story points (parent + sub-tasks)
  </step>
</write-to-notion>
