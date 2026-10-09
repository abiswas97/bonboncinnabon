#!/usr/bin/env python3
"""Take a read-only recovery snapshot of a device from the gaming profile.

The device is only listed, hashed, resolved, read and archived. Nothing on it
is started, stopped, written or asked to save, so the snapshot is the on-disk
state. Files are inventoried and hashed before and after archiving.

Each snapshot is built in <library root>/Staging/snapshots/<device label>/<stamp>/
as <scope>.tar and manifest.json. Only once fully verified is that folder moved
by rename to <library root>/Recovery/<device label>/<stamp>/, which must not
exist yet. Any failure leaves the build in Staging with <scope>.tar.incomplete
and a manifest with status "incomplete", and nothing under Recovery. Only a
manifest with status "verified" in Recovery means success. File contents and
command output are never printed; the manifest holds only paths, sizes and
hashes.

Config values starting with ~/ resolve against the device home.

Scopes:
  config  each emulator's main config, its folder, config_dirs and the paths
          named by config_keys (filtered by config_extensions), plus the
          frontend settings file and its settings, collections, custom_systems
          and gamelists folders
  full    config plus every device path, the whole frontend home and the data
          folders named by each emulator's data_keys (unfiltered)

Usage:
  snapshot.py --device ID --scope config|full [--library ID] [--dry-run]
"""

import argparse
import hashlib
import json
import os
import posixpath
import re
import shlex
import stat
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gaming_profile  # noqa: E402

SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
       "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=2"]
EXTENSIONS = (".cfg", ".opt", ".rmp", ".slangp", ".glslp", ".cgp")
FRONTEND_FOLDERS = ("settings", "collections", "custom_systems", "gamelists")
KEY_LINE = re.compile(r'^\s*(\w+)\s*=\s*"([^"\n]*)"')
DIGEST = re.compile(r"[0-9a-f]{64}")
BATCH = 80
STAMP = "%Y-%m-%d_%H-%M-%S_%Z"
# Hashing and archiving scale with data size; ServerAlive* catches a dead link sooner.
# ponytail: fixed ceilings of 1 h per hash batch and 6 h per archive; make them options if a device needs longer.
HASH_TIMEOUT = 3600
ARCHIVE_TIMEOUT = 6 * 3600


class SnapshotError(Exception):
    pass


# Backends ------------------------------------------------------------------

def _raise(error):
    raise error


class Local:
    """Read files on this computer."""

    def home(self):
        return os.path.expanduser("~")

    def read(self, path):
        return Path(path).read_bytes()

    def realpaths(self, paths):
        return [os.path.realpath(path) if os.path.exists(path) else None for path in paths]

    def files(self, roots):
        found = []
        for root in roots:
            if os.path.isfile(root):
                found.append(root)
                continue
            for folder, _, names in os.walk(root, onerror=_raise):
                found += [path for path in (os.path.join(folder, name) for name in names)
                          if stat.S_ISREG(os.lstat(path).st_mode)]
        return found

    def hashes(self, paths):
        result = {}
        for path in paths:
            with open(path, "rb") as file:
                result[path] = hashlib.file_digest(file, "sha256").hexdigest()
        return result

    def sizes(self, paths):
        return {path: os.lstat(path).st_size for path in paths}

    def archive(self, paths, out):
        with tarfile.open(fileobj=out, mode="w|") as tar:
            for path in paths:
                tar.add(path, arcname=path.lstrip("/"), recursive=False)


def _quote(paths):
    return " ".join(shlex.quote(path) for path in paths)


def _batches(paths):
    return (paths[start:start + BATCH] for start in range(0, len(paths), BATCH))


