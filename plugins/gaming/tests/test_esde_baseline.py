import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import esde_baseline  # noqa: E402
import gaming_profile as gp  # noqa: E402

EXAMPLE = json.loads((PLUGIN / "profile.example.json").read_text(encoding="utf-8"))
SETTINGS = """<?xml version="1.0"?>
<bool name="CollectionShowSystemInfo" value="true" />
<string name="ThemeSet" value="synthetic-theme" />
<!-- comments survive the synthetic root -->
<int name="ScreensaverTimer" value="300000" />
<float name="ScreenBrightness" value="0.75" />
<string name="ScraperUsernameScreenScraper" value="someone" />
<string name="ScraperPasswordScreenScraper" value="not-a-real-password" />
<string name="RetroAchievementsToken" value="not-a-real-token" />
<string name="UIMode_passkey" value="not-a-real-passkey" />
"""
CREDENTIALS = ["ScraperUsernameScreenScraper", "ScraperPasswordScreenScraper", "RetroAchievementsToken",
               "UIMode_passkey"]


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = esde_baseline.main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


class BaselineTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)
        self.settings = self.dir / "es_settings.xml"
        self.settings.write_text(SETTINGS, encoding="utf-8")

    def baseline(self, values):
        path = self.dir / "baseline.json"
        path.write_text(json.dumps(values), encoding="utf-8")
        return path

    def test_reads_every_setting_type(self):
        self.assertEqual(esde_baseline.read_settings(self.settings)["ScreenBrightness"], "0.75")
        self.assertEqual(len(esde_baseline.read_settings(self.settings)), 8)

    def test_matching_baseline_passes(self):
        baseline = self.baseline({"ThemeSet": "synthetic-theme", "CollectionShowSystemInfo": "true"})
        code, out, err = run("check", "--settings", self.settings, "--baseline", baseline)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"checked": 2, "drift": []})
        self.assertEqual(err, "")

    def test_changed_and_missing_keys_are_drift(self):
        baseline = self.baseline({"ThemeSet": "other-theme", "ScreensaverTimer": "300000",
                                  "CollectionShowSystemInfo": "True", "ThemeVariant": "dark"})
        code, out, err = run("check", "--settings", self.settings, "--baseline", baseline)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out), {"checked": 4, "drift": [
            {"key": "ThemeSet", "expected": "other-theme", "found": "synthetic-theme"},
            {"key": "CollectionShowSystemInfo", "expected": "True", "found": "true"},
            {"key": "ThemeVariant", "expected": "dark", "found": None},
        ]})
        self.assertIn("esde_baseline: 3 of 4 baselined settings drifted", err)

    def test_non_string_baseline_is_rejected(self):
        code, _, err = run("check", "--settings", self.settings, "--baseline", self.baseline({"ThemeSet": True}))
        self.assertEqual(code, 1)
        self.assertIn("string values", err)

    def test_device_baseline_comes_from_profile(self):
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.dir)}):
            self.assertEqual(run("check", "--settings", self.settings, "--device", "handheld")[0], 2)
            data = copy.deepcopy(EXAMPLE)
            data["devices"]["handheld"]["frontend"]["baseline"]["settings"] = {"ThemeSet": "synthetic-theme"}
            gp.profile_path().parent.mkdir(parents=True)
            gp.profile_path().write_text(json.dumps(data), encoding="utf-8")
            code, out, _ = run("check", "--settings", self.settings, "--device", "handheld")
            self.assertEqual((code, json.loads(out)["checked"]), (0, 1))
            code, _, err = run("check", "--settings", self.settings, "--device", "desktop")
            self.assertEqual(code, 1)
            self.assertIn("no value at /devices/desktop/frontend/baseline/settings", err)

    def test_capture_all_excludes_credentials(self):
        code, out, err = run("capture", "--settings", self.settings)
        self.assertEqual(code, 0)
        captured = json.loads(out)
        self.assertEqual(list(captured), ["CollectionShowSystemInfo", "ThemeSet", "ScreensaverTimer",
                                          "ScreenBrightness"])
        self.assertNotIn("not-a-real", out)
        self.assertIn("left out credential settings: " + ", ".join(CREDENTIALS), err)
        profile = copy.deepcopy(EXAMPLE)
        profile["devices"]["handheld"]["frontend"]["baseline"]["settings"] = captured
        self.assertEqual(gp.validate(profile), [])

    def test_capture_selected_keys_still_excludes_credentials(self):
        code, out, err = run("capture", "--settings", self.settings,
                             "--keys", "ThemeSet, ScraperPasswordScreenScraper")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ThemeSet": "synthetic-theme"})
        self.assertIn("ScraperPasswordScreenScraper", err)

    def test_capture_excludes_ui_mode_passkey(self):
        code, out, err = run("capture", "--settings", self.settings, "--keys", "ThemeSet,UIMode_passkey")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ThemeSet": "synthetic-theme"})
        self.assertEqual(err, "esde_baseline: left out credential settings: UIMode_passkey\n")

    def test_capture_unknown_key_fails(self):
        code, out, err = run("capture", "--settings", self.settings, "--keys", "ThemeSet,NoSuchKey")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("NoSuchKey", err)

    def test_malformed_settings_fail(self):
        self.settings.write_text('<?xml version="1.0"?>\n<string name="ThemeSet" value="x"\n', encoding="utf-8")
        code, _, err = run("capture", "--settings", self.settings)
        self.assertEqual(code, 1)
        self.assertIn("esde_baseline: ", err)


if __name__ == "__main__":
    unittest.main()
