#!/usr/bin/env python3
"""Plan or copy a local game-library tree, preserving conflicts and checking bytes.

Every source file is hashed (SHA-256 and MD5) and compared with the destination:
reused when the hashes match, copy when the destination file is absent, and
conflict when it differs. Without --apply only EVIDENCE is written. With --apply,
files are copied through a sibling .sync-part file, verified, and moved into
place with os.replace. A conflict stops the run unless --preserve-conflicts is
given; the old destination file is then first copied to
<recovery root>/<UTC stamp>/<relative path>. The recovery root defaults to
DESTINATION/Recovery/Previous Cloud Files and must lie outside SOURCE.
Nothing is ever deleted, and the evidence never claims cloud presence.

Usage:
  sync_tree.py SOURCE DESTINATION EVIDENCE [--apply] [--preserve-conflicts]
               [--recovery-root PATH] [--exclude NAME]...
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CHUNK = 8 * 1024 * 1024
PROGRESS_SECONDS = 30
PARTIAL = ".sync-part"
UNFINISHED = (".incomplete", ".onboard-part", PARTIAL)
RECOVERY = Path("Recovery", "Previous Cloud Files")


class SyncError(Exception):
    pass


def digest(path):
    """Return the SHA-256 and MD5 hex digests of a file, reading it once."""
    sha, md5 = hashlib.sha256(), hashlib.md5(usedforsecurity=False)
    with path.open("rb") as file:
        while block := file.read(CHUNK):
            sha.update(block)
            md5.update(block)
    return sha.hexdigest(), md5.hexdigest()


def is_metadata(name):
    return name == ".DS_Store" or name.startswith("._")


def is_unfinished(name):
    return name.endswith(UNFINISHED) or (name.startswith(".") and name.endswith(".lock"))


def inventory(root, skip=()):
    """Return (files, excluded) relative to root, refusing anything unsafe to copy.

    skip names top-level entries of root that are left out entirely.
    """
    files, excluded = [], []
    for base, dirs, names in os.walk(root):
        base = Path(base)
        if base == root:
            dirs[:] = [name for name in dirs if name not in skip]
            names = [name for name in names if name not in skip]
        dirs.sort()
        names.sort()
        for name in dirs:
            if (base / name).is_symlink():
                relative = (base / name).relative_to(root)
                raise SyncError(f"directory symlink requires explicit preservation policy: {relative}")
        for name in names:
            path = base / name
            relative = path.relative_to(root)
            if is_metadata(name):
                excluded.append(str(relative))
            elif path.is_symlink() or not path.is_file():
                raise SyncError(f"non-regular file requires explicit preservation policy: {relative}")
            elif is_unfinished(name):
                raise SyncError(f"unfinished operation in source tree: {relative}")
            else:
                files.append(relative)
    return files, excluded


def inside(path, root):
    return path == root or root in path.parents


def check_roots(source, destination, evidence, recovery_root, skip=()):
    if not source.is_dir():
        raise SyncError(f"source missing: {source}")
    if inside(destination, source) or inside(source, destination):
        raise SyncError("overlapping roots")
    skipped = [source / name for name in skip]

    def in_source(path):
        return inside(path, source) and not any(inside(path, folder) for folder in skipped)

    if in_source(evidence) or inside(evidence, destination):
        raise SyncError("evidence must be outside synchronized roots")
    if in_source(recovery_root):
        raise SyncError("recovery root must be outside source")


def read_source(path, relative):
    """Hash a source file, refusing it if its size or mtime moved during the read."""
    before = path.stat()
    sha, md5 = digest(path)
    after = path.stat()
    if (after.st_size, after.st_mtime_ns) != (before.st_size, before.st_mtime_ns):
        raise SyncError(f"source changed while reading {relative}")
    return {"relative": str(relative), "bytes": before.st_size, "source_mtime_ns": before.st_mtime_ns,
            "sha256": sha, "md5": md5}


def destination_sha(path, relative):
    if path.exists() and not path.is_file():
        raise SyncError(f"destination type collision: {relative}")
    return digest(path)[0] if path.is_file() else None


def classify(sha, old_sha):
    if old_sha == sha:
        return "reused"
    return "copy" if old_sha is None else "conflict"


def preserve(target, recovery, old_sha):
    recovery.parent.mkdir(parents=True, exist_ok=True)
    if recovery.exists():
        raise SyncError(f"recovery collision: {recovery}")
    shutil.copyfile(target, recovery)
    if digest(recovery)[0] != old_sha:
        raise SyncError(f"recovery checksum mismatch: {recovery}")


def transfer(src, dst, sha, old_sha, relative):
    """Copy through a sibling partial file, then replace atomically. Partials survive failures."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    temp = dst.with_name(dst.name + PARTIAL)
    if temp.exists():
        raise SyncError(f"partial collision retained: {temp}")
    shutil.copyfile(src, temp)
    if digest(temp)[0] != sha:
        raise SyncError(f"transfer checksum mismatch: {relative}")
    if dst.is_file() and digest(dst)[0] != old_sha:
        raise SyncError(f"destination changed during transfer: {relative}")
    os.replace(temp, dst)


