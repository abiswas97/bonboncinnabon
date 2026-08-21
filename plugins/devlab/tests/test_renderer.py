from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

PLUGIN = Path(__file__).parents[1]
RENDERER = PLUGIN / "skills/dashboard/scripts/render.py"
SNAPSHOTS = Path(__file__).parent / "snapshots"
spec = importlib.util.spec_from_file_location("devlab_renderer", RENDERER)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def run(document):
    return subprocess.run([sys.executable, RENDERER], input=json.dumps(document), text=True, capture_output=True)


class RendererTests(unittest.TestCase):
    def test_empty_project_snapshot(self):
        result = run({"mode": "project", "project_name": "Empty", "key": "EMP", "as_of": "2026-08-21T12:00:00+05:30", "tasks": []})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (SNAPSHOTS / "empty-project.txt").read_text())

    def test_quotes_newlines_unicode_and_fixed_timestamp(self):
        document = {
            "mode": "project",
            "project_name": "Avi's \"計画\"\nNext",
            "key": "Q",
            "as_of": "2026-08-21T12:00:00+05:30",
            "tasks": [{"id": "1", "name": "Café 計画", "level": "Task", "status": "Done", "points": 2, "parent_id": None, "blocked_by": []}],
        }
        result = run(document)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2026-08-21T12:00:00+05:30", result.stdout)
        self.assertIn("Café 計画", result.stdout)
        for line in result.stdout.splitlines():
            self.assertLessEqual(renderer.display_width(line), renderer.WIDTH)

    def test_subtask_points_are_displayed_but_not_aggregated(self):
        tasks = [
            {"id": "t", "name": "Parent", "level": "Task", "status": "Done", "points": 3, "parent_id": None, "blocked_by": []},
            {"id": "s1", "name": "One", "level": "Sub-task", "status": "Done", "points": 1, "parent_id": "t", "blocked_by": []},
            {"id": "s2", "name": "Two", "level": "Sub-task", "status": "Done", "points": 2, "parent_id": "t", "blocked_by": []},
        ]
        result = run({"mode": "project", "project_name": "P", "key": "P", "as_of": "2026-08-21T00:00:00Z", "tasks": tasks})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("3/3 points", result.stdout)
        self.assertIn("1pt decomposition", result.stdout)

    def test_blocked_age_and_timezone_snapshot(self):
        tasks = [
            {"id": "t", "name": "Parent", "level": "Task", "status": "Blocked", "points": 3, "parent_id": None, "blocked_by": ["b"], "start_date": "2026-08-18T06:30:00Z"},
            {"id": "s1", "name": "One", "level": "Sub-task", "status": "Done", "points": 1, "parent_id": "t", "blocked_by": []},
            {"id": "s2", "name": "Two", "level": "Sub-task", "status": "To Do", "points": 2, "parent_id": "t", "blocked_by": []},
        ]
        result = run({"mode": "project", "project_name": "Roadmap", "key": "RD", "as_of": "2026-08-21T12:00:00+05:30", "tasks": tasks})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (SNAPSHOTS / "blocked-project.txt").read_text())

    def test_empty_overview(self):
        result = run({"mode": "overview", "as_of": "2026-08-21T00:00:00Z", "projects": []})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No active projects", result.stdout)

    def test_malformed_json_and_invalid_schema_fail_concisely(self):
        malformed = subprocess.run([sys.executable, RENDERER], input="{", text=True, capture_output=True)
        self.assertEqual(malformed.returncode, 2)
        self.assertIn("malformed JSON", malformed.stderr)
        invalid = run({"mode": "project", "tasks": [{"level": "Task"}]})
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("input error", invalid.stderr)

    def test_bar_clamps_invalid_totals(self):
        self.assertEqual(renderer.bar(5, -2, 4), "░░░░")
        self.assertEqual(renderer.bar(20, 10, 4), "████")

    def test_dates_must_be_timezone_aware(self):
        result = run({"mode": "project", "project_name": "P", "key": "P", "as_of": "2026-08-21", "tasks": []})
        self.assertEqual(result.returncode, 2)
        self.assertIn("timezone", result.stderr)


if __name__ == "__main__":
    unittest.main()
