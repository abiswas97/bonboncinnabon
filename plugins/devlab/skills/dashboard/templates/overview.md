# Cross-Project Dashboard Data Shape

The skill must construct this JSON and pipe it to render.py via stdin:

```json
{
  "projects": [
    {
      "name": "Example Project",
      "status": "Active",
      "total_tasks": 12,
      "done_tasks": 8,
      "total_pts": 31,
      "done_pts": 24,
      "blocked": 1,
      "velocity_total": 7
    }
  ],
  "knowledge": {
    "resources": 12,
    "courses": 3,
    "papers": 5,
    "tech_stack": 8
  },
  "attention": [
    "! PRJ-9   Example blocked task     Blocked 3d",
    "! PRJ-2   Example stale task      Stale 7d"
  ]
}
```

Invoke: `echo '<json>' | python3 ${CLAUDE_SKILL_DIR}/scripts/render.py --mode overview`
