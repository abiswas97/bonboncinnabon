import contextlib
import copy
import hashlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import checks  # noqa: E402

EXAMPLE = json.loads((PLUGIN / "profile.example.json").read_text(encoding="utf-8"))


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = checks.main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


def png(width, height):
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IEND", b"")


JFIF = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"


def jpeg(width, height, sof=0xC0):
    frame = bytes([0xFF, sof]) + struct.pack(">HBHHB", 11, 8, height, width, 1) + b"\x01\x11\x00"
    return b"\xff\xd8" + JFIF + frame + b"\xff\xd9"


def gif(width, height):
    return b"GIF89a" + struct.pack("<HH", width, height) + b"\x00\x00\x00;"


def webp(kind, payload):
    body = b"WEBP" + kind + struct.pack("<I", len(payload)) + payload
    return b"RIFF" + struct.pack("<I", len(body)) + body


def vp8(width, height):
    return webp(b"VP8 ", b"\x00\x00\x00\x9d\x01\x2a" + struct.pack("<HH", width, height))


def vp8l(width, height):
    return webp(b"VP8L", b"\x2f" + ((width - 1) | (height - 1) << 14).to_bytes(4, "little"))


def vp8x(width, height):
    return webp(b"VP8X", b"\x00" * 4 + (width - 1).to_bytes(3, "little") + (height - 1).to_bytes(3, "little"))


class TempTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)

    def write(self, relative, data=b"data"):
        path = self.dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path


class MountedTest(TempTest):
    def write_profile(self, root, volume):
        data = copy.deepcopy(EXAMPLE)
        data["libraries"]["main"].update(root=str(root), volume=str(volume))
        path = self.dir / "config" / "bonboncinnabon" / "gaming" / "profile.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_root_and_volume(self):
        code, out, _ = run("mounted", "--root", self.dir, "--volume", "/")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"root": str(self.dir), "root_exists": True,
                                           "volume": "/", "volume_mounted": True})
        self.assertEqual(run("mounted", "--root", self.dir)[0], 0)

    def test_missing_root_or_unmounted_volume_fails(self):
        code, out, err = run("mounted", "--root", self.dir / "absent", "--volume", self.dir)
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out)["root_exists"])
        self.assertIn("checks: library root not found", err)
        self.assertIn("volume not mounted", err)

    def test_library_reads_profile(self):
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.dir / "config")}):
            code, _, err = run("mounted", "--library", "main")
            self.assertEqual(code, 2)
            self.assertIn("No gaming profile", err)
            self.write_profile(self.dir, "/")
            code, out, _ = run("mounted", "--library", "main")
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["root"], str(self.dir))
            code, _, err = run("mounted", "--library", "other")
            self.assertEqual(code, 1)
            self.assertIn("unknown library other", err)


