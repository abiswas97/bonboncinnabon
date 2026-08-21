from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

from devlab_contracts import (
    ContractError,
    TRANSITIONS,
    closure_targets,
    require_capabilities,
    transition_effects,
    transition_kind,
    validate_hierarchy,
    velocity,
)


def task(identifier, level="Task", status="To Do", points=2, parent_id=None):
    return {
        "id": identifier,
        "name": identifier,
        "level": level,
        "status": status,
        "points": points,
        "parent_id": parent_id,
        "blocked_by": [],
    }


class TransitionTests(unittest.TestCase):
    def test_every_listed_transition_and_no_other_transition(self):
        statuses = set(TRANSITIONS)
        for source, rules in TRANSITIONS.items():
            listed = set(rules["normal"] + rules["confirmation"])
            for target in statuses:
                if target in listed:
                    self.assertIn(transition_kind(source, target), {"normal", "confirmation"})
                else:
                    with self.assertRaises(ContractError):
                        transition_kind(source, target)

    def test_transition_side_effects(self):
        self.assertEqual(
            transition_effects({"status": "To Do", "start_date": None}, "In Progress", "2026-08-21"),
            {"Status": "In Progress", "Start Date": "2026-08-21"},
        )
        with self.assertRaisesRegex(ContractError, "requires at least one blocker"):
            transition_effects({"status": "To Do"}, "Blocked", "2026-08-21")
        self.assertEqual(
            transition_effects({"status": "Blocked"}, "In Progress", "2026-08-21", ["x"])["Blocked By"],
            [],
        )
        self.assertIsNone(transition_effects({"status": "Done"}, "To Do", "2026-08-21")["End Date"])


class HierarchyTests(unittest.TestCase):
    def test_parent_cannot_close_with_open_child(self):
        tasks = [task("parent", points=3), task("child", "Sub-task", points=3, parent_id="parent")]
        with self.assertRaisesRegex(ContractError, "descendants are open"):
            closure_targets("parent", tasks, recursive=False)
        self.assertEqual(closure_targets("parent", tasks, recursive=True), ["child", "parent"])

    def test_terminal_parent_with_open_child_is_invalid(self):
        tasks = [task("parent", status="Done", points=3), task("child", "Sub-task", points=3, parent_id="parent")]
        with self.assertRaisesRegex(ContractError, "terminal parent"):
            validate_hierarchy(tasks)

    def test_subtask_points_must_equal_parent_and_velocity_never_double_counts(self):
        tasks = [
            task("parent", status="Done", points=3),
            task("one", "Sub-task", status="Done", points=1, parent_id="parent"),
            task("two", "Sub-task", status="Done", points=2, parent_id="parent"),
        ]
        self.assertEqual(velocity(tasks), (3, 3))
        tasks[2]["points"] = 3
        with self.assertRaisesRegex(ContractError, "points must equal"):
            validate_hierarchy(tasks)

    def test_epics_have_no_points_and_subtasks_are_leaves(self):
        with self.assertRaisesRegex(ContractError, "Epics cannot"):
            validate_hierarchy([task("epic", "Epic", points=1)])
        tasks = [task("parent"), task("child", "Sub-task", parent_id="parent"), task("grandchild", "Sub-task", points=2, parent_id="child")]
        with self.assertRaises(ContractError):
            validate_hierarchy(tasks)


class BoundaryTests(unittest.TestCase):
    def test_missing_notion_capabilities_are_actionable(self):
        with self.assertRaisesRegex(ContractError, "create, query, update"):
            require_capabilities({"search", "fetch"})

    def test_legacy_migration_previews_then_requires_confirmation_and_preserves_input(self):
        migration = PLUGIN / "skills/setup/scripts/migrate_config.py"
        legacy_text = """project_name: Legacy Project
notion:
  project_page: 11111111-1111-4111-8111-111111111111
  product_spec: null
  tasks_db: 22222222-2222-4222-8222-222222222222
  task_template: 33333333-3333-4333-8333-333333333333
sync:
  sources:
    - CLAUDE.md
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "legacy.yaml"
            output = root / ".devlab/config.yaml"
            legacy.write_text(legacy_text)
            preview = subprocess.run([sys.executable, migration, legacy, output], text=True, capture_output=True)
            self.assertEqual(preview.returncode, 3)
            self.assertIn("schema_version: 1", preview.stdout)
            self.assertFalse(output.exists())
            confirmed = subprocess.run([sys.executable, migration, legacy, output, "--confirm"], text=True, capture_output=True)
            self.assertEqual(confirmed.returncode, 0, confirmed.stderr)
            self.assertTrue(output.exists())
            self.assertEqual(legacy.read_text(), legacy_text)
            first_output = output.read_text()
            repeated = subprocess.run([sys.executable, migration, legacy, output, "--confirm"], text=True, capture_output=True)
            self.assertEqual(repeated.returncode, 2)
            self.assertEqual(output.read_text(), first_output)

    def test_legacy_migration_rejects_invalid_identifiers(self):
        migration = PLUGIN / "skills/setup/scripts/migrate_config.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "legacy.yaml"
            output = root / "config.yaml"
            legacy.write_text("""project_name: Broken
notion:
  project_page: not-a-uuid
  product_spec: null
  tasks_db: also-bad
  task_template: bad
sync:
  sources:
    - AGENTS.md
""")
            result = subprocess.run([sys.executable, migration, legacy, output, "--confirm"], text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("must be a UUID", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