class Ssh:
    """Run read-only commands through prefix + [command]; output never leaves this object."""

    def __init__(self, device, hints, prefix):
        self.device, self.hints, self.prefix = device, hints, prefix

    def _run(self, step, command, data=b"", out=subprocess.PIPE, timeout=180):
        try:
            result = subprocess.run(self.prefix + [command], input=data, stdout=out,
                                    stderr=subprocess.DEVNULL, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            result = None
        if result is None or result.returncode:
            raise SnapshotError(f"{step} failed on {self.device}; check: {self.hints}")
        return result.stdout

    def _bad(self, step):
        return SnapshotError(f"unexpected {step} response from {self.device}")

    def home(self):
        home = os.fsdecode(self._run("resolve home", 'printf %s "$HOME"'))
        if not posixpath.isabs(home):
            raise self._bad("resolve home")
        return home

    def read(self, path):
        return self._run("read config", "cat -- " + shlex.quote(path))

    def realpaths(self, paths):
        if not paths:
            return []
        script = ("for p in " + _quote(paths) + '; do if test -e "$p"; then '
                  'realpath -- "$p" || exit 1; else echo; fi; done')
        lines = os.fsdecode(self._run("resolve paths", script)).split("\n")[:-1]
        if len(lines) != len(paths):
            raise self._bad("resolve paths")
        return [line or None for line in lines]

    def files(self, roots):
        if not roots:
            return []
        output = self._run("inventory", "find " + _quote(roots) + " -type f -print0")
        return [os.fsdecode(path) for path in output.split(b"\0") if path]

    def hashes(self, paths):
        result = {}
        for batch in _batches(paths):
            output = self._run("hash", "sha256sum --zero -- " + _quote(batch), timeout=HASH_TIMEOUT)
            for record in output.split(b"\0"):
                if record:
                    digest = record[:64].decode("ascii", "replace")
                    if not DIGEST.fullmatch(digest):
                        raise self._bad("hash")
                    result[os.fsdecode(record[66:])] = digest
        if set(result) != set(paths):
            raise self._bad("hash")
        return result

    def sizes(self, paths):
        result = {}
        for batch in _batches(paths):
            sizes = self._run("size", "stat -c %s -- " + _quote(batch)).split()
            if len(sizes) != len(batch) or not all(size.isdigit() for size in sizes):
                raise self._bad("size")
            result.update(zip(batch, map(int, sizes)))
        return result

    def archive(self, paths, out):
        members = b"".join(os.fsencode(path.lstrip("/")) + b"\0" for path in paths)
        self._run("archive", "COPYFILE_DISABLE=1 tar -C / --null -T - -cf -", members, out,
                  timeout=ARCHIVE_TIMEOUT)


def backend_for(device):
    connect = device["connect"]
    if connect["method"] == "local":
        return Local()
    hints = " ".join(connect.get("hints", [])) or "the device is awake and reachable over SSH"
    return Ssh(device["label"], hints, SSH + [connect["ssh_alias"]])


# Discovery -----------------------------------------------------------------

def library_root(profile, library_id):
    libraries = profile["libraries"]
    library_id = library_id or next(key for key, value in libraries.items() if value.get("canonical"))
    library = libraries.get(library_id)
    if library is None:
        raise SnapshotError(f"unknown library {library_id}")
    if library.get("volume") and not os.path.ismount(library["volume"]):
        raise SnapshotError("library drive not mounted")
    if not os.path.isdir(library["root"]):
        raise SnapshotError("library root missing")
    return Path(library["root"])


def configured_paths(data, keys):
    values = {}
    for line in data.decode("utf-8", errors="replace").splitlines():
        match = KEY_LINE.match(line)
        if match and match[1] in keys:
            values[match[1]] = match[2]
    return {key: value for key, value in values.items() if value and value != "default"}


def expand_home(value, backend):
    return backend.home() + value[1:] if value == "~" or value.startswith("~/") else value


def roots_for(device, scope, backend):
    """Return [(path, extensions or None)] and [(emulator, main config, bytes read)]."""
    roots, mains = [], []

    def add(where, path, extensions=None):
        if not posixpath.isabs(path):
            raise SnapshotError(f"{where} is a relative path; inspect how it resolves first")
        roots.append((path, extensions))

    for name, emulator in device.get("emulators", {}).items():
        main = emulator.get("config")
        if not main:
            continue
        where = f"emulators/{name}"
        extensions = frozenset(e.lower() for e in emulator.get("config_extensions", EXTENSIONS))
        add(f"{where}/config", main)
        data = backend.read(main)
        if not data:
            raise SnapshotError(f"{where}/config is empty")
        mains.append((name, main, data))
        add(f"{where}/config", posixpath.dirname(main), extensions)
        for folder in emulator.get("config_dirs", []):
            add(f"{where}/config_dirs", folder, extensions)
        for key, value in configured_paths(data, set(emulator.get("config_keys", []))).items():
            add(f"{where}/config_keys/{key}", expand_home(value, backend), extensions)
        if scope == "full":
            for key, value in configured_paths(data, set(emulator.get("data_keys", []))).items():
                add(f"{where}/data_keys/{key}", expand_home(value, backend))
    frontend = device.get("frontend", {})
    if frontend.get("settings_file"):
        add("frontend/settings_file", frontend["settings_file"])
    home = frontend.get("home")
    for folder in FRONTEND_FOLDERS if home else ():
        add("frontend/home", posixpath.join(home, folder))
    if scope == "full":
        for key, path in device.get("paths", {}).items():
            add(f"paths/{key}", path)
        if home:
            add("frontend/home", home)
    return roots, mains


def _inside(path, root):
    return path == root or path.startswith(root.rstrip("/") + "/")


def canonical(roots, backend):
    """Resolve roots, merge aliases and drop roots that another root already covers."""
    names = sorted({path for path, _ in roots})
    real = dict(zip(names, backend.realpaths(names)))
    merged = {}
    for path, extensions in roots:
        target = real[path]
        if target is None:
            continue
        if target in merged:
            extensions = None if merged[target] is None or extensions is None else merged[target] | extensions
        merged[target] = extensions

    def covered(path, extensions):
        return any(other != path and _inside(path, other)
                   and (wider is None or (extensions is not None and extensions <= wider))
                   for other, wider in merged.items())

    kept = {path: extensions for path, extensions in merged.items() if not covered(path, extensions)}
    return kept, [path for path in names if real[path] is None], real


def inventory(roots, backend):
    def wanted(path):
        suffix = PurePosixPath(path).suffix.lower()
        return any(_inside(path, root) and (extensions is None or suffix in extensions)
                   for root, extensions in roots.items())

    # ponytail: files x roots scan; roots stay in the tens, so no index needed.
    return sorted({path for path in backend.files(sorted(roots)) if wanted(path)})


# Capture -------------------------------------------------------------------

def _now(timezone):
    return datetime.now(ZoneInfo(timezone))


def _folders(root, *parts):
    """Create root/parts one level at a time, so a vanished drive fails instead of creating a substitute."""
    folder = root
    for part in parts:
        folder = folder / part
        folder.mkdir(mode=0o700, exist_ok=True)
    return folder


def new_build(root, label, stamp):
    if "/" in label or label in (".", ".."):
        raise SnapshotError("device label cannot be used as a folder name")
    build = _folders(root, "Staging", "snapshots", label) / stamp
    try:
        build.mkdir(mode=0o700)
    except FileExistsError:
        raise SnapshotError(f"{build} already exists; snapshots are never reused") from None
    return build


def publish_target(root, label, stamp):
    final = _folders(root, "Recovery", label) / stamp
    if final.exists():
        raise SnapshotError(f"{final} already exists; snapshots are never reused")
    return final


def verify(archive, before):
    records, found = [], set()
    with tarfile.open(archive, "r:") as tar:
        for member in tar:
            source = "/" + member.name
            if not member.isfile() or source not in before or source in found:
                raise SnapshotError("unexpected archive member")
            found.add(source)
            digest = hashlib.file_digest(tar.extractfile(member), "sha256").hexdigest()
            if digest != before[source]:
                raise SnapshotError("archive content checksum mismatch")
            records.append({"source": source, "archive_path": member.name,
                            "bytes": member.size, "sha256": digest})
    if found != set(before):
        raise SnapshotError("archive inventory mismatch")
    return records


def capture(partial, paths, before, roots, backend):
    with partial.open("xb") as out:
        backend.archive(paths, out)
        out.flush()
        os.fsync(out.fileno())
    if inventory(roots, backend) != paths or backend.hashes(paths) != before:
        raise SnapshotError("source files changed during the snapshot")
    records = verify(partial, before)
    with partial.open("rb") as file:
        return records, hashlib.file_digest(file, "sha256").hexdigest()


def write_manifest(destination, manifest):
    with (destination / "manifest.json").open("x", encoding="utf-8") as out:
        json.dump(manifest, out, indent=2, ensure_ascii=False)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())


