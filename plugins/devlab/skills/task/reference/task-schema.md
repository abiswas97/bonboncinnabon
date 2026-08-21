# Task domain

The machine-readable task shape is `../../../domain/task.schema.json`; legal transitions are `../../../domain/transitions.json`.

## Hierarchy

```text
Epic
└── Task
    └── Sub-task
```

- Epic: strategic container, no parent, no story points, never executable.
- Task: executable planning unit, optionally parented by an Epic, points must be 1, 2, 3, or 5.
- Sub-task: leaf parented by a Task, points must be 1, 2, 3, or 5.
- When a Task has Sub-tasks, their point sum must equal the Task's points.
- Velocity counts each Task once and counts it completed only when that Task is Done.
- A terminal parent cannot have a non-terminal descendant.

## Required Notion properties

Task Name, Status, Priority, Story Points, Type, Level, Labels, Project, Parent Issue, Sub-issues, Blocked By, Notes, Start Date, End Date, Due Date, Created, Last Edited, Issue Key, and ID.

Setup discovers the Tasks database through the selected project's relation and verifies these properties. No database or template identifier is embedded in the plugin.