class CollisionsTest(TempTest):
    def setUp(self):
        super().setUp()
        self.staging, self.root = self.dir / "staging", self.dir / "root"
        self.root.mkdir()

    def test_statuses_and_case_collision_with_destination(self):
        self.write("staging/ROMs/gba/New.gba", b"new")
        self.write("staging/ROMs/gba/Same.gba", b"same")
        self.write("staging/ROMs/gba/Conflict.gba", b"staged")
        self.write("staging/ROMs/gba/game.gba", b"case")
        self.write("staging/ROMs/gba/.DS_Store")
        self.write("staging/ROMs/gba/._New.gba")
        self.write("root/ROMs/gba/Same.gba", b"same")
        self.write("root/ROMs/gba/Conflict.gba", b"library")
        self.write("root/ROMs/gba/Game.gba", b"case")
        code, out, err = run("collisions", self.staging, self.root)
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertEqual({p["path"]: p["status"] for p in report["paths"]}, {
            "ROMs/gba/Conflict.gba": "conflict", "ROMs/gba/New.gba": "new",
            "ROMs/gba/Same.gba": "same", "ROMs/gba/game.gba": "case-collision"})
        collision = next(p for p in report["paths"] if p["status"] == "case-collision")
        self.assertEqual(collision["existing"], "ROMs/gba/Game.gba")
        self.assertEqual(report["summary"], {"conflict": 1, "new": 1, "same": 1, "case-collision": 1})
        self.assertIn("2 conflict or case-collision", err)
        self.assertFalse((self.root / "ROMs/gba/New.gba").exists())

    def test_new_and_same_pass(self):
        self.write("staging/BIOS/bios.bin", b"same")
        self.write("staging/Docs/Manual.pdf", b"new")
        self.write("root/BIOS/bios.bin", b"same")
        self.assertEqual(run("collisions", self.staging, self.root)[0], 0)

    def test_staging_paths_that_collide_when_casefolded(self):
        # Staging may sit on a case-sensitive disk, so fake the walk.
        staged = ["ROMs/GBA/Game.gba", "ROMs/gba/game.gba", "ROMs/gba/Other.gba"]
        with mock.patch.object(checks, "_staged", return_value=staged):
            self.staging.mkdir()
            code, out, _ = run("collisions", self.staging, self.root)
        self.assertEqual(code, 1)
        paths = {p["path"]: p for p in json.loads(out)["paths"]}
        self.assertEqual(paths["ROMs/GBA/Game.gba"]["collides_with"], ["ROMs/gba/game.gba"])
        self.assertEqual(paths["ROMs/gba/game.gba"]["status"], "case-collision")
        self.assertEqual(paths["ROMs/gba/Other.gba"]["status"], "new")

    def test_missing_destination_root_is_an_error(self):
        self.staging.mkdir()
        code, _, err = run("collisions", self.staging, self.dir / "unmounted")
        self.assertEqual(code, 1)
        self.assertIn("not a directory", err)


class ImagesTest(TempTest):
    def test_valid_headers_report_dimensions(self):
        fixtures = {"a.png": png(640, 480), "b.jpg": jpeg(320, 240), "c.jpg": jpeg(12, 34, sof=0xC2),
                    "d.gif": gif(16, 8), "e.webp": vp8(300, 200), "f.webp": vp8l(1024, 768),
                    "g.webp": vp8x(5000, 3000), "h.png": png(2, 3) + b"\x00\x00\x02"}
        paths = [self.write(name, data) for name, data in fixtures.items()]
        code, out, _ = run("images", *paths)
        self.assertEqual(code, 0)
        found = [(Path(i["file"]).name, i["format"], i["width"], i["height"]) for i in json.loads(out)["images"]]
        self.assertEqual(found, [("a.png", "png", 640, 480), ("b.jpg", "jpeg", 320, 240),
                                 ("c.jpg", "jpeg", 12, 34), ("d.gif", "gif", 16, 8),
                                 ("e.webp", "webp", 300, 200), ("f.webp", "webp", 1024, 768),
                                 ("g.webp", "webp", 5000, 3000), ("h.png", "png", 2, 3)])

    def test_unknown_truncated_and_zero_size_fail(self):
        no_frame = b"\xff\xd8" + JFIF + b"\xff\xd9"
        cases = {"short.png": (png(1, 1)[:20], "no IHDR"), "cut.png": (png(1, 1)[:-4], "no IEND"),
                 "noframe.jpg": (no_frame, "no frame header"), "cut.jpg": (jpeg(1, 1)[:-2], "no end marker"),
                 "cut.gif": (gif(1, 1)[:8], "truncated GIF header"), "cut.webp": (vp8(1, 1)[:-3], "RIFF size"),
                 "zero.png": (png(0, 10), "zero-size"), "text.png": (b"plain text", "unknown"),
                 "empty.gif": (b"", "empty")}
        paths = [self.write(name, data) for name, (data, _) in cases.items()]
        code, out, err = run("images", *paths, self.write("ok.gif", gif(2, 2)))
        self.assertEqual(code, 1)
        errors = {Path(i["file"]).name: i.get("error") for i in json.loads(out)["images"]}
        for name, (_, message) in cases.items():
            self.assertIn(message, errors[name], name)
        self.assertIsNone(errors["ok.gif"])
        self.assertIn(f"{len(cases)} of {len(cases) + 1} image(s) failed", err)


