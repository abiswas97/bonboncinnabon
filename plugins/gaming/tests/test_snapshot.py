import contextlib
import copy
import hashlib
import io
import itertools
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import gaming_profile as gp  # noqa: E402
import snapshot  # noqa: E402

EXAMPLE = json.loads((PLUGIN / "profile.example.json").read_text(encoding="utf-8"))
START = datetime(2026, 10, 9, 12, 0, 0, tzinfo=ZoneInfo("Europe/London"))
LABEL = "Fake Handheld"
SECRET = "hunter2-do-not-print"

CONFIG_FILES = {
    "Android/data/com.retroarch/files/retroarch.cfg",
    "Android/data/com.retroarch/files/core.opt",
    "RetroArch/config/mGBA/mGBA.opt",
    "RetroArch/config/mGBA/game.cfg",
    "RetroArch/config/mGBA/crt.slangp",
    "RetroArch/remaps/mGBA/game.rmp",
    "RetroArch/autoconfig/pad.cfg",
    "RetroArch/autoconfig/PAD2.CFG",
    "ES-DE/settings/es_settings.xml",
    "ES-DE/settings/notes.txt",
    "ES-DE/collections/custom-cozy.cfg",
    "ES-DE/custom_systems/es_systems.xml",
    "ES-DE/gamelists/gba/gamelist.xml",
}
FULL_ONLY = {"ROMs/gba/game.gba", "Saves/game.srm", "ES-DE/themes/theme.xml", "ES-DE/downloaded_media/x.png"}
NEVER = {"Android/data/com.retroarch/files/log.txt", "RetroArch/config/readme.md",
         "RetroArch/shaders/crt.slangp"}


def shell_ok(command):
    return subprocess.run(["bash", "-c", command], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


GNU_STREAMS = shell_ok("sha256sum --zero -- /dev/null && printf 'dev/null\\0' | tar -C / --null -T - -cf - >/dev/null")
GNU_STAT = shell_ok("stat -c %s -- /dev/null")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(os.path.realpath(temp.name))
        self.device = self.base / "device"
        self.library = self.base / "library"
        self.library.mkdir()
        for patcher in (mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.base / "xdg")}),
                        mock.patch.object(snapshot, "_now", self.ticking_clock())):
            patcher.start()
            self.addCleanup(patcher.stop)
        for relative in CONFIG_FILES | FULL_ONLY | NEVER:
            self.put(relative, f"data for {relative}\n")
        d = self.device
        self.cfg = self.put("Android/data/com.retroarch/files/retroarch.cfg",
                            f'rgui_config_directory = "{d}/RetroArch/config"\n'
                            f'input_remapping_directory = "{d}/RetroArch/remaps"\n'
                            'joypad_autoconfig_dir = "default"\n'
                            'core_options_path = ""\n'
                            f'cheevos_password = "{SECRET}"\n')
        self.fake = {
            "label": LABEL,
            "connect": {"method": "local", "hints": ["Wake the fake device."]},
            "paths": {"roms": str(d / "ROMs"), "saves": str(d / "Saves")},
            "emulators": {"retroarch": {
                "config": str(self.cfg),
                "config_dirs": [str(d / "RetroArch/autoconfig")],
                "config_keys": ["rgui_config_directory", "input_remapping_directory",
                                "joypad_autoconfig_dir", "core_options_path"],
            }},
            "frontend": {"home": str(d / "ES-DE"), "settings_file": str(d / "ES-DE/settings/es_settings.xml")},
        }
        self.save()

    @staticmethod
    def ticking_clock():
        ticks = itertools.count()
        return lambda timezone: START + timedelta(seconds=next(ticks))

    def put(self, relative, text):
        path = self.device / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def save(self):
        data = copy.deepcopy(EXAMPLE)
        data["libraries"]["main"].update(root=str(self.library), volume="/")
        data["devices"] = {"fake": self.fake}
        gp.write(data)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = snapshot.main(["--device", "fake", *argv])
        return code, out.getvalue(), err.getvalue()

    def snapshot_ok(self, scope="config"):
        code, out, err = self.run_cli("--scope", scope)
        self.assertEqual((code, err), (0, ""))
        summary = json.loads(out)
        folder = Path(summary["directory"])
        return summary, folder, json.loads((folder / "manifest.json").read_text(encoding="utf-8"))

    def sources(self, manifest):
        return {str(Path(record["source"]).relative_to(self.device)) for record in manifest["files"]}

    def only_folder(self, *parts):
        folders = list(self.library.joinpath(*parts, LABEL).iterdir())
        self.assertEqual(len(folders), 1)
        return folders[0]

    def assert_incomplete(self, code, err, reason):
        """The failed build stays in Staging, marked incomplete."""
        self.assertEqual(code, 1)
        self.assertIn("not verified", err)
        folder = self.only_folder("Staging", "snapshots")
        self.assertIn(str(folder), err)
        self.assertEqual(sorted(p.name for p in folder.iterdir()), ["config.tar.incomplete", "manifest.json"])
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "incomplete")
        self.assertIn(reason, manifest["reason"])


