#!/usr/bin/env python3
"""Read-only library checks. Each prints JSON and exits 1 when its check fails.

Nothing is created, changed or deleted.

Usage:
  checks.py mounted (--library ID | --root PATH [--volume PATH])
  checks.py collisions STAGING ROOT
  checks.py images FILE...
  checks.py manifest ROOT [--hash]
  checks.py manifest-preserved OLD NEW [--moved OLDPATH=NEWPATH]... [--updated PATH|/KEY/PATH]...
  checks.py device-hashes --device ID --map FILE
  checks.py delta SOURCE TARGET [--exclude NAME]... [--since YYYY-MM-DD] [--list FILE]

mounted     The library root exists and, when given, its volume is a mount point.
            --library reads root and volume from the gaming profile.
collisions  Each staged file is new, the same as its destination (equal SHA-256),
            a conflict, or a case-collision. Libraries often live on exFAT, which
            ignores case, so names that differ only by case are the same file.
images      PNG, JPEG, GIF and WebP files have a known header with non-zero
            dimensions. PNG, JPEG and WebP files must also reach their end
            marker or declared size; trailing padding is tolerated.
manifest    Entries in library-manifest.json `files` and `additions` exist, with
            recorded `bytes` and, with --hash, `sha256`. Paths are relative to
            ROOT unless absolute. Missing collection members are warnings.
manifest-preserved
            Every top-level key of manifest OLD is still in NEW, and every entry
            of OLD's `files` and `additions` is in NEW's same list, compared as
            canonical JSON. An entry may change only its `file`, and only as
            named by a --moved pair, or any other field when its `file` is named
            by --updated (a re-recorded size or hash). Every other top-level key
            keeps its nested history: no key removed, no list shortened, no value
            changed, unless --updated names that key path (starting with /).
            Entries new in NEW are listed as added.
device-hashes
            FILE is a JSON object {"<device path>": "<local path>"}. Each device
            file, read through snapshot.py's backend for the profile device,
            must have the same SHA-256 as its local file. Contents are never
            printed.
delta       Source files the target lacks, holds at a different size, or that
            changed since --since (local midnight). Only metadata is read at
            the target, so online-only cloud files are never downloaded.
            --list writes the paths for sync_tree.py --only.
"""

import argparse
import datetime
import hashlib
import json
import os
import struct
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gaming_profile  # noqa: E402
import snapshot  # noqa: E402

PROG = "checks"
MANIFEST = "library-manifest.json"
PNG = b"\x89PNG\r\n\x1a\n"
PNG_END = b"IEND\xaeB`\x82"
JPEG_SOF = set(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}
JPEG_STANDALONE = {0x01, *range(0xD0, 0xD8)}


class CheckError(Exception):
    pass