class ManifestTest(TempTest):
    def manifest(self, extra):
        good = self.write("ROMs/gba/Good.gba", b"good")
        data = {
            "files": [
                {"file": "ROMs/gba/Good.gba", "bytes": 4, "sha256": hashlib.sha256(b"good").hexdigest().upper()},
                {"file": "ROMs/gba/Hashless.gba", "bytes": 3},
                {"kind": "note without a file"},
                *extra,
            ],
            "additions": [{"file": str(good), "bytes": 4, "date": "2026-01-01"}, {"summary": {}}],
            "collections": {"desired": [{"name": "favourites", "order": "alpha",
                                         "members": ["ROMs/gba/Good.gba", "ROMs/gba/Gone.gba"]}]},
        }
        self.write("ROMs/gba/Hashless.gba", b"abc")
        (self.dir / "library-manifest.json").write_text(json.dumps(data), encoding="utf-8")

    def test_valid_manifest_with_missing_collection_member_warns(self):
        self.manifest([])
        code, out, _ = run("manifest", self.dir, "--hash")
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual((report["checked"], report["problems"]), (3, []))
        self.assertEqual(report["warnings"], [{"collection": "favourites", "member": "ROMs/gba/Gone.gba",
                                               "warning": "missing"}])

    def test_filesystem_metadata_entries_warn_instead_of_failing(self):
        self.manifest([{"file": "Frontends/ES-DE/Device/Current/._gamelist.xml", "bytes": 4096}])
        code, out, _ = run("manifest", self.dir)
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual(report["checked"], 3)
        self.assertIn({"entry": "/files/3", "file": "Frontends/ES-DE/Device/Current/._gamelist.xml",
                       "warning": "filesystem metadata entry; not checked"}, report["warnings"])

    def test_missing_files_and_wrong_sizes_fail(self):
        self.write("ROMs/gb/Short.gb", b"12")
        self.manifest([{"file": "ROMs/gb/Absent.gb"}, {"file": "ROMs/gb/Short.gb", "bytes": 3}])
        code, out, err = run("manifest", self.dir)
        self.assertEqual(code, 1)
        problems = json.loads(out)["problems"]
        self.assertEqual([(p["entry"], p["problem"]) for p in problems], [
            ("/files/3", "missing"), ("/files/4", "size 2 differs from recorded 3")])
        self.assertIn("2 of 5 manifest entries failed", err)

    def test_hash_flag_checks_sha256(self):
        self.write("ROMs/gb/Changed.gb", b"xyz")
        self.manifest([{"file": "ROMs/gb/Changed.gb", "bytes": 3, "sha256": hashlib.sha256(b"abc").hexdigest()}])
        self.assertEqual(run("manifest", self.dir)[0], 0)
        code, out, _ = run("manifest", self.dir, "--hash")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["problems"][0]["problem"], "sha256 differs from recorded")

    def test_missing_manifest_is_an_error(self):
        code, _, err = run("manifest", self.dir)
        self.assertEqual(code, 1)
        self.assertIn("checks: ", err)