def take_snapshot(profile, device_id, scope, library_id=None, dry_run=False, backend=None):
    if gaming_profile.validate(profile):
        raise SnapshotError("profile is invalid; run gaming_profile.py validate")
    device = profile["devices"].get(device_id)
    if device is None:
        raise SnapshotError(f"unknown device {device_id}")
    root = library_root(profile, library_id)
    backend = backend or backend_for(device)
    roots, mains = roots_for(device, scope, backend)
    kept, missing, real = canonical(roots, backend)
    paths = inventory(kept, backend)
    if dry_run:
        return {"dry_run": True, "roots": sorted(kept), "missing_paths": missing,
                "files": len(paths), "bytes": sum(backend.sizes(paths).values())}
    if not paths:
        raise SnapshotError("nothing to snapshot")
    before = backend.hashes(paths)
    for name, main, data in mains:
        if real[main] not in before:
            raise SnapshotError(f"emulators/{name}/config missing from inventory")
        if before[real[main]] != hashlib.sha256(data).hexdigest():
            raise SnapshotError(f"emulators/{name}/config changed while discovering; retry when quiet")

    timezone = profile["timezone"]
    stamp = _now(timezone).strftime(STAMP)
    build = new_build(root, device["label"], stamp)
    partial = build / f"{scope}.tar.incomplete"
    try:
        records, archive_sha256 = capture(partial, paths, before, kept, backend)
        final = publish_target(root, device["label"], stamp)
    except (SnapshotError, OSError, tarfile.TarError) as error:
        write_manifest(build, {"status": "incomplete", "reason": str(error),
                               "created_at": _now(timezone).isoformat(),
                               "device": device_id, "scope": scope})
        raise SnapshotError(f"{error}; not verified, incomplete archive kept in {build}") from None
    partial.rename(build / f"{scope}.tar")
    write_manifest(build, {"status": "verified", "created_at": _now(timezone).isoformat(),
                           "device": device_id, "scope": scope, "missing_paths": missing,
                           "files": records, "archive_sha256": archive_sha256})
    # Same volume, so the verified folder appears whole; a non-empty folder at final makes this fail.
    os.rename(build, final)
    return {"directory": str(final), "status": "verified",
            "verified_files": len(records), "missing_paths": missing}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--device", required=True)
    parser.add_argument("--scope", required=True, choices=("config", "full"))
    parser.add_argument("--library", help="library id; defaults to the canonical library")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    umask = os.umask(0o077)
    try:
        summary = take_snapshot(gaming_profile.load(), args.device, args.scope, args.library, args.dry_run)
    except (SnapshotError, gaming_profile.ProfileError, OSError, json.JSONDecodeError,
            tarfile.TarError) as error:
        print(f"snapshot: {error}", file=sys.stderr)
        return 1
    finally:
        os.umask(umask)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
