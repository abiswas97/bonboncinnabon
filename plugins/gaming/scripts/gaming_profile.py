#!/usr/bin/env python3
"""Read and write the shared gaming profile.

The profile lives at $XDG_CONFIG_HOME/bonboncinnabon/gaming/profile.json
(or ~/.config/... when XDG_CONFIG_HOME is unset or relative) so Claude Code
and Codex read the same file. This script is the only writer: every write is
validated, the previous file is copied to history/, and the new file replaces
the old one atomically.

Usage:
  gaming_profile.py path
  gaming_profile.py show [POINTER]
  gaming_profile.py set POINTER JSON [--dry-run]
  gaming_profile.py unset POINTER [--dry-run]
  gaming_profile.py note DEVICE TEXT [--dry-run]
  gaming_profile.py validate [--file FILE]
  gaming_profile.py init --from FILE
"""

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SCHEMA_VERSION = 1
MAX_NOTES = 50
MAX_NOTE_CHARS = 300
ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SECRET_KEY = re.compile(r"(^|[_-])pass(word|wd|key)?$|secret|token|api[_-]?key|private[_-]?key|credential", re.I)
CONNECT_METHODS = {"ssh", "local"}
MISSING = "No gaming profile at {}. Run the gaming setup skill to create it."


class ProfileError(Exception):
    pass


def profile_path():
    base = os.environ.get("XDG_CONFIG_HOME", "")
    root = Path(base) if base and os.path.isabs(base) else Path.home() / ".config"
    return root / "bonboncinnabon" / "gaming" / "profile.json"


def load(path=None):
    path = path or profile_path()
    if not path.is_file():
        raise ProfileError(MISSING.format(path))
    with path.open(encoding="utf-8") as file:
        return json.load(file)


# Validation ---------------------------------------------------------------

def _absolute(value):
    return isinstance(value, str) and os.path.isabs(value)


def _check_notes(notes, where, errors):
    if not isinstance(notes, list):
        errors.append(f"{where}: must be a list")
        return
    if len(notes) > MAX_NOTES:
        errors.append(f"{where}: {len(notes)} notes exceed the limit of {MAX_NOTES}")
    for index, note in enumerate(notes):
        here = f"{where}/{index}"
        if not isinstance(note, dict) or set(note) - {"date", "text"}:
            errors.append(f"{here}: must be an object with only date and text")
            continue
        if not isinstance(note.get("date"), str) or not DATE.match(note["date"]):
            errors.append(f"{here}/date: must be YYYY-MM-DD")
        text = note.get("text")
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_NOTE_CHARS:
            errors.append(f"{here}/text: must be 1-{MAX_NOTE_CHARS} characters")


def _check_ids(section, where, errors):
    if not isinstance(section, dict):
        errors.append(f"{where}: must be an object keyed by id")
        return {}
    for key in section:
        if not ID.match(key):
            errors.append(f"{where}/{key}: id must be lowercase letters, digits and hyphens")
    return section