class LocalSnapshotTest(SnapshotTest):
    def test_b2_library_checks_create_nothing(self):
        with mock.patch("os.path.ismount", return_value=False):
            code, out, err = self.run_cli("--scope", "config")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("library drive not mounted", err)
        self.assertEqual(list(self.library.iterdir()), [])

        self.library.rmdir()
        code, _, err = self.run_cli("--scope", "config")
        self.assertEqual(code, 1)
        self.assertIn("library root missing", err)
        self.assertFalse(self.library.exists())

    def test_relative_configured_path_is_an_error(self):
        self.cfg.write_text('rgui_config_directory = "relative/config"\n', encoding="utf-8")
        code, _, err = self.run_cli("--scope", "config")
        self.assertEqual(code, 1)
        self.assertIn("emulators/retroarch/config_keys/rgui_config_directory is a relative path", err)
        self.assertNotIn("relative/config", err)
        self.assertEqual(list(self.library.iterdir()), [])

    def test_home_relative_configured_path_resolves_on_device(self):
        self.cfg.write_text('rgui_config_directory = "~/RetroArch/config"\n', encoding="utf-8")
        with mock.patch.dict(os.environ, {"HOME": str(self.device)}):
            code, out, err = self.run_cli("--scope", "config", "--dry-run")
        self.assertEqual((code, err), (0, ""))
        self.assertIn(str(self.device / "RetroArch/config"), json.loads(out)["roots"])

    def test_b4_canonical_roots_dedupe_symlinks_and_record_missing(self):
        link = self.device / "remaps-link"
        link.symlink_to(self.device / "RetroArch/remaps")
        nowhere = str(self.device / "nowhere")
        self.fake["emulators"]["retroarch"]["config_dirs"] += [
            str(link), str(self.device / "RetroArch/config/mGBA"), nowhere]
        self.save()
        code, out, _ = self.run_cli("--scope", "config", "--dry-run")
        self.assertEqual(code, 0)
        plan = json.loads(out)
        d = self.device
        self.assertEqual(plan["roots"], sorted([
            str(self.cfg), str(self.cfg.parent), str(d / "RetroArch/autoconfig"),
            str(d / "RetroArch/config"), str(d / "RetroArch/remaps"),
            *(str(d / "ES-DE" / f) for f in snapshot.FRONTEND_FOLDERS)]))
        self.assertEqual(plan["missing_paths"], [nowhere])

        _, _, manifest = self.snapshot_ok()
        sources = [record["source"] for record in manifest["files"]]
        self.assertEqual(len(sources), len(set(sources)))
        self.assertEqual(self.sources(manifest), CONFIG_FILES)
        self.assertEqual(manifest["missing_paths"], [nowhere])

    def test_extension_filter_and_main_config_always_included(self):
        _, _, manifest = self.snapshot_ok()
        self.assertEqual(self.sources(manifest), CONFIG_FILES)

        self.fake["emulators"]["retroarch"]["config_extensions"] = [".opt"]
        self.save()
        _, _, manifest = self.snapshot_ok()
        self.assertEqual(self.sources(manifest), {
            "Android/data/com.retroarch/files/retroarch.cfg",
            "Android/data/com.retroarch/files/core.opt",
            "RetroArch/config/mGBA/mGBA.opt",
            *(f for f in CONFIG_FILES if f.startswith("ES-DE/")),
        })

    def test_full_scope_adds_paths_and_frontend_home(self):
        summary, folder, manifest = self.snapshot_ok("full")
        self.assertEqual(self.sources(manifest), CONFIG_FILES | FULL_ONLY)
        self.assertEqual(manifest["scope"], "full")
        self.assertTrue((folder / "full.tar").is_file())

    def test_full_scope_adds_data_keys_unfiltered(self):
        data = {"RetroArch/states/game.state1", "RetroArch/system/bios/gba_bios.bin"}
        for relative in data:
            self.put(relative, f"data for {relative}\n")
        with self.cfg.open("a", encoding="utf-8") as cfg:
            cfg.write(f'savestate_directory = "{self.device}/RetroArch/states"\n'
                      'system_directory = "~/RetroArch/system"\n'
                      'savefile_directory = "default"\n')
        self.fake["emulators"]["retroarch"]["data_keys"] = [
            "savefile_directory", "savestate_directory", "system_directory"]
        self.save()
        with mock.patch.dict(os.environ, {"HOME": str(self.device)}):
            _, _, config = self.snapshot_ok("config")
            _, _, full = self.snapshot_ok("full")
        self.assertEqual(self.sources(config), CONFIG_FILES)
        self.assertEqual(self.sources(full), CONFIG_FILES | FULL_ONLY | data)

        self.cfg.write_text('savestate_directory = "states"\n', encoding="utf-8")
        code, _, err = self.run_cli("--scope", "full", "--dry-run")
        self.assertEqual(code, 1)
        self.assertIn("emulators/retroarch/data_keys/savestate_directory is a relative path", err)
        self.assertEqual(self.run_cli("--scope", "config", "--dry-run")[0], 0)

    def test_b5_main_config_changed_while_discovering(self):
        original = snapshot.Local.read

        def read_then_save(backend, path):
            data = original(backend, path)
            with open(path, "a", encoding="utf-8") as file:
                file.write('video_driver = "gl"\n')
            return data

        with mock.patch.object(snapshot.Local, "read", read_then_save):
            code, _, err = self.run_cli("--scope", "config")
        self.assertEqual(code, 1)
        self.assertIn("changed while discovering; retry when quiet", err)
        self.assertEqual(list(self.library.iterdir()), [])

    def test_b6_private_new_folder_never_reused(self):
        stamp = "2026-10-09_12-00-00_BST"
        with mock.patch.object(snapshot, "_now", lambda timezone: START):
            summary, folder, _ = self.snapshot_ok()
            first = (folder / "manifest.json").read_bytes()
            code, _, err = self.run_cli("--scope", "config")
        self.assertEqual(folder, self.library / "Recovery" / LABEL / stamp)
        self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
        for name in ("config.tar", "manifest.json"):
            self.assertEqual((folder / name).stat().st_mode & 0o777, 0o600)
        self.assertIn("already exists", err)
        self.assertEqual(self.only_folder("Recovery"), folder)
        self.assertEqual(sorted(p.name for p in folder.iterdir()), ["config.tar", "manifest.json"])
        self.assertEqual((folder / "manifest.json").read_bytes(), first)
        self.assert_incomplete(code, err, "already exists; snapshots are never reused")
        self.assertEqual(self.only_folder("Staging", "snapshots").name, stamp)

    def test_b7_change_during_capture_keeps_incomplete_archive(self):
        original = snapshot.Local.archive

        def archive_then_edit(backend, paths, out):
            original(backend, paths, out)
            (self.device / "RetroArch/remaps/mGBA/game.rmp").write_text("changed\n", encoding="utf-8")

        with mock.patch.object(snapshot.Local, "archive", archive_then_edit):
            code, _, err = self.run_cli("--scope", "config")
        self.assert_incomplete(code, err, "source files changed during the snapshot")
        self.assertFalse((self.library / "Recovery").exists())

    def test_b8_unexpected_archive_member_fails_verification(self):
        original = snapshot.Local.archive

        def archive_duplicate(backend, paths, out):
            original(backend, paths + paths[:1], out)

        with mock.patch.object(snapshot.Local, "archive", archive_duplicate):
            code, _, err = self.run_cli("--scope", "config")
        self.assert_incomplete(code, err, "unexpected archive member")
        self.assertFalse((self.library / "Recovery").exists())

    def test_b9_verified_manifest_fields(self):
        with mock.patch.object(snapshot.os, "rename", wraps=os.rename) as rename:
            code, out, err = self.run_cli("--scope", "config")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.count("\n"), 1)
        summary = json.loads(out)
        folder = Path(summary["directory"])
        build = self.library / "Staging" / "snapshots" / LABEL / folder.name
        self.assertEqual(folder, self.library / "Recovery" / LABEL / "2026-10-09_12-00-00_BST")
        rename.assert_any_call(build, folder)
        self.assertFalse(build.exists())
        text = (folder / "manifest.json").read_text(encoding="utf-8")
        manifest = json.loads(text)
        self.assertEqual(set(manifest), {"status", "created_at", "device", "scope", "missing_paths",
                                         "files", "archive_sha256"})
        self.assertEqual((manifest["status"], manifest["device"], manifest["scope"], manifest["missing_paths"]),
                         ("verified", "fake", "config", []))
        self.assertEqual(datetime.fromisoformat(manifest["created_at"]).utcoffset(), timedelta(hours=1))
        self.assertEqual(manifest["archive_sha256"], sha256(folder / "config.tar"))
        self.assertFalse((folder / "config.tar.incomplete").exists())
        for record in manifest["files"]:
            self.assertEqual(set(record), {"source", "archive_path", "bytes", "sha256"})
            self.assertEqual(record["archive_path"], record["source"].lstrip("/"))
            self.assertEqual(record["bytes"], os.path.getsize(record["source"]))
            self.assertEqual(record["sha256"], sha256(record["source"]))
        self.assertEqual(summary, {"directory": str(folder), "status": "verified",
                                   "verified_files": len(CONFIG_FILES), "missing_paths": []})
        for output in (out, err, text):
            self.assertNotIn(SECRET, output)

    def test_dry_run_writes_nothing(self):
        code, out, err = self.run_cli("--scope", "full", "--dry-run")
        self.assertEqual((code, err), (0, ""))
        plan = json.loads(out)
        expected = CONFIG_FILES | FULL_ONLY
        self.assertEqual(plan["files"], len(expected))
        self.assertEqual(plan["bytes"], sum(os.path.getsize(self.device / f) for f in expected))
        self.assertEqual(plan["missing_paths"], [])
        self.assertIn(str(self.device / "ROMs"), plan["roots"])
        self.assertEqual(list(self.library.iterdir()), [])


