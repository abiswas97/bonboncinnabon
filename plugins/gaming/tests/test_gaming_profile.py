import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import gaming_profile as gp  # noqa: E402

EXAMPLE = json.loads((PLUGIN / "profile.example.json").read_text(encoding="utf-8"))


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = gp.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class ProfileTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory()
        self.addCleanup(self.home.cleanup)
        patcher = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": self.home.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.path = Path(self.home.name) / "bonboncinnabon" / "gaming" / "profile.json"

    def init_example(self):
        source = Path(self.home.name) / "seed.json"
        source.write_text(json.dumps(EXAMPLE), encoding="utf-8")
        self.assertEqual(run("init", "--from", str(source))[0], 0)

    def test_path_uses_absolute_xdg_and_ignores_relative(self):
        self.assertEqual(gp.profile_path(), self.path)
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": "relative/dir"}):
            self.assertEqual(gp.profile_path(), Path.home() / ".config/bonboncinnabon/gaming/profile.json")

    def test_example_is_valid(self):
        self.assertEqual(gp.validate(EXAMPLE), [])

    def test_missing_profile_routes_to_setup(self):
        code, _, err = run("show")
        self.assertEqual(code, 2)
        self.assertIn("Run the gaming setup skill", err)

    def test_init_refuses_to_overwrite(self):
        self.init_example()
        code, _, err = run("init", "--from", str(Path(self.home.name) / "seed.json"))
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)

    def test_set_writes_history_and_dry_run_does_not(self):
        self.init_example()
        before = self.path.read_bytes()
        code, out, _ = run("set", "/devices/handheld/install_opt_in", "true", "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("would change", out)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(run("set", "/devices/handheld/install_opt_in", "true")[0], 0)
        self.assertTrue(gp.load()["devices"]["handheld"]["install_opt_in"])
        history = list((self.path.parent / "history").iterdir())
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].read_bytes(), before)
        self.assertEqual(oct(self.path.stat().st_mode & 0o777), "0o600")

    def test_invalid_update_leaves_file_unchanged(self):
        self.init_example()
        before = self.path.read_bytes()
        code, _, err = run("unset", "/devices/handheld/label")
        self.assertEqual(code, 1)
        self.assertIn("/devices/handheld/label", err)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertFalse((self.path.parent / "history").exists())

    def test_rejects_credentials(self):
        data = copy.deepcopy(EXAMPLE)
        data["devices"]["handheld"]["connect"]["password"] = "x"
        data["backup_targets"]["cloud"]["api_token"] = "x"
        data["preferences"].append("-----BEGIN OPENSSH PRIVATE KEY-----")
        errors = "\n".join(gp.validate(data))
        self.assertIn("connect/password", errors)
        self.assertIn("api_token", errors)
        self.assertIn("private key", errors)
        clean = copy.deepcopy(EXAMPLE)
        clean["devices"]["handheld"]["paths"]["bypass"] = "/x"
        self.assertEqual(gp.validate(clean), [])

    def test_rejects_passkey_settings(self):
        data = copy.deepcopy(EXAMPLE)
        data["devices"]["handheld"]["frontend"]["baseline"]["settings"]["UIMode_passkey"] = "uuddlrlrba"
        self.assertEqual(gp.validate(data), [
            "/devices/handheld/frontend/baseline/settings/UIMode_passkey: credentials do not belong in the profile"])
        self.assertIsNone(gp.SECRET_KEY.search("passkey_hint"))

    def test_note_cap(self):
        data = copy.deepcopy(EXAMPLE)
        data["devices"]["handheld"]["notes"] = []
        for index in range(gp.MAX_NOTES):
            gp.add_note(data, "handheld", f"fact {index}", today=date(2026, 1, 1))
        self.assertEqual(gp.validate(data), [])
        with self.assertRaises(gp.ProfileError):
            gp.add_note(data, "handheld", "one too many")
        with self.assertRaises(gp.ProfileError):
            gp.add_note(data, "nope", "unknown device")

    def test_structural_rules(self):
        data = copy.deepcopy(EXAMPLE)
        data["libraries"]["second"] = {"root": "/x", "canonical": True}
        data["devices"]["handheld"]["connect"] = {"method": "ssh"}
        data["devices"]["Bad_ID"] = {"label": "x", "connect": {"method": "local"}}
        data["backup_targets"]["cloud"]["library"] = "missing"
        data["timezone"] = "Not/AZone"
        errors = "\n".join(gp.validate(data))
        for expected in ("exactly one library", "ssh_alias", "Bad_ID", "/backup_targets/cloud/library", "/timezone"):
            self.assertIn(expected, errors)

    def test_pointer_escaping_and_note_command(self):
        self.init_example()
        self.assertEqual(run("set", "/collections/a~1b", '"x"')[0], 0)
        self.assertEqual(gp.load()["collections"]["a/b"], "x")
        self.assertEqual(run("note", "desktop", "Windowed launcher works.")[0], 0)
        self.assertEqual(gp.load()["devices"]["desktop"]["notes"][-1]["text"], "Windowed launcher works.")
        code, out, _ = run("show", "/devices/desktop/connect/method")
        self.assertEqual((code, json.loads(out)), (0, "local"))


if __name__ == "__main__":
    unittest.main()