class ManifestPreservedTest(TempTest):
    OLD = {"version": 1,
           "files": [{"file": "ROMs/gba/A.gba", "bytes": 1, "sha256": "aa"}, {"file": "ROMs/gba/B.gba", "bytes": 2}],
           "additions": [{"file": "BIOS/x.bin", "bytes": 3, "date": "2026-01-01"}],
           "collections": {"desired": [{"name": "cozy", "members": ["ROMs/gba/A.gba"]}]},
           "backup_verification": {"status": "verified", "runs": [{"date": "2026-01-01"}]}}

    def compare(self, new, *flags):
        old_path = self.write("old.json", json.dumps(self.OLD).encode())
        new_path = self.write("new.json", json.dumps(new).encode())
        code, out, err = run("manifest-preserved", old_path, new_path, *flags)
        return code, json.loads(out), err

    def test_reordered_superset_passes_and_lists_additions(self):
        new = copy.deepcopy(self.OLD)
        new["files"] = [dict(reversed(entry.items())) for entry in reversed(new["files"])]
        new["files"].append({"file": "ROMs/gba/C.gba", "bytes": 4})
        new["generated"] = "2026-10-09"
        code, report, err = self.compare(new)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual((report["missing_keys"], report["missing_entries"], report["moved"]), ([], [], []))
        self.assertEqual(report["added"], [{"entry": "/files/2", "file": "ROMs/gba/C.gba"}])

    def test_lost_key_or_changed_entry_fails(self):
        new = copy.deepcopy(self.OLD)
        del new["collections"]
        new["files"][1]["bytes"] = 20
        code, report, err = self.compare(new)
        self.assertEqual(code, 1)
        self.assertEqual(report["missing_keys"], ["collections"])
        self.assertEqual(report["missing_entries"], [{"entry": "/files/1", "file": "ROMs/gba/B.gba"}])
        self.assertEqual(report["added"], [{"entry": "/files/1", "file": "ROMs/gba/B.gba"}])
        self.assertIn("checks: 1 top-level key(s), 1 entries and 0 nested history value(s) of OLD missing or changed in NEW", err)

    def test_moved_path_needs_flag_and_may_change_only_file(self):
        new = copy.deepcopy(self.OLD)
        new["files"][0]["file"] = "ROMs/gba/Renamed.gba"
        code, report, _ = self.compare(new)
        self.assertEqual((code, report["missing_entries"]), (1, [{"entry": "/files/0", "file": "ROMs/gba/A.gba"}]))
        code, report, err = self.compare(new, "--moved", "ROMs/gba/A.gba=ROMs/gba/Renamed.gba")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(report["moved"], [{"entry": "/files/0", "file": "ROMs/gba/A.gba",
                                            "to": "ROMs/gba/Renamed.gba"}])
        self.assertEqual(report["added"], [])
        new["files"][0]["sha256"] = "bb"
        code, report, _ = self.compare(new, "--moved", "ROMs/gba/A.gba=ROMs/gba/Renamed.gba")
        self.assertEqual((code, report["moved"]), (1, []))
        self.assertEqual(report["missing_entries"], [{"entry": "/files/0", "file": "ROMs/gba/A.gba"}])

    def test_updated_path_may_change_other_fields_only_when_named(self):
        new = copy.deepcopy(self.OLD)
        new["files"][0]["sha256"] = "bb"
        code, report, _ = self.compare(new)
        self.assertEqual((code, report["missing_entries"]), (1, [{"entry": "/files/0", "file": "ROMs/gba/A.gba"}]))
        code, report, err = self.compare(new, "--updated", "ROMs/gba/A.gba")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(report["updated"], [{"entry": "/files/0", "file": "ROMs/gba/A.gba"}])
        del new["files"][0]
        code, report, _ = self.compare(new, "--updated", "ROMs/gba/A.gba")
        self.assertEqual(code, 1)


    def test_nested_history_is_kept_unless_named(self):
        new = copy.deepcopy(self.OLD)
        new["backup_verification"]["runs"].append({"date": "2026-10-09"})
        new["collections"]["desired"][0]["members"].append("ROMs/gba/B.gba")
        code, report, _ = self.compare(new)
        self.assertEqual((code, report["history_changes"]), (0, []))
        new["backup_verification"]["status"] = "pending"
        new["backup_verification"]["runs"] = []
        new["collections"]["desired"][0]["members"] = ["ROMs/gba/B.gba"]
        new["version"] = 2
        code, report, _ = self.compare(new)
        self.assertEqual(code, 1)
        self.assertEqual({c["path"] for c in report["history_changes"]}, {
            "/backup_verification/status", "/backup_verification/runs", "/backup_verification/runs/0",
            "/backup_verification/runs/0/date", "/collections/desired/0/members/0", "/version"})
        code, report, _ = self.compare(new, "--updated", "/backup_verification", "--updated", "/collections",
                                       "--updated", "/version")
        self.assertEqual((code, report["history_changes"]), (0, []))


    def test_type_changes_are_reported_and_root_allowance_refused(self):
        new = copy.deepcopy(self.OLD)
        new["backup_verification"]["runs"] = {"replaced": True}
        new["collections"]["desired"][0] = "flattened"
        code, report, _ = self.compare(new)
        self.assertEqual(code, 1)
        changes = {c["path"]: c["change"] for c in report["history_changes"]}
        self.assertEqual(changes["/backup_verification/runs"], "list became key")
        self.assertEqual(changes["/collections/desired/0"], "key became value")
        old_path = self.write("old.json", json.dumps(self.OLD).encode())
        code, _, err = run("manifest-preserved", old_path, old_path, "--updated", "/")
        self.assertEqual(code, 1)
        self.assertIn("would skip every check", err)