class SshSnapshotTest(SnapshotTest):
    def run_over(self, prefix, *argv):
        backend = snapshot.Ssh(LABEL, "Wake the fake device.", prefix)
        with mock.patch.object(snapshot, "backend_for", lambda device: backend):
            return self.run_cli(*argv)

    @unittest.skipUnless(GNU_STREAMS, "needs sha256sum --zero and tar --null -T -")
    def test_ssh_commands_match_local_backend(self):
        _, _, local = self.snapshot_ok()
        code, out, err = self.run_over(["env", "COPYFILE_DISABLE=1", "bash", "-c"], "--scope", "config")
        self.assertEqual((code, err), (0, ""))
        remote = json.loads((Path(json.loads(out)["directory"]) / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(remote["status"], "verified")
        self.assertEqual(remote["files"], local["files"])

    @unittest.skipUnless(GNU_STAT, "needs stat -c %s")
    def test_ssh_dry_run_matches_local_backend(self):
        local = self.run_cli("--scope", "full", "--dry-run")
        self.assertEqual(self.run_over(["bash", "-c"], "--scope", "full", "--dry-run"), local)

    def test_ssh_hash_and_archive_timeouts_are_bounded(self):
        backend = snapshot.Ssh(LABEL, "Wake the fake device.", ["ssh"])
        failed = subprocess.CompletedProcess([], 1, b"")
        with mock.patch.object(snapshot.subprocess, "run", return_value=failed) as run:
            self.assertRaises(snapshot.SnapshotError, backend.hashes, ["/x"])
            self.assertRaises(snapshot.SnapshotError, backend.archive, ["/x"], None)
        self.assertEqual([call.kwargs["timeout"] for call in run.call_args_list], [3600, 6 * 3600])

    def test_ssh_failure_names_step_and_hints_only(self):
        leak = f"echo {SECRET}; echo {SECRET} >&2; exit 1"
        code, out, err = self.run_over(["bash", "-c", leak, "ssh"], "--scope", "config")
        self.assertEqual((code, out), (1, ""))
        self.assertEqual(err, f"snapshot: read config failed on {LABEL}; check: Wake the fake device.\n")
        self.assertEqual(list(self.library.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