def apply_file(src, dst, row, old_sha, recovery):
    """Bring one destination file in line with its source; return the recovery path used, if any.

    recovery is None unless conflicts may be preserved.
    """
    relative = row["relative"]
    if row["action"] != "conflict":
        recovery = None
    elif recovery is None:
        raise SyncError(f"different destination retained; resolve ownership: {relative}")
    else:
        preserve(dst, recovery, old_sha)
    if row["action"] != "reused":
        transfer(src, dst, row["sha256"], old_sha, relative)
    if digest(dst)[0] != row["sha256"]:
        raise SyncError(f"final destination checksum mismatch: {relative}")
    if digest(src)[0] != row["sha256"]:
        raise SyncError(f"source changed during copy: {relative}")
    return str(recovery) if recovery else None


def write_evidence(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def total_bytes(rows):
    return sum(row["bytes"] for row in rows)


def reverify(source, files, rows, skip=()):
    """Refuse if the source tree, or any file read earlier, changed during the run."""
    if inventory(source, skip)[0] != files:
        raise SyncError("source inventory changed")
    for row in rows:
        path = source / row["relative"]
        now = path.stat()
        if (now.st_size != row["bytes"] or now.st_mtime_ns != row["source_mtime_ns"]
                or digest(path)[0] != row["sha256"]):
            raise SyncError(f"previously read source changed during sync: {row['relative']}")


def sync(source, destination, evidence, apply=False, preserve_conflicts=False, recovery_root=None,
         exclude=()):
    source, destination, evidence = (Path(p).resolve() for p in (source, destination, evidence))
    recovery_root = Path(recovery_root).resolve() if recovery_root else destination / RECOVERY
    exclude = tuple(exclude)
    if any("/" in name or name in ("", ".", "..") for name in exclude):
        raise SyncError("--exclude takes a top-level name, not a path")
    check_roots(source, destination, evidence, recovery_root, exclude)
    files, excluded = inventory(source, exclude)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows = []
    last = time.monotonic()
    for relative in files:
        row = read_source(source / relative, relative)
        old_sha = destination_sha(destination / relative, relative)
        row["action"] = classify(row["sha256"], old_sha)
        row["recovery"] = None
        if apply:
            recovery = recovery_root / stamp / relative if preserve_conflicts else None
            row["recovery"] = apply_file(source / relative, destination / relative, row, old_sha, recovery)
        rows.append(row)
        if time.monotonic() - last > PROGRESS_SECONDS:
            write_evidence(evidence, {"status": "running", "source": str(source),
                                      "destination": str(destination), "files": rows})
            print(json.dumps({"verified_files": len(rows), "total_files": len(files),
                              "bytes_processed": total_bytes(rows)}), flush=True)
            last = time.monotonic()
    reverify(source, files, rows, exclude)
    result = {"status": "local-copy-verified" if apply else "plan", "source": str(source),
              "destination": str(destination), "files": rows, "excluded_filesystem_metadata": excluded,
              "cloud_presence_verified": False, "cloud_hashes_verified": False}
    if exclude:
        result["excluded_top_level"] = list(exclude)
    write_evidence(evidence, result)
    print(json.dumps({"status": result["status"], "files": len(rows), "bytes": total_bytes(rows),
                      "conflicts": sum(row["action"] == "conflict" for row in rows)}), flush=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("evidence")
    parser.add_argument("--apply", action="store_true", help="copy files; without it only EVIDENCE is written")
    parser.add_argument("--preserve-conflicts", action="store_true",
                        help="copy differing destination files to Recovery before replacing them")
    parser.add_argument("--recovery-root", metavar="PATH",
                        help="where preserved conflicts go; default DESTINATION/Recovery/Previous Cloud Files")
    parser.add_argument("--exclude", action="append", default=[], metavar="NAME",
                        help="leave out this top-level entry of SOURCE; EVIDENCE may live inside it")
    args = parser.parse_args(argv)
    try:
        sync(args.source, args.destination, args.evidence, args.apply, args.preserve_conflicts,
             args.recovery_root, args.exclude)
    except (SyncError, OSError) as error:
        print(f"sync_tree: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