def sha256(path):
    with open(path, "rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


# mounted ---------------------------------------------------------------------

def mounted(args):
    root, volume = args.root, args.volume
    if args.library:
        library = gaming_profile.load().get("libraries", {}).get(args.library)
        if not isinstance(library, dict):
            raise CheckError(f"unknown library {args.library}")
        root, volume = library.get("root"), library.get("volume")
    report = {"root": root, "root_exists": bool(root) and os.path.isdir(root)}
    problems = [] if report["root_exists"] else [f"library root not found: {root}"]
    if volume:
        report.update(volume=volume, volume_mounted=os.path.ismount(volume))
        if not report["volume_mounted"]:
            problems.append(f"volume not mounted: {volume}")
    return report, "; ".join(problems)


# collisions ------------------------------------------------------------------

def _fold(name):
    return unicodedata.normalize("NFC", name).casefold()


def _is_metadata(name):
    return name == ".DS_Store" or name.startswith("._")


def _staged(staging):
    for folder, dirs, names in os.walk(staging):
        dirs.sort()
        for name in sorted(names):
            if not _is_metadata(name):
                yield os.path.relpath(os.path.join(folder, name), staging).replace(os.sep, "/")


def _existing(root, rel, listings):
    """Return how the destination actually spells rel, or None when nothing matches."""
    current, actual = root, []
    for part in rel.split("/"):
        if current not in listings:
            folded = {}
            try:
                for name in os.listdir(current):
                    folded.setdefault(_fold(name), []).append(name)
            except (FileNotFoundError, NotADirectoryError):
                pass
            listings[current] = folded
        names = listings[current].get(_fold(part))
        if not names:
            return None
        actual.append(part if part in names else names[0])
        current = os.path.join(current, actual[-1])
    return "/".join(actual)


def collisions(args):
    for path in (args.staging, args.root):
        if not os.path.isdir(path):
            raise CheckError(f"not a directory: {path}")
    paths = list(_staged(args.staging))
    groups = {}
    for rel in paths:
        groups.setdefault(_fold(rel), []).append(rel)
    listings, entries = {}, []
    for rel in paths:
        twins = [other for other in groups[_fold(rel)] if other != rel]
        existing = _existing(args.root, rel, listings)
        if twins:
            entry = {"path": rel, "status": "case-collision", "collides_with": twins}
        elif existing is None:
            entry = {"path": rel, "status": "new"}
        elif existing != rel:
            entry = {"path": rel, "status": "case-collision", "existing": existing}
        else:
            dest = os.path.join(args.root, rel)
            same = os.path.isfile(dest) and sha256(dest) == sha256(os.path.join(args.staging, rel))
            entry = {"path": rel, "status": "same" if same else "conflict"}
        entries.append(entry)
    summary = {}
    for entry in entries:
        summary[entry["status"]] = summary.get(entry["status"], 0) + 1
    bad = summary.get("conflict", 0) + summary.get("case-collision", 0)
    report = {"staging": args.staging, "root": args.root, "summary": summary, "paths": entries}
    return report, f"{bad} conflict or case-collision path(s)" if bad else None


# images ----------------------------------------------------------------------

def _png(data):
    if len(data) < 24 or data[12:16] != b"IHDR":
        raise CheckError("truncated PNG: no IHDR")
    if PNG_END not in data[33:]:
        raise CheckError("truncated PNG: no IEND")
    return struct.unpack(">II", data[16:24])


def _jpeg(data):
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            raise CheckError("corrupt JPEG: expected a marker")
        marker = data[pos + 1]
        if marker == 0xFF:
            pos += 1
            continue
        if marker in JPEG_STANDALONE:
            pos += 2
            continue
        if marker in (0xD9, 0xDA):
            break
        if marker in JPEG_SOF and pos + 9 <= len(data):
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            if data.rfind(b"\xff\xd9") < pos:
                raise CheckError("truncated JPEG: no end marker")
            return width, height
        pos += 2 + struct.unpack(">H", data[pos + 2:pos + 4])[0]
    raise CheckError("truncated JPEG: no frame header")


def _gif(data):
    # ponytail: header only; walk the blocks to the 0x3B trailer if cut-short GIFs turn up
    if len(data) < 10:
        raise CheckError("truncated GIF header")
    return struct.unpack("<HH", data[6:10])


def _webp(data):
    if len(data) < struct.unpack("<I", data[4:8])[0] + 8:
        raise CheckError("truncated WebP: shorter than its RIFF size")
    chunk = data[12:16]
    if chunk == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
        width, height = struct.unpack("<HH", data[26:30])
        return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X" and len(data) >= 30:
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    raise CheckError("truncated or unknown WebP header")


def image_size(data):
    """Return (format, width, height) or raise CheckError."""
    if data.startswith(PNG):
        kind, (width, height) = "png", _png(data)
    elif data.startswith(b"\xff\xd8"):
        kind, (width, height) = "jpeg", _jpeg(data)
    elif data[:6] in (b"GIF87a", b"GIF89a"):
        kind, (width, height) = "gif", _gif(data)
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind, (width, height) = "webp", _webp(data)
    else:
        raise CheckError("unknown image format" if data else "empty file")
    if not (width and height):
        raise CheckError(f"zero-size {kind} ({width}x{height})")
    return kind, width, height


def images(args):
    entries = []
    for path in args.files:
        try:
            with open(path, "rb") as file:
                kind, width, height = image_size(file.read())
            entries.append({"file": path, "format": kind, "width": width, "height": height})
        except (CheckError, OSError) as error:
            entries.append({"file": path, "error": str(error)})
    bad = sum("error" in entry for entry in entries)
    return {"images": entries}, f"{bad} of {len(entries)} image(s) failed" if bad else None


# manifest --------------------------------------------------------------------

def _entry_problem(root, entry, with_hash):
    path = os.path.join(root, entry["file"])  # an absolute file replaces root
    if not os.path.isfile(path):
        return "missing"
    if entry.get("bytes") is not None and os.path.getsize(path) != entry["bytes"]:
        return f"size {os.path.getsize(path)} differs from recorded {entry['bytes']}"
    if with_hash and entry.get("sha256") and sha256(path) != entry["sha256"].lower():
        return "sha256 differs from recorded"
    return None


def manifest(args):
    with open(os.path.join(args.root, MANIFEST), encoding="utf-8") as file:
        data = json.load(file)
    checked, problems, warnings = 0, [], []
    for section in ("files", "additions"):
        for position, entry in enumerate(data.get(section) or []):
            if not isinstance(entry, dict) or not isinstance(entry.get("file"), str):
                continue
            if _is_metadata(os.path.basename(entry["file"])):
                warnings.append({"entry": f"/{section}/{position}", "file": entry["file"],
                                 "warning": "filesystem metadata entry; not checked"})
                continue
            checked += 1
            problem = _entry_problem(args.root, entry, args.hash)
            if problem:
                problems.append({"entry": f"/{section}/{position}", "file": entry["file"], "problem": problem})
    for collection in (data.get("collections") or {}).get("desired") or []:
        for member in collection.get("members") or []:
            if not os.path.exists(os.path.join(args.root, member)):
                warnings.append({"collection": collection.get("name"), "member": member, "warning": "missing"})
    report = {"root": args.root, "checked": checked, "hashed": args.hash,
              "problems": problems, "warnings": warnings}
    return report, f"{len(problems)} of {checked} manifest entries failed" if problems else None


# manifest-preserved ----------------------------------------------------------

def _load_manifest(path):
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise CheckError(f"{path}: manifest must be a JSON object")
    return data


def _canonical(entry):
    return json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _file(entry):
    return entry["file"] if isinstance(entry, dict) and isinstance(entry.get("file"), str) else None


def _where(section, position, entry):
    return {"entry": f"/{section}/{position}", "file": _file(entry)}


def _move(text):
    old, sep, new = text.partition("=")
    if not (old and sep and new):
        raise argparse.ArgumentTypeError(f"expected OLDPATH=NEWPATH, got {text!r}")
    return old, new


def _shape(value, path=""):
    """Map each nested key path to ("key", None), ("list", length) or ("value", scalar)."""
    shape = {}
    if isinstance(value, dict):
        for key, child in value.items():
            here = f"{path}/{key}"
            shape[here] = ("key", None) if isinstance(child, (dict, list)) else ("value", child)
            shape.update(_shape(child, here))
    elif isinstance(value, list):
        shape[path] = ("list", len(value))
        for position, child in enumerate(value):
            if isinstance(child, (dict, list)):
                shape[f"{path}/{position}"] = ("key", None)
                shape.update(_shape(child, f"{path}/{position}"))
            else:
                shape[f"{path}/{position}"] = ("value", child)
    return shape


def _history_changes(old, new, allowed):
    """Nested history outside files/additions: keys kept, lists never shorter, values unchanged."""
    changes = []
    for key in old:
        if key in ("files", "additions") or key not in new:
            continue
        before, after = _shape({key: old[key]}), _shape({key: new[key]})
        for path, (kind, value) in before.items():
            if any(path == root or path.startswith(root + "/") for root in allowed):
                continue
            if path not in after:
                changes.append({"path": path, "change": "removed"})
            elif after[path][0] != kind:
                changes.append({"path": path, "change": f"{kind} became {after[path][0]}"})
            elif kind == "list" and after[path][1] < value:
                changes.append({"path": path, "change": f"list shrank from {value} to {after[path][1]}"})
            elif kind == "value" and after[path] != (kind, value):
                changes.append({"path": path, "change": "value changed"})
    return changes


def manifest_preserved(args):
    old, new = _load_manifest(args.old), _load_manifest(args.new)
    moves = dict(args.moved)
    updates = {path for path in args.updated if not path.startswith("/")}
    allowed = [path.rstrip("/") for path in args.updated if path.startswith("/")]
    if "" in allowed:
        raise CheckError("--updated / would skip every check; name a key path such as /backup_verification")
    missing_keys = [key for key in old if key not in new]
    missing, moved, updated, added = [], [], [], []
    for section in ("files", "additions"):
        old_entries, new_entries = old.get(section) or [], new.get(section) or []
        present = {_canonical(entry) for entry in new_entries}
        by_file = {_file(entry): _canonical(entry) for entry in new_entries if _file(entry)}
        accounted = set()
        for position, entry in enumerate(old_entries):
            text = _canonical(entry)
            target = moves.get(_file(entry))
            if text not in present and target is not None:
                text = _canonical({**entry, "file": target})
                if text in present:
                    moved.append({**_where(section, position, entry), "to": target})
            if text not in present and _file(entry) in updates and _file(entry) in by_file:
                text = by_file[_file(entry)]
                updated.append(_where(section, position, entry))
            if text in present:
                accounted.add(text)
            else:
                missing.append(_where(section, position, entry))
        added += [_where(section, position, entry) for position, entry in enumerate(new_entries)
                  if _canonical(entry) not in accounted]
    history = _history_changes(old, new, allowed)
    report = {"old": args.old, "new": args.new, "missing_keys": missing_keys,
              "missing_entries": missing, "moved": moved, "updated": updated, "added": added,
              "history_changes": history}
    failure = (f"{len(missing_keys)} top-level key(s), {len(missing)} entries and "
               f"{len(history)} nested history value(s) of OLD missing or changed in NEW")
    return report, failure if missing_keys or missing or history else None


# device-hashes ---------------------------------------------------------------

def device_hashes(args):
    profile = gaming_profile.load()
    if gaming_profile.validate(profile):
        raise CheckError("profile is invalid; run gaming_profile.py validate")
    device = profile["devices"].get(args.device)
    if device is None:
        raise CheckError(f"unknown device {args.device}")
    with open(args.map, encoding="utf-8") as file:
        pairs = json.load(file)
    if not isinstance(pairs, dict) or not all(
            isinstance(local, str) and os.path.isabs(remote) for remote, local in pairs.items()):
        raise CheckError("map must be a JSON object of absolute device paths to local paths")
    backend = snapshot.backend_for(device)
    remote_paths = list(pairs)
    present = [path for path, real in zip(remote_paths, backend.realpaths(remote_paths)) if real]
    remote = backend.hashes(present)
    entries, summary = [], {"match": 0, "mismatch": 0, "missing": 0}
    for path, local in pairs.items():
        gone = [side for side, there in (("device", path in remote), ("local", os.path.isfile(local)))
                if not there]
        if gone:
            entry = {"device_path": path, "local_path": local, "status": "missing", "missing": gone}
        else:
            entry = {"device_path": path, "local_path": local,
                     "status": "match" if remote[path] == sha256(local) else "mismatch"}
        summary[entry["status"]] += 1
        entries.append(entry)
    failure = f"{summary['mismatch']} mismatched and {summary['missing']} missing of {len(entries)} path(s)"
    report = {"device": args.device, "summary": summary, "paths": entries}
    return report, failure if summary["mismatch"] or summary["missing"] else None


# delta ------------------------------------------------------------------------

def delta(args):
    """List source files a cloud mirror lacks, holds at another size, or that changed since a date.

    Only metadata is read at the target, so online-only cloud files are never downloaded.
    """
    since = datetime.date.fromisoformat(args.since) if args.since else None
    cutoff = datetime.datetime.combine(since, datetime.time()).timestamp() if since else None
    entries, unchanged = [], 0
    for folder, dirs, names in os.walk(args.source):
        if os.path.samefile(folder, args.source):
            dirs[:] = [name for name in dirs if name not in args.exclude]
            names = [name for name in names if name not in args.exclude]
        dirs.sort()
        for name in sorted(names):
            if _is_metadata(name):
                continue
            path = os.path.join(folder, name)
            rel = os.path.relpath(path, args.source).replace(os.sep, "/")
            info, target = os.stat(path), os.path.join(args.target, rel)
            if not os.path.exists(target):
                reason = "new"
            elif os.path.getsize(target) != info.st_size:
                reason = "size-differs"
            elif cutoff is not None and info.st_mtime >= cutoff:
                reason = "changed-since"
            else:
                unchanged += 1
                continue
            entry = {"relative": rel, "reason": reason, "bytes": info.st_size}
            if reason != "new":
                there = os.stat(target)
                entry["target_online_only"] = there.st_blocks * 512 < there.st_size
            entries.append(entry)
    if args.list:
        with open(args.list, "w", encoding="utf-8") as file:
            file.writelines(entry["relative"] + "\n" for entry in entries)
    report = {"source": args.source, "target": args.target, "since": args.since,
              "unchanged_by_name_and_size": unchanged, "delta": entries}
    return report, None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    mount = commands.add_parser("mounted")
    where = mount.add_mutually_exclusive_group(required=True)
    where.add_argument("--library", metavar="ID")
    where.add_argument("--root", metavar="PATH")
    mount.add_argument("--volume", metavar="PATH")
    mount.set_defaults(run=mounted)
    clash = commands.add_parser("collisions")
    clash.add_argument("staging")
    clash.add_argument("root")
    clash.set_defaults(run=collisions)
    image = commands.add_parser("images")
    image.add_argument("files", nargs="+", metavar="FILE")
    image.set_defaults(run=images)
    listing = commands.add_parser("manifest")
    listing.add_argument("root")
    listing.add_argument("--hash", action="store_true")
    listing.set_defaults(run=manifest)
    preserved = commands.add_parser("manifest-preserved")
    preserved.add_argument("old")
    preserved.add_argument("new")
    preserved.add_argument("--moved", type=_move, action="append", default=[], metavar="OLDPATH=NEWPATH")
    preserved.add_argument("--updated", action="append", default=[], metavar="PATH")
    preserved.set_defaults(run=manifest_preserved)
    hashes = commands.add_parser("device-hashes")
    hashes.add_argument("--device", required=True, metavar="ID")
    hashes.add_argument("--map", required=True, metavar="FILE")
    hashes.set_defaults(run=device_hashes)
    changes = commands.add_parser("delta")
    changes.add_argument("source")
    changes.add_argument("target")
    changes.add_argument("--exclude", action="append", default=[], metavar="NAME")
    changes.add_argument("--since", metavar="YYYY-MM-DD")
    changes.add_argument("--list", metavar="FILE", help="write the delta paths for sync_tree.py --only")
    changes.set_defaults(run=delta)
    args = parser.parse_args(argv)
    if args.command == "mounted" and args.library and args.volume:
        parser.error("--volume goes with --root; --library reads the volume from the profile")

    try:
        report, failure = args.run(args)
    except (CheckError, snapshot.SnapshotError, gaming_profile.ProfileError, OSError, ValueError) as error:
        print(f"{PROG}: {error}", file=sys.stderr)
        return 2 if str(error).startswith("No gaming profile") else 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if failure:
        print(f"{PROG}: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
