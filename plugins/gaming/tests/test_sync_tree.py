import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import sync_tree as st  # noqa: E402

STAMP = "20260102T030405Z"
RECOVERY = Path("Recovery", "Previous Cloud Files", STAMP)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def tree(root):
    """Every entry under root with its bytes and mtime, or None when root is absent."""
    if not root.exists():
        return None
    return {str(p.relative_to(root)): (p.read_bytes() if p.is_file() else None, p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*"))}


class SyncTreeTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        self.source = self.tmp / "source"
        self.dest = self.tmp / "dest"
        self.evidence = self.tmp / "evidence" / "sync.json"
        self.source.mkdir()
        clock = mock.patch.object(st, "datetime")
        clock.start().now.return_value = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        self.addCleanup(clock.stop)

    def sync(self, apply=False, preserve=False):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = st.sync(self.source, self.dest, self.evidence, apply, preserve)
        return result, [json.loads(line) for line in out.getvalue().splitlines()]

    def cli(self, *flags):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = st.main([str(self.source), str(self.dest), str(self.evidence), *flags])
        return code, out.getvalue(), err.getvalue()

    def refused(self, pattern, apply=False, preserve=False):
        with self.assertRaisesRegex(st.SyncError, pattern):
            self.sync(apply, preserve)

    def mixed(self, copy=True):
        """a.txt is absent at the destination, b.txt matches and sub/c.txt differs."""
        if copy:
            write(self.source / "a.txt", b"alpha")
        write(self.source / "b.txt", b"bravo")
        write(self.source / "sub/c.txt", b"charlie new")
        write(self.dest / "b.txt", b"bravo")
        write(self.dest / "sub/c.txt", b"charlie old")

    # T1

    def test_t1_skips_and_lists_filesystem_metadata(self):
        write(self.source / "a.txt", b"alpha")
        for name in (".DS_Store", "._a.txt", "sub/._b"):
            write(self.source / name, b"meta")
        result, _ = self.sync(apply=True)
        self.assertEqual(result["excluded_filesystem_metadata"], [".DS_Store", "._a.txt", "sub/._b"])
        self.assertEqual([row["relative"] for row in result["files"]], ["a.txt"])
        self.assertEqual(list(tree(self.dest)), ["a.txt"])

    # T2

    def test_t2_refuses_directory_symlink_before_copying(self):
        write(self.source / "a.txt", b"alpha")
        (self.tmp / "elsewhere").mkdir()
        os.symlink(self.tmp / "elsewhere", self.source / "linked", target_is_directory=True)
        self.refused("directory symlink requires explicit preservation policy: linked", apply=True)
        self.assertIsNone(tree(self.dest))
        self.assertFalse(self.evidence.exists())

    def test_t2_refuses_symlinked_and_non_regular_files_before_copying(self):
        makers = {"symlink": lambda path: os.symlink(path.parent / "a.txt", path), "fifo": os.mkfifo}
        for name, make in makers.items():
            with self.subTest(name):
                self.source = self.tmp / name
                write(self.source / "a.txt", b"alpha")
                make(self.source / "b")
                self.refused("non-regular file requires explicit preservation policy: b", apply=True)
                self.assertIsNone(tree(self.dest))

    def test_t2_refuses_unfinished_operation_markers_before_copying(self):
        markers = ("x.incomplete", "x.onboard-part", "x.sync-part", ".x.lock", "sub/.y.lock")
        for index, marker in enumerate(markers):
            with self.subTest(marker):
                self.source = self.tmp / f"marker-{index}"
                write(self.source / "a.txt", b"alpha")
                write(self.source / marker, b"partial")
                self.refused(f"unfinished operation in source tree: {marker}", apply=True)
                self.assertIsNone(tree(self.dest))
        self.source = self.tmp / "plain-lock"
        write(self.source / "x.lock", b"not a dot-file")
        result, _ = self.sync()
        self.assertEqual(result["files"][0]["relative"], "x.lock")

    # T3

    def test_t3_refuses_overlapping_roots(self):
        write(self.source / "a.txt", b"alpha")
        roots = {"same": self.source, "destination inside source": self.source / "inner",
                 "source inside destination": self.tmp}
        for name, dest in roots.items():
            with self.subTest(name):
                self.dest = dest
                self.refused("overlapping roots", apply=True)
        self.assertEqual(list(tree(self.source)), ["a.txt"])

    def test_t3_refuses_evidence_inside_either_root(self):
        write(self.source / "a.txt", b"alpha")
        for evidence in (self.source / "e.json", self.dest / "logs/e.json", self.source, self.dest):
            with self.subTest(str(evidence)):
                self.evidence = evidence
                self.refused("evidence must be outside synchronized roots", apply=True)
        self.assertIsNone(tree(self.dest))
        self.assertEqual(list(tree(self.source)), ["a.txt"])

    def test_cli_errors_go_to_stderr_without_traceback(self):
        self.dest = self.source
        self.assertEqual(self.cli("--apply"), (1, "", "sync_tree: overlapping roots\n"))
        self.source, self.dest = self.tmp / "missing", self.tmp / "dest"
        code, out, err = self.cli()
        self.assertEqual((code, out), (1, ""))
        self.assertEqual(err, f"sync_tree: source missing: {self.source}\n")

    # T4

    def test_t4_records_hashes_and_classifies_each_file(self):
        self.mixed()
        result, _ = self.sync()
        rows = {row["relative"]: row for row in result["files"]}
        self.assertEqual({name: row["action"] for name, row in rows.items()},
                         {"a.txt": "copy", "b.txt": "reused", "sub/c.txt": "conflict"})
        for name, row in rows.items():
            path = self.source / name
            data = path.read_bytes()
            self.assertEqual(row["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(row["md5"], hashlib.md5(data).hexdigest())
            self.assertEqual(row["bytes"], len(data))
            self.assertEqual(row["source_mtime_ns"], path.stat().st_mtime_ns)
            self.assertIsNone(row["recovery"])

    def test_t4_refuses_source_that_changes_while_read(self):
        source = write(self.source / "a.txt", b"alpha")
        real = st.digest

        def read_then_touch(path):
            digests = real(path)
            if path == source:
                os.utime(source, ns=(1, 1))
            return digests

        with mock.patch.object(st, "digest", side_effect=read_then_touch):
            self.refused("source changed while reading a.txt")
        self.assertFalse(self.evidence.exists())

    def test_t4_refuses_destination_type_collision(self):
        write(self.source / "a.txt", b"alpha")
        (self.dest / "a.txt").mkdir(parents=True)
        self.refused("destination type collision: a.txt", apply=True)

    # T5

    def test_t5_conflict_without_preserve_fails_with_path_and_keeps_destination(self):
        self.mixed(copy=False)
        before = tree(self.dest)
        code, out, err = self.cli("--apply")
        self.assertEqual((code, out), (1, ""))
        self.assertEqual(err, "sync_tree: different destination retained; resolve ownership: sub/c.txt\n")
        self.assertEqual(tree(self.dest), before)

    def test_t5_preserve_conflicts_keeps_verified_recovery_copy(self):
        self.mixed()
        result, _ = self.sync(apply=True, preserve=True)
        recovery = self.dest / RECOVERY / "sub/c.txt"
        self.assertEqual(recovery.read_bytes(), b"charlie old")
        self.assertEqual((self.dest / "sub/c.txt").read_bytes(), b"charlie new")
        recoveries = {row["relative"]: row["recovery"] for row in result["files"]}
        self.assertEqual(recoveries, {"a.txt": None, "b.txt": None, "sub/c.txt": str(recovery)})

    def test_t5_recovery_root_option_places_preserved_copies(self):
        self.mixed()
        elsewhere = self.tmp / "elsewhere"
        code, _, err = self.cli("--apply", "--preserve-conflicts", "--recovery-root", str(elsewhere))
        self.assertEqual((code, err), (0, ""))
        recovery = elsewhere / STAMP / "sub/c.txt"
        self.assertEqual(recovery.read_bytes(), b"charlie old")
        self.assertEqual((self.dest / "sub/c.txt").read_bytes(), b"charlie new")
        self.assertFalse((self.dest / "Recovery").exists())
        rows = {row["relative"]: row["recovery"] for row in json.loads(self.evidence.read_text())["files"]}
        self.assertEqual(rows["sub/c.txt"], str(recovery))

    def test_t5_refuses_recovery_root_inside_source(self):
        self.mixed()
        source_before, dest_before = tree(self.source), tree(self.dest)
        for root in (self.source, self.source / "sub" / "kept"):
            with self.subTest(str(root)):
                code, out, err = self.cli("--apply", "--preserve-conflicts", "--recovery-root", str(root))
                self.assertEqual((code, out), (1, ""))
                self.assertEqual(err, "sync_tree: recovery root must be outside source\n")
        self.assertEqual(tree(self.source), source_before)
        self.assertEqual(tree(self.dest), dest_before)
        self.assertFalse(self.evidence.exists())

    def test_t5_refuses_existing_recovery_path(self):
        self.mixed(copy=False)
        write(self.dest / RECOVERY / "sub/c.txt", b"earlier recovery")
        before = tree(self.dest)
        self.refused("recovery collision", apply=True, preserve=True)
        self.assertEqual(tree(self.dest), before)

    def test_t5_verifies_recovery_copy_hash(self):
        self.mixed(copy=False)
        real = shutil.copyfile

        def corrupt_recovery(src, dst):
            real(src, dst)
            if "Recovery" in Path(dst).parts:
                Path(dst).write_bytes(b"corrupt")

        with mock.patch.object(st.shutil, "copyfile", side_effect=corrupt_recovery):
            self.refused("recovery checksum mismatch", apply=True, preserve=True)
        self.assertEqual((self.dest / "sub/c.txt").read_bytes(), b"charlie old")

    # T6

    def test_t6_copies_through_sync_part_and_os_replace(self):
        self.mixed()
        with mock.patch.object(st.shutil, "copyfile", wraps=shutil.copyfile) as copy, \
                mock.patch.object(st.os, "replace", wraps=os.replace) as replace:
            result, _ = self.sync(apply=True, preserve=True)
        target, temp = self.dest / "a.txt", self.dest / "a.txt.sync-part"
        copy.assert_any_call(self.source / "a.txt", temp)
        replace.assert_any_call(temp, target)
        replace.assert_any_call(self.dest / "sub/c.txt.sync-part", self.dest / "sub/c.txt")
        self.assertEqual(replace.call_count, 2)
        self.assertEqual(target.read_bytes(), b"alpha")
        self.assertEqual(list(self.dest.rglob("*.sync-part")), [])
        self.assertEqual(result["status"], "local-copy-verified")

    def test_t6_refuses_existing_sync_part(self):
        write(self.source / "a.txt", b"alpha")
        write(self.dest / "a.txt.sync-part", b"earlier partial")
        before = tree(self.dest)
        self.refused("partial collision retained", apply=True)
        self.assertEqual(tree(self.dest), before)

    def test_t6_verifies_sync_part_hash_and_keeps_it(self):
        write(self.source / "a.txt", b"alpha")
        with mock.patch.object(st.shutil, "copyfile", side_effect=lambda src, dst: Path(dst).write_bytes(b"bad")):
            self.refused("transfer checksum mismatch: a.txt", apply=True)
        self.assertEqual(tree(self.dest)["a.txt.sync-part"][0], b"bad")
        self.assertFalse((self.dest / "a.txt").exists())

    def test_t6_refuses_destination_changed_during_transfer(self):
        write(self.source / "a.txt", b"alpha")
        real = shutil.copyfile

        def copy_while_another_writer_lands(src, dst):
            real(src, dst)
            write(self.dest / "a.txt", b"other writer")

        with mock.patch.object(st.shutil, "copyfile", side_effect=copy_while_another_writer_lands):
            self.refused("destination changed during transfer: a.txt", apply=True)
        self.assertEqual((self.dest / "a.txt").read_bytes(), b"other writer")
        self.assertEqual((self.dest / "a.txt.sync-part").read_bytes(), b"alpha")

    def test_t6_verifies_final_destination_hash(self):
        write(self.source / "a.txt", b"alpha")
        real = os.replace

        def replace_then_corrupt(temp, target):
            real(temp, target)
            Path(target).write_bytes(b"corrupt")

        with mock.patch.object(st.os, "replace", side_effect=replace_then_corrupt):
            self.refused("final destination checksum mismatch: a.txt", apply=True)

    def test_t6_refuses_source_changed_mid_copy(self):
        source = write(self.source / "a.txt", b"alpha")
        real = shutil.copyfile

        def copy_then_edit_source(src, dst):
            real(src, dst)
            source.write_bytes(b"edited mid-copy")

        with mock.patch.object(st.shutil, "copyfile", side_effect=copy_then_edit_source):
            self.refused("source changed during copy: a.txt", apply=True)
        self.assertFalse(self.evidence.exists())

    # T7

    def test_t7_progress_at_most_every_30_seconds(self):
        for name in ("a.txt", "b.txt", "c.txt"):
            write(self.source / name, b"12345")
        written = []
        real = st.write_evidence

        def record(path, data):
            real(path, data)
            written.append(json.loads(path.read_text()))

        # Start, then one reading per file; only 31 s exceeds the limit, and it resets the clock.
        ticks = [0, 30, 31, 31, 61]
        with mock.patch.object(st.time, "monotonic", side_effect=ticks), \
                mock.patch.object(st, "write_evidence", side_effect=record):
            _, lines = self.sync()
        self.assertEqual(lines, [{"verified_files": 2, "total_files": 3, "bytes_processed": 10},
                                 {"status": "plan", "files": 3, "bytes": 15, "conflicts": 0}])
        running = written[0]
        self.assertEqual(list(running), ["status", "source", "destination", "files"])
        self.assertEqual(running["status"], "running")
        self.assertEqual([row["relative"] for row in running["files"]], ["a.txt", "b.txt"])
        self.assertEqual(written[1]["status"], "plan")

    def test_t7_refuses_source_inventory_change(self):
        write(self.source / "a.txt", b"alpha")
        real = st.digest

        def digest_while_file_arrives(path):
            write(self.source / "late.txt", b"late")
            return real(path)

        with mock.patch.object(st, "digest", side_effect=digest_while_file_arrives):
            self.refused("source inventory changed")
        self.assertFalse(self.evidence.exists())

    def test_t7_reverifies_size_mtime_and_hash_of_every_source(self):
        edits = {"size": (b"alpha!", 0), "mtime": (b"alpha", 1), "hash": (b"ALPHA", 0)}
        real = st.digest
        for case, (content, mtime_offset) in edits.items():
            with self.subTest(case):
                self.source = self.tmp / case
                first = write(self.source / "a.txt", b"alpha")
                second = write(self.source / "b.txt", b"bravo")
                mtime = first.stat().st_mtime_ns

                def edit_first_after_reading_it(path):
                    if path == second:
                        first.write_bytes(content)
                        os.utime(first, ns=(mtime, mtime + mtime_offset))
                    return real(path)

                with mock.patch.object(st, "digest", side_effect=edit_first_after_reading_it):
                    self.refused("previously read source changed during sync: a.txt")

    # T8

    def test_t8_evidence_fields_and_final_summary_line(self):
        self.mixed()
        code, out, err = self.cli("--apply", "--preserve-conflicts")
        self.assertEqual((code, err), (0, ""))
        evidence = json.loads(self.evidence.read_text())
        self.assertEqual(list(evidence), ["status", "source", "destination", "files",
                                          "excluded_filesystem_metadata", "cloud_presence_verified",
                                          "cloud_hashes_verified"])
        self.assertEqual(evidence["status"], "local-copy-verified")
        self.assertEqual((evidence["source"], evidence["destination"]), (str(self.source), str(self.dest)))
        self.assertIs(evidence["cloud_presence_verified"], False)
        self.assertIs(evidence["cloud_hashes_verified"], False)
        for row in evidence["files"]:
            self.assertEqual(list(row), ["relative", "bytes", "source_mtime_ns", "sha256", "md5", "action",
                                         "recovery"])
        self.assertEqual(len(out.splitlines()), 1)
        self.assertEqual(json.loads(out), {"status": "local-copy-verified", "files": 3, "bytes": 21, "conflicts": 1})

    # T9

    def test_t9_plan_writes_only_evidence(self):
        self.mixed()
        source_before, dest_before = tree(self.source), tree(self.dest)
        code, out, _ = self.cli("--preserve-conflicts")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"status": "plan", "files": 3, "bytes": 21, "conflicts": 1})
        self.assertEqual(json.loads(self.evidence.read_text())["status"], "plan")
        self.assertEqual(tree(self.dest), dest_before)
        self.assertEqual(tree(self.source), source_before)
        self.dest = self.tmp / "absent"
        self.sync()
        self.assertFalse(self.dest.exists())

    # Never delete

    def test_apply_never_deletes_from_source_or_destination(self):
        self.mixed()
        write(self.dest / "only-in-destination.txt", b"keep")
        source_before = tree(self.source)
        deny = mock.Mock(side_effect=AssertionError("deletion attempted"))
        with contextlib.ExitStack() as stack:
            for module, name in ((os, "unlink"), (os, "remove"), (os, "rmdir"), (os, "removedirs"),
                                 (shutil, "rmtree")):
                stack.enter_context(mock.patch.object(module, name, deny))
            result, _ = self.sync(apply=True, preserve=True)
        deny.assert_not_called()
        self.assertEqual(result["status"], "local-copy-verified")
        self.assertEqual(tree(self.source), source_before)
        self.assertEqual((self.dest / "only-in-destination.txt").read_bytes(), b"keep")
        self.assertEqual((self.dest / RECOVERY / "sub/c.txt").read_bytes(), b"charlie old")


    def test_exclude_leaves_out_top_level_entry_and_may_hold_evidence(self):
        write(self.source / "library-manifest.json", b"{}")
        write(self.source / "ROMs/a.gba", b"rom")
        write(self.source / "Staging/run/work.incomplete", b"partial")
        self.evidence = self.source / "Staging" / "run" / "evidence.json"
        code, out, err = self.cli("--apply", "--exclude", "Staging")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(sorted(tree(self.dest)), ["ROMs", "ROMs/a.gba", "library-manifest.json"])
        evidence = json.loads(self.evidence.read_text())
        self.assertEqual(evidence["excluded_top_level"], ["Staging"])
        self.assertEqual(sorted(row["relative"] for row in evidence["files"]),
                         ["ROMs/a.gba", "library-manifest.json"])

    def test_exclude_does_not_excuse_evidence_elsewhere_in_source(self):
        write(self.source / "ROMs/a.gba", b"rom")
        self.evidence = self.source / "ROMs" / "evidence.json"
        code, _, err = self.cli("--exclude", "Staging")
        self.assertEqual(code, 1)
        self.assertIn("evidence must be outside synchronized roots", err)
        code, _, err = self.cli("--exclude", "ROMs/sub")
        self.assertEqual(code, 1)
        self.assertIn("top-level name", err)


    def test_only_syncs_listed_paths_and_refuses_unknown_ones(self):
        write(self.source / "new.gba", b"new")
        write(self.source / "big/untouched.iso", b"unchanged")
        write(self.dest / "big/untouched.iso", b"unchanged")
        listing = write(self.tmp / "delta.txt", b"new.gba\n")
        with mock.patch.object(st, "digest", wraps=st.digest) as spy:
            code, _, err = self.cli("--apply", "--only", str(listing))
        self.assertEqual((code, err), (0, ""))
        self.assertTrue((self.dest / "new.gba").is_file())
        self.assertNotIn(self.dest / "big/untouched.iso", [call.args[0] for call in spy.call_args_list])
        self.assertEqual(json.loads(self.evidence.read_text())["only_listed_paths"], 1)
        write(self.tmp / "delta.txt", b"missing.gba\n")
        code, _, err = self.cli("--only", str(listing))
        self.assertEqual(code, 1)
        self.assertIn("listed path not in source: missing.gba", err)


if __name__ == "__main__":
    unittest.main()
