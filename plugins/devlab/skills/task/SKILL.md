---
name: task
description: Plan a Notion task through isolated proposer and critic debate, then create only the fully approved result.
---

# Plan a task

Read `../../domain/notion-capabilities.md`, `reference/task-schema.md`, `reference/proposer.md`, `reference/critic.md`, and `templates/story-output.md` before starting.

1. Validate `.devlab/config.yaml` and require `search`, `fetch`, `query`, and `create`.
2. Resolve any requested Epic and fetch sibling Tasks. Read available shared repository guidance and relevant implementation sources.
3. Verify that the active host supports two isolated subagents. If it does not, stop: `DevLab task planning requires host-native isolated subagent delegation for proposer and critic roles.`
4. For each unlocked section, spawn a proposer using `reference/proposer.md`, then a separate critic using `reference/critic.md`. Give both the same project context and let the host choose its configured model.
5. Present both outputs and ask the user to approve, revise, or redirect the section. Lock only approved sections.
6. Enforce the domain rules before creation: Epics have no points; Tasks use 1, 2, 3, or 5 points; Sub-task points must sum exactly to the parent Task; Sub-tasks cannot have children.
7. Show the complete task, properties, page body, and every Sub-task. Obtain final confirmation immediately before any Notion write.
8. Create the parent, then confirmed Sub-tasks. On a partial connector failure, stop and report exactly which pages were created and which remain.

The Task's points are authoritative. Report them once; child points explain the decomposition.
