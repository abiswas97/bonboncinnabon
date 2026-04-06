# Tasks DB Schema Reference

## Database

Collection: `collection://713f8ed9-13cd-4610-bcba-4dd80d83a67e`

## Properties

| Property | Type | Values / Notes |
|---|---|---|
| Task Name | title | Required |
| Status | status | Backlog, To Do, In Progress, In Review, Blocked, Done, Won't Do |
| Priority | select | Urgent, High, Medium, Low |
| Story Points | number | 1, 2, 3, or 5 |
| Type | select | Feature, Bug, Chore, Spike, Docs |
| Level | select | Epic, Task (default), Sub-task |
| Labels | multi_select | frontend, backend, ux, infra, api, performance, dx, security, core, growth |
| Project | relation | -> Dev Lab DB |
| Parent Issue | relation | -> Tasks DB (self, limit 1) |
| Sub-issues | relation | -> Tasks DB (self, reverse of Parent Issue) |
| Blocked By | relation | -> Tasks DB (self) |
| Assignee | person | limit 1 |
| Notes | text | Short context or description |
| Start Date | date | Set on first transition to In Progress |
| End Date | date | Set on transition to Done or Won't Do |
| Due Date | date | Optional deadline |
| Created | created_time | Auto |
| Last Edited | last_edited_time | Auto |
| Issue Key | formula | Project key + ID (e.g. PRJ-12) |
| ID | auto_increment | Sequential |

## Task Template Structure

Template ID: read from `.claude/devlab-notion.yaml` `task_template` field.

Page body sections (in order):

1. **Description** - what and why, user story format when applicable
2. **Goals / Non-Goals** - explicit scope in/out, with sub-headers
3. **Acceptance Criteria** - testable checkboxes, grouped by area
4. **References & Resources** - links to related tasks, docs, PRs
5. **Notes** - collapsible: Technical notes + Open questions
6. **Sub-tasks** - inline Tasks DB filtered to sub-issues, one level deep
7. **Log** - running notes, newest first

Each section has a gray quote/callout describing what belongs there (guides AI agents).

## Hierarchy Rules

<hierarchy>
  <level name="Epic" parent="none" children="Task">
    Strategic container grouping related Tasks.
    Must NOT have a Parent Issue.
    Should have Sub-issues (child Tasks).
    Not directly workable. Use /devlab:task-pick on child Tasks.
  </level>
  <level name="Task" default="true" parent="none|Epic" children="Sub-task">
    Deliverable work item.
    Can be standalone (no parent) or nested under an Epic via Parent Issue.
    Can have Sub-tasks as children (one level deep).
  </level>
  <level name="Sub-task" parent="Task" children="none">
    Granular step under a Task.
    MUST have a Parent Issue pointing to a Task (never an Epic).
    Leaf node. Cannot have children.
  </level>
</hierarchy>

- Sub-tasks inherit Labels and Project from parent
- Sub-tasks get their own Story Points (do not double-count with parent)
- Epic Story Points represent total scope; child Task points are the source of truth

## Status Transitions

```
Backlog -> To Do -> In Progress -> In Review -> Done
                       |                        |
                       +-> Blocked               +-> Won't Do
```

- Backlog -> Done directly requires confirmation
- In Progress sets Start Date (first time only)
- Done / Won't Do sets End Date
- Blocked prompts for Blocked By relation