def _check_secrets(value, where, errors):
    if isinstance(value, dict):
        for key, child in value.items():
            if SECRET_KEY.search(key):
                errors.append(f"{where}/{key}: credentials do not belong in the profile")
            _check_secrets(child, f"{where}/{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_secrets(child, f"{where}/{index}", errors)
    elif isinstance(value, str) and "-----BEGIN" in value:
        errors.append(f"{where}: looks like a private key")


def validate(data):
    """Return a list of 'pointer: problem' strings; empty means valid."""
    errors = []
    if not isinstance(data, dict):
        return [": profile must be a JSON object"]
    for key in ("schema_version", "timezone", "libraries", "backup_targets", "devices",
                "collections", "policies", "preferences"):
        if key not in data:
            errors.append(f"/{key}: required")
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"/schema_version: must be {SCHEMA_VERSION}")
    try:
        ZoneInfo(str(data.get("timezone")))
    except (ZoneInfoNotFoundError, ValueError):
        errors.append("/timezone: must be an IANA timezone such as Europe/London")

    libraries = _check_ids(data.get("libraries", {}), "/libraries", errors)
    if libraries and sum(bool(lib.get("canonical")) for lib in libraries.values() if isinstance(lib, dict)) != 1:
        errors.append("/libraries: exactly one library must have canonical: true")
    for key, library in libraries.items():
        here = f"/libraries/{key}"
        if not isinstance(library, dict):
            errors.append(f"{here}: must be an object")
            continue
        if not _absolute(library.get("root")):
            errors.append(f"{here}/root: must be an absolute path")
        if "volume" in library and not _absolute(library["volume"]):
            errors.append(f"{here}/volume: must be an absolute path")
        for field in ("extra_sources", "off_limits"):
            if not all(_absolute(p) for p in library.get(field, [])):
                errors.append(f"{here}/{field}: must be absolute paths")
        _check_notes(library.get("notes", []), f"{here}/notes", errors)

    for key, target in _check_ids(data.get("backup_targets", {}), "/backup_targets", errors).items():
        here = f"/backup_targets/{key}"
        if not isinstance(target, dict) or not isinstance(target.get("kind"), str):
            errors.append(f"{here}/kind: required string")
            continue
        if not isinstance(target.get("enabled"), bool):
            errors.append(f"{here}/enabled: must be true or false")
        if target.get("library") not in libraries:
            errors.append(f"{here}/library: must name a library id")

    for key, device in _check_ids(data.get("devices", {}), "/devices", errors).items():
        here = f"/devices/{key}"
        if not isinstance(device, dict):
            errors.append(f"{here}: must be an object")
            continue
        if not isinstance(device.get("label"), str) or not device["label"].strip():
            errors.append(f"{here}/label: required string")
        connect = device.get("connect")
        if not isinstance(connect, dict) or connect.get("method") not in CONNECT_METHODS:
            errors.append(f"{here}/connect/method: must be one of {sorted(CONNECT_METHODS)}")
        elif connect["method"] == "ssh" and not connect.get("ssh_alias"):
            errors.append(f"{here}/connect/ssh_alias: required for ssh")
        if not isinstance(device.get("install_opt_in", False), bool):
            errors.append(f"{here}/install_opt_in: must be true or false")
        for system, mapping in device.get("systems", {}).items():
            if not isinstance(mapping, dict) or not isinstance(mapping.get("emulator"), str):
                errors.append(f"{here}/systems/{system}/emulator: required string")
        baseline = device.get("frontend", {}).get("baseline", {}).get("settings", {})
        if not isinstance(baseline, dict) or not all(isinstance(v, str) for v in baseline.values()):
            errors.append(f"{here}/frontend/baseline/settings: values must be strings")
        _check_notes(device.get("notes", []), f"{here}/notes", errors)

    for name in ("collections", "policies"):
        if not isinstance(data.get(name, {}), dict):
            errors.append(f"/{name}: must be an object")
    if not isinstance(data.get("preferences", []), list) or not all(
            isinstance(p, str) for p in data.get("preferences", [])):
        errors.append("/preferences: must be a list of strings")
    _check_secrets(data, "", errors)
    return errors


# JSON Pointer (RFC 6901) --------------------------------------------------

def _tokens(pointer):
    if pointer in ("", "/"):
        return []
    if not pointer.startswith("/"):
        raise ProfileError(f"pointer must start with /: {pointer}")
    return [t.replace("~1", "/").replace("~0", "~") for t in pointer[1:].split("/")]


def get(data, pointer):
    node = data
    for token in _tokens(pointer):
        if isinstance(node, list) and token.isdigit() and int(token) < len(node):
            node = node[int(token)]
        elif isinstance(node, dict) and token in node:
            node = node[token]
        else:
            raise ProfileError(f"no value at {pointer}")
    return node


