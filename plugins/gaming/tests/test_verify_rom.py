import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))

import verify_rom  # noqa: E402

ROM = b"synthetic rom bytes " * 64
OTHER = b"another synthetic rom " * 32


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = verify_rom.main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


def hashes(data):
    return {"crc": f"{zlib.crc32(data):08X}", "md5": hashlib.md5(data).hexdigest().upper(),
            "sha1": hashlib.sha1(data).hexdigest().upper(), "size": len(data)}


class VerifyRomTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)

    def write(self, name, data):
        path = self.dir / name
        path.write_bytes(data) if isinstance(data, bytes) else path.write_text(data, encoding="utf-8")
        return path

    def logiqx(self, body):
        return self.write("set.dat", f'<?xml version="1.0"?>\n<datafile>{body}</datafile>\n')

    def test_logiqx_sha1_match_is_case_insensitive(self):
        h = hashes(ROM)
        dat = self.logiqx(f'<game name="Example Game"><rom name="Example.gba" size="{h["size"]}" '
                          f'crc="{h["crc"]}" md5="{h["md5"]}" sha1="{h["sha1"]}" sha256="ignored"/></game>')
        code, out, _ = run(self.write("a.gba", ROM), "--dat", dat)
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertIn("achievement-hash", report["note"])
        result = report["files"][0]
        self.assertEqual(result["sha1"], hashlib.sha1(ROM).hexdigest())
        self.assertEqual(result["sha256"], hashlib.sha256(ROM).hexdigest())
        self.assertEqual(result["size"], len(ROM))
        self.assertEqual(result["matches"], [{"dat": str(dat), "game": "Example Game",
                                              "rom": "Example.gba", "matched_on": "sha1"}])

    def test_logiqx_machine_falls_back_to_crc_and_size(self):
        h = hashes(ROM)
        dat = self.logiqx(f'<machine name="Board"><rom name="chip.bin" size="{h["size"]}" crc="{h["crc"]}"/>'
                          f'<rom name="wrong-size.bin" size="1" crc="{h["crc"]}"/></machine>')
        code, out, _ = run(self.write("chip.bin", ROM), "--dat", dat)
        self.assertEqual(code, 0)
        matches = json.loads(out)["files"][0]["matches"]
        self.assertEqual([(m["rom"], m["matched_on"]) for m in matches], [("chip.bin", "crc32+size")])

    def test_sha1_in_dat_wins_over_matching_crc(self):
        h = hashes(ROM)
        dat = self.logiqx(f'<game name="G"><rom name="r" size="{h["size"]}" crc="{h["crc"]}" '
                          f'sha1="{"0" * 40}"/></game>')
        code, _, err = run(self.write("a.gba", ROM), "--dat", dat)
        self.assertEqual(code, 1)
        self.assertIn("no DAT match", err)

    def test_clrmamepro_md5_match_across_two_dats(self):
        h = hashes(ROM)
        clr = self.write("set.txt", 'clrmamepro (\n\tname "Synthetic"\n)\n\n'
                                    'game (\n\tname "Clr Game"\n\tdescription "Clr Game (v1)"\n'
                                    f'\trom ( name "Clr Rom.sfc" size {h["size"]} crc {h["crc"]} md5 {h["md5"]} )\n)\n')
        other = self.logiqx('<game name="Unrelated"><rom name="x" size="1" crc="00000000" sha1="'
                            + "1" * 40 + '"/></game>')
        code, out, _ = run(self.write("a.sfc", ROM), "--dat", other, "--dat", clr)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["files"][0]["matches"],
                         [{"dat": str(clr), "game": "Clr Game", "rom": "Clr Rom.sfc", "matched_on": "md5"}])

    def test_unmatched_file_fails(self):
        dat = self.logiqx(f'<game name="G"><rom name="r" sha1="{hashes(ROM)["sha1"]}"/></game>')
        code, out, err = run(self.write("a.gba", ROM), self.write("b.gba", OTHER), "--dat", dat)
        self.assertEqual(code, 1)
        files = json.loads(out)["files"]
        self.assertEqual([bool(f["matches"]) for f in files], [True, False])
        self.assertIn("b.gba: no DAT match", err)

    def test_zip_members_are_verified_instead_of_zip(self):
        dat = self.logiqx(f'<game name="G1"><rom name="one" sha1="{hashes(ROM)["sha1"]}"/></game>'
                          f'<game name="G2"><rom name="two" sha1="{hashes(OTHER)["sha1"]}"/></game>')
        archive = self.dir / "pack.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("folder/", b"")
            zf.writestr("folder/one.gba", ROM)
            zf.writestr("two.gba", OTHER)
        code, out, _ = run(archive, "--dat", dat)
        self.assertEqual(code, 0)
        files = json.loads(out)["files"]
        self.assertEqual([(f["member"], f["matches"][0]["game"]) for f in files],
                         [("folder/one.gba", "G1"), ("two.gba", "G2")])
        self.assertTrue(all(f["file"] == str(archive) for f in files))

    def test_corrupted_zip_fails(self):
        dat = self.logiqx(f'<game name="G"><rom name="one" sha1="{hashes(ROM)["sha1"]}"/></game>')
        archive = self.dir / "bad.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_STORED) as zf:
            zf.writestr("one.gba", ROM)
        data = bytearray(archive.read_bytes())
        data[data.find(ROM) + 10] ^= 0xFF
        archive.write_bytes(bytes(data))
        code, out, err = run(archive, "--dat", dat)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["files"], [{"file": str(archive), "error": "bad zip member one.gba"}])
        self.assertIn("verify_rom: ", err)

    def test_not_a_zip_fails(self):
        dat = self.logiqx(f'<game name="G"><rom name="one" sha1="{hashes(ROM)["sha1"]}"/></game>')
        code, out, _ = run(self.write("fake.zip", ROM), "--dat", dat)
        self.assertEqual(code, 1)
        self.assertIn("error", json.loads(out)["files"][0])

    def test_unsupported_archive_exits_3(self):
        dat = self.logiqx('<game name="G"><rom name="r" size="1" crc="00000000"/></game>')
        for name in ("pack.7z", "pack.RAR"):
            code, out, err = run(self.write(name, b"archive"), "--dat", dat)
            self.assertEqual(code, 3)
            self.assertEqual(out, "")
            self.assertIn(f"{name}: unsupported archive; extract first", err)

    def test_dat_without_roms_is_an_error(self):
        code, _, err = run(self.write("a.gba", ROM), "--dat", self.write("empty.dat", "not a dat"))
        self.assertEqual(code, 1)
        self.assertIn("no ROM entries", err)


    def test_without_dat_hashes_and_tests_archives_only(self):
        good = self.write("homebrew.gba", ROM)
        code, out, err = run(good)
        self.assertEqual((code, err), (0, ""))
        report = json.loads(out)
        self.assertIn("identity is unverified", report["note"])
        self.assertEqual(report["files"][0]["sha256"], hashlib.sha256(ROM).hexdigest())
        self.assertEqual(report["files"][0]["matches"], [])
        code, out, _ = run(self.write("fake.zip", ROM))
        self.assertEqual(code, 1)
        self.assertIn("error", json.loads(out)["files"][0])


if __name__ == "__main__":
    unittest.main()
