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
| Issue Key | formula | Project key + ID (e.g. FAM-12) |
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

## Sub-task Rules

- Sub-tasks are Tasks DB entries with Parent Issue set to the parent task
- One level deep only. If a sub-task needs children, promote it to its own task
- Sub-tasks inherit Labels and Project from parent
- Sub-tasks get their own Story Points (do not double-count with parent)

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