def _parent(data, pointer, create):
    tokens = _tokens(pointer)
    if not tokens:
        raise ProfileError("cannot replace the whole profile; use init")
    node = data
    for token in tokens[:-1]:
        if isinstance(node, list) and token.isdigit():
            node = node[int(token)]
        elif isinstance(node, dict):
            if token not in node:
                if not create:
                    raise ProfileError(f"no value at {pointer}")
                node[token] = {}
            node = node[token]
        else:
            raise ProfileError(f"cannot descend into {token} at {pointer}")
    return node, tokens[-1]


def set_value(data, pointer, value):
    parent, key = _parent(data, pointer, create=True)
    if isinstance(parent, list):
        parent[int(key)] = value
    else:
        parent[key] = value


def unset_value(data, pointer):
    parent, key = _parent(data, pointer, create=False)
    if isinstance(parent, list):
        del parent[int(key)]
    elif key in parent:
        del parent[key]
    else:
        raise ProfileError(f"no value at {pointer}")


def add_note(data, device, text, today=None):
    if device not in data.get("devices", {}):
        raise ProfileError(f"unknown device {device}")
    notes = data["devices"][device].setdefault("notes", [])
    if len(notes) >= MAX_NOTES:
        raise ProfileError(f"{device} already has {MAX_NOTES} notes; merge or remove one first")
    notes.append({"date": (today or date.today()).isoformat(), "text": text.strip()})


# Writing -------------------------------------------------------------------

def write(data, path=None):
    """Validate, keep a history copy of the current file, then replace atomically."""
    path = path or profile_path()
    errors = validate(data)
    if errors:
        raise ProfileError("profile not written:\n" + "\n".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.exists():
        history = path.parent / "history"
        history.mkdir(exist_ok=True, mode=0o700)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        with (history / f"profile-{stamp}.json").open("xb") as copy:
            copy.write(path.read_bytes())
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".profile-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    except BaseException:
        if os.path.exists(temp):
            os.unlink(temp)
        raise


def _dump(value):
    return json.dumps(value, indent=2, ensure_ascii=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("path")
    show = commands.add_parser("show")
    show.add_argument("pointer", nargs="?", default="")
    for name in ("set", "unset", "note"):
        sub = commands.add_parser(name)
        sub.add_argument("first")
        if name != "unset":
            sub.add_argument("second")
        sub.add_argument("--dry-run", action="store_true")
    check = commands.add_parser("validate")
    check.add_argument("--file", type=Path)
    init = commands.add_parser("init")
    init.add_argument("--from", dest="source", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.command == "path":
            print(profile_path())
        elif args.command == "show":
            print(_dump(get(load(), args.pointer)))
        elif args.command == "validate":
            with (args.file or profile_path()).open(encoding="utf-8") as file:
                errors = validate(json.load(file))
            if errors:
                raise ProfileError("\n".join(errors))
            print("profile is valid")
        elif args.command == "init":
            if profile_path().exists():
                raise ProfileError(f"{profile_path()} already exists; use set, unset or note")
            with args.source.open(encoding="utf-8") as file:
                write(json.load(file))
            print(f"created {profile_path()}")
        else:
            data = load()
            if args.command == "set":
                old = get(data, args.first) if _has(data, args.first) else None
                set_value(data, args.first, json.loads(args.second))
                change = f"{args.first}: {json.dumps(old)} -> {args.second}"
            elif args.command == "unset":
                old = get(data, args.first)
                unset_value(data, args.first)
                change = f"{args.first}: removed {json.dumps(old)}"
            else:
                add_note(data, args.first, args.second)
                change = f"/devices/{args.first}/notes: added {json.dumps(args.second)}"
            if args.dry_run:
                errors = validate(data)
                print(("would change " if not errors else "invalid change ") + change)
                if errors:
                    raise ProfileError("\n".join(errors))
            else:
                write(data)
                print("changed " + change)
    except (ProfileError, json.JSONDecodeError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 2 if isinstance(error, ProfileError) and str(error).startswith("No gaming profile") else 1
    return 0


def _has(data, pointer):
    try:
        get(data, pointer)
        return True
    except ProfileError:
        return False


if __name__ == "__main__":
    sys.exit(main())
