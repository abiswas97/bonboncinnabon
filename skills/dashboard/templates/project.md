# Per-Project Dashboard Data Shape

The skill must construct this JSON and pipe it to render.py via stdin:

```json
{
  "tasks": [
    {
      "name": "Example task",
      "issue_key": "PRJ-12",
      "status": "In Progress",
      "story_points": 3,
      "priority": "High",
      "type": "Feature",
      "level": "Task",
      "labels": ["frontend"],
      "start_date": "2026-03-20",
      "end_date": null,
      "last_edited": "2026-04-01T12:00:00Z",
      "blocked_by": null,
      "parent_issue": null,
      "sub_tasks": [
        {
          "name": "Sub-task name",
          "issue_key": "PRJ-12a",
          "status": "Done",
          "story_points": 1,
          "level": "Sub-task"
        }
      ]
    }
  ],
  "epics": [
    {
      "name": "Example epic",
      "issue_key": "PRJ-5",
      "status": "In Progress",
      "total_tasks": 6,
      "done_tasks": 2,
      "total_pts": 21,
      "done_pts": 8
    }
  ],
  "courses": 2,
  "papers": 1,
  "resources": 4
}
```

Invoke: `echo '<json>' | python3 ${CLAUDE_SKILL_DIR}/scripts/render.py --mode project --name "<project_name>" --key "<project_key>"`