class DeviceHashesTest(TempTest):
    def setUp(self):
        super().setUp()
        data = copy.deepcopy(EXAMPLE)
        data["devices"]["here"] = {"label": "Here", "connect": {"method": "local"}}
        path = self.dir / "config" / "bonboncinnabon" / "gaming" / "profile.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        patcher = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.dir / "config")})
        patcher.start()
        self.addCleanup(patcher.stop)

    def check(self, pairs, device="here"):
        mapping = self.write("map.json", json.dumps({str(k): str(v) for k, v in pairs.items()}).encode())
        return run("device-hashes", "--device", device, "--map", mapping)

    def test_reports_matches_mismatches_and_missing_without_contents(self):
        pairs = {self.write("device/same.sav", b"SECRET-SAME"): self.write("local/same.sav", b"SECRET-SAME"),
                 self.write("device/diff.sav", b"SECRET-DEVICE"): self.write("local/diff.sav", b"SECRET-LOCAL"),
                 self.dir / "device/absent.sav": self.write("local/only.sav", b"SECRET-ONLY"),
                 self.write("device/only.sav", b"SECRET-ONLY"): self.dir / "local/absent.sav"}
        with mock.patch.object(checks.snapshot, "backend_for", wraps=checks.snapshot.backend_for) as backend:
            code, out, err = self.check(pairs)
        self.assertEqual(backend.call_args.args[0]["label"], "Here")
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertEqual(report["summary"], {"match": 1, "mismatch": 1, "missing": 2})
        self.assertEqual([(p["device_path"], p["status"], p.get("missing")) for p in report["paths"]], [
            (str(self.dir / "device/same.sav"), "match", None), (str(self.dir / "device/diff.sav"), "mismatch", None),
            (str(self.dir / "device/absent.sav"), "missing", ["device"]),
            (str(self.dir / "device/only.sav"), "missing", ["local"])])
        self.assertIn("checks: 1 mismatched and 2 missing of 4 path(s)", err)
        self.assertNotIn("SECRET", out + err)

    def test_all_matching_passes_and_bad_input_fails(self):
        device, local = self.write("device/a.sav", b"a"), self.write("local/a.sav", b"a")
        code, out, err = self.check({device: local})
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(json.loads(out)["summary"], {"match": 1, "mismatch": 0, "missing": 0})
        code, _, err = self.check({device: local}, device="nope")
        self.assertEqual(code, 1)
        self.assertIn("unknown device nope", err)
        code, _, err = self.check({"device/a.sav": local})
        self.assertEqual(code, 1)
        self.assertIn("absolute device paths", err)


if __name__ == "__main__":
    unittest.main()
