#!/usr/bin/env python3
"""Contract tests for schemas/chunk-task.schema.json. Run:

    python3 scripts/test_chunk_schema.py          (from the plugin root)

Two layers:
- STRUCTURAL (always run, stdlib `json` only): pin the load-bearing clauses so a
  careless edit can't silently weaken the contract — the work-axes if/then, the
  personal-forbids-axes else, the required list, kind=TEXT, and reminder.triggers
  being a non-empty array.
- SEMANTIC (run only when `jsonschema` is installed; pip install jsonschema):
  validate canonical instances against the real schema. Skips cleanly otherwise,
  so the stdlib-only invariant of the test suite is preserved.

The stage enum's single source of truth is config.yaml `contexts.work.pipeline`;
these tests pin the schema's own copy, not the cross-file sync (that has no stdlib
YAML reader).
"""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(os.path.dirname(HERE), "schemas", "chunk-task.schema.json")

with open(SCHEMA_PATH) as f:
    SCHEMA = json.load(f)

WORK_AXES = ["stage", "intensity", "ai_discount", "est0_min"]
STAGES = ["research", "db", "backend", "frontend", "review",
          "address-comments", "qa", "deploy"]

try:
    from jsonschema import Draft202012Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class Structure(unittest.TestCase):
    def test_base_required_includes_context(self):
        self.assertEqual(
            set(SCHEMA["required"]), {"id", "title", "context", "kind", "ai_generated"})

    def test_context_enum(self):
        self.assertEqual(SCHEMA["properties"]["context"]["enum"], ["work", "personal"])

    def test_work_requires_all_axes(self):
        self.assertEqual(SCHEMA["if"]["properties"]["context"]["const"], "work")
        self.assertEqual(set(SCHEMA["then"]["required"]), set(WORK_AXES))

    def test_personal_forbids_work_axes(self):
        # `else` sets each work axis to the `false` schema (property must be absent).
        forbidden = SCHEMA["else"]["properties"]
        for axis in ["stage", "intensity", "ai_discount"]:
            self.assertIs(forbidden.get(axis), False, f"{axis} should be forbidden for personal")
        # est0_min is allowed for personal (optional), so must NOT be forbidden.
        self.assertNotIn("est0_min", forbidden)

    def test_kind_and_ai_generated_pinned(self):
        self.assertEqual(SCHEMA["properties"]["kind"]["const"], "TEXT")
        self.assertEqual(SCHEMA["properties"]["ai_generated"]["const"], True)

    def test_reminder_triggers_is_nonempty_array(self):
        reminder = SCHEMA["properties"]["reminder"]
        self.assertEqual(set(reminder["required"]), {"due", "triggers"})
        triggers = reminder["properties"]["triggers"]
        self.assertEqual(triggers["type"], "array")
        self.assertEqual(triggers["minItems"], 1)
        self.assertEqual(reminder["additionalProperties"], False)

    def test_stage_enum_matches_expected(self):
        self.assertEqual(SCHEMA["properties"]["stage"]["enum"], STAGES)

    def test_no_extra_properties_allowed(self):
        self.assertEqual(SCHEMA["additionalProperties"], False)


def work(**over):
    c = {"id": "c", "title": "Backend: checkout API", "context": "work",
         "stage": "backend", "intensity": "deep", "ai_discount": "discounted",
         "est0_min": 45, "kind": "TEXT", "ai_generated": True}
    c.update(over)
    return c


def personal(**over):
    c = {"id": "p", "title": "Book the dentist appointment", "context": "personal",
         "kind": "TEXT", "ai_generated": True}
    c.update(over)
    return c


@unittest.skipUnless(HAS_JSONSCHEMA, "pip install jsonschema to run semantic validation")
class Semantic(unittest.TestCase):
    def setUp(self):
        Draft202012Validator.check_schema(SCHEMA)
        self.v = Draft202012Validator(SCHEMA)

    def valid(self, obj):
        return not list(self.v.iter_errors(obj))

    def test_work_chunk_valid(self):
        self.assertTrue(self.valid(work()))

    def test_work_missing_stage_invalid(self):
        c = work()
        del c["stage"]
        self.assertFalse(self.valid(c))

    def test_personal_chunk_valid(self):
        self.assertTrue(self.valid(personal(
            priority="should", est0_min=15,
            reminder={"due": "2026-06-03T10:00:00+05:30", "triggers": ["TRIGGER:PT0S"]})))

    def test_personal_with_work_axis_invalid(self):
        self.assertFalse(self.valid(personal(stage="backend")))

    def test_personal_est0_allowed(self):
        self.assertTrue(self.valid(personal(est0_min=15)))

    def test_reminder_single_trigger_string_invalid(self):
        self.assertFalse(self.valid(personal(
            reminder={"due": "2026-06-03T10:00:00+05:30", "trigger": "TRIGGER:PT0S"})))

    def test_reminder_empty_triggers_invalid(self):
        self.assertFalse(self.valid(personal(
            reminder={"due": "2026-06-03T10:00:00+05:30", "triggers": []})))

    def test_no_context_invalid(self):
        c = work()
        del c["context"]
        self.assertFalse(self.valid(c))


if __name__ == "__main__":
    unittest.main(verbosity=2)
