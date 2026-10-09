#!/usr/bin/env python3
"""Compare ES-DE settings with a device baseline, or capture one.

es_settings.xml has no single root element, so the content after the XML
declaration is wrapped in a synthetic root before parsing. Settings are
<bool|int|float|string name=".." value=".." /> elements, compared as exact
strings. A baselined key missing from the file counts as drift.

Usage:
  esde_baseline.py check --settings FILE (--device ID | --baseline JSON_FILE)
  esde_baseline.py capture --settings FILE [--keys K1,K2]

capture prints a JSON object ready for
  gaming_profile.py set /devices/ID/frontend/baseline/settings JSON
It always leaves out credential settings and names them on stderr.
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gaming_profile  # noqa: E402

PROG = "esde_baseline"
TYPES = {"bool", "int", "float", "string"}
DECLARATION = re.compile(r"^\s*<\?xml[^>]*\?>")
ACCOUNT_KEY = re.compile(r"username|password", re.I)


class BaselineError(Exception):
    pass


def read_settings(path):
    with open(path, encoding="utf-8-sig") as file:
        body = DECLARATION.sub("", file.read(), count=1)
    try:
        root = ET.fromstring(f"<settings>{body}</settings>")
    except ET.ParseError as error:
        raise BaselineError(f"{path}: {error}") from error
    return {item.get("name"): item.get("value") for item in root
            if item.tag in TYPES and item.get("name") is not None}


def load_baseline(args):
    if args.baseline:
        with open(args.baseline, encoding="utf-8") as file:
            baseline = json.load(file)
    else:
        baseline = gaming_profile.get(gaming_profile.load(),
                                      f"/devices/{args.device}/frontend/baseline/settings")
    if not isinstance(baseline, dict) or not all(isinstance(v, str) for v in baseline.values()):
        raise BaselineError("baseline must be a JSON object of string values")
    return baseline


def is_credential(key):
    return bool(gaming_profile.SECRET_KEY.search(key) or ACCOUNT_KEY.search(key))


def check(args):
    settings, baseline = read_settings(args.settings), load_baseline(args)
    drift = [{"key": key, "expected": expected, "found": settings.get(key)}
             for key, expected in baseline.items() if settings.get(key) != expected]
    failure = f"{len(drift)} of {len(baseline)} baselined settings drifted" if drift else None
    return {"checked": len(baseline), "drift": drift}, failure


def capture(args):
    settings = read_settings(args.settings)
    keys = [k.strip() for k in args.keys.split(",") if k.strip()] if args.keys else list(settings)
    absent = [key for key in keys if key not in settings]
    if absent:
        raise BaselineError(f"not in {args.settings}: {', '.join(absent)}")
    excluded = [key for key in keys if is_credential(key)]
    if excluded:
        print(f"{PROG}: left out credential settings: {', '.join(excluded)}", file=sys.stderr)
    return {key: settings[key] for key in keys if key not in excluded}, None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    compare = commands.add_parser("check")
    compare.add_argument("--settings", required=True, metavar="FILE")
    source = compare.add_mutually_exclusive_group(required=True)
    source.add_argument("--device", metavar="ID")
    source.add_argument("--baseline", metavar="JSON_FILE")
    compare.set_defaults(run=check)
    record = commands.add_parser("capture")
    record.add_argument("--settings", required=True, metavar="FILE")
    record.add_argument("--keys", metavar="K1,K2")
    record.set_defaults(run=capture)
    args = parser.parse_args(argv)

    try:
        report, failure = args.run(args)
    except (BaselineError, gaming_profile.ProfileError, OSError, ValueError) as error:
        print(f"{PROG}: {error}", file=sys.stderr)
        return 2 if str(error).startswith("No gaming profile") else 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if failure:
        print(f"{PROG}: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
