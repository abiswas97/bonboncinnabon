# Per-Project Dashboard Data Shape

The skill must construct this JSON and pipe it to render.py via stdin:

```json
{
  "tasks": [
    {
      "name": "Task name",
      "issue_key": "FAM-12",
      "status": "In Progress",
      "story_points": 3,
      "priority": "High",
      "type": "Feature",
      "labels": ["frontend"],
      "start_date": "2026-03-20",
      "end_date": null,
      "last_edited": "2026-04-01T12:00:00Z",
      "blocked_by": null,
      "parent_issue": null,
      "sub_tasks": [
        {
          "name": "Sub-task name",
          "issue_key": "FAM-12a",
          "status": "Done",
          "story_points": 1
        }
      ]
    }
  ],
  "courses": 2,
  "papers": 1,
  "resources": 4
}
```

Invoke: `echo '<json>' | python3 ${CLAUDE_SKILL_DIR}/scripts/render.py --mode project --name "Familiar" --key "FAM"`
