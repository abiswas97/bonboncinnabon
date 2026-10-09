#!/usr/bin/env python3
"""Verify ROM files against Logiqx XML or clrmamepro DAT catalogues.

Each file is hashed in one pass (size, CRC32, MD5, SHA-1, SHA-256). A zip is
integrity-tested and each member is verified instead of the zip itself. A DAT
entry matches on SHA-1 when it has one, else MD5, else CRC32 plus size. A
catalogue match proves dump identity only, not achievement-hash compatibility.
Without --dat (no catalogue covers the game, such as homebrew), files are only
hashed and zips integrity-tested; identity stays unverified.

Usage:
  verify_rom.py FILE [FILE...] [--dat DAT...]

Exit status: 0 when every file or zip member matched (or, without --dat, was
read intact), 1 when any did not or could not be read, 3 for .7z and .rar
archives (extract them first).
"""

import argparse
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib

PROG = "verify_rom"
CHUNK = 8 * 1024 * 1024
UNSUPPORTED = {".7z", ".rar"}
ZIP_ERRORS = (zipfile.BadZipFile, zlib.error, EOFError, NotImplementedError, RuntimeError)
NOTE = "A catalogue match proves dump identity only, not achievement-hash compatibility."
NO_CATALOGUE = "No catalogue given: files were hashed and archives tested; identity is unverified."
CLR_TOKEN = re.compile(r'"([^"]*)"|([()])|([^\s()"]+)')
OPEN, CLOSE = object(), object()


class VerifyError(Exception):
    pass


def digest(stream):
    """Return size, CRC32, MD5, SHA-1 and SHA-256 of a binary stream, reading it once."""
    hashes = {name: hashlib.new(name, usedforsecurity=False) for name in ("md5", "sha1", "sha256")}
    crc = size = 0
    while block := stream.read(CHUNK):
        crc = zlib.crc32(block, crc)
        size += len(block)
        for value in hashes.values():
            value.update(block)
    return {"size": size, "crc32": f"{crc:08x}", **{name: h.hexdigest() for name, h in hashes.items()}}


# DAT parsing ----------------------------------------------------------------

def _entry(dat, game, rom):
    size, crc = rom.get("size", "").strip(), rom.get("crc", "").strip()
    return {"dat": dat, "game": game, "rom": rom.get("name"),
            "size": int(size) if size.isdigit() else None,
            "crc32": crc.lower().zfill(8) if crc else "",
            "md5": rom.get("md5", "").strip().lower(),
            "sha1": rom.get("sha1", "").strip().lower()}


def _logiqx(dat, data):
    root = ET.fromstring(data)
    if root.tag != "datafile":
        raise VerifyError(f"{dat}: XML root is <{root.tag}>, not a Logiqx <datafile>")
    return [_entry(dat, game.get("name"), rom.attrib)
            for game in root if game.tag in ("game", "machine")
            for rom in game.findall("rom")]


def _clr_tokens(text):
    for quoted, paren, word in (match.groups() for match in CLR_TOKEN.finditer(text)):
        if paren:
            yield OPEN if paren == "(" else CLOSE
        else:
            yield word if quoted is None else quoted


def _clr_block(tokens):
    """Parse `key value` and `key ( ... )` pairs up to the closing parenthesis."""
    items = []
    for key in tokens:
        if key is CLOSE:
            break
        value = next(tokens, CLOSE)
        if value is CLOSE:
            break
        items.append((key, _clr_block(tokens) if value is OPEN else value))
    return items


def _clrmamepro(dat, text):
    entries = []
    for key, game in _clr_block(_clr_tokens(text)):
        if key in ("game", "machine") and isinstance(game, list):
            name = next((v for k, v in game if k == "name" and isinstance(v, str)), None)
            entries += [_entry(dat, name, {k: v for k, v in rom if isinstance(v, str)})
                        for k, rom in game if k == "rom" and isinstance(rom, list)]
    return entries


def load_dat(path):
    with open(path, "rb") as file:
        data = file.read()
    try:
        if data.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"<"):
            entries = _logiqx(path, data)
        else:
            entries = _clrmamepro(path, data.decode("utf-8", errors="replace"))
    except ET.ParseError as error:
        raise VerifyError(f"{path}: {error}") from error
    if not entries:
        raise VerifyError(f"{path}: no ROM entries found")
    return entries


# Matching -------------------------------------------------------------------

def index(entries):
    """Key each DAT entry by the strongest identity it records."""
    table = {}
    for entry in entries:
        if entry["sha1"]:
            key = ("sha1", entry["sha1"])
        elif entry["md5"]:
            key = ("md5", entry["md5"])
        elif entry["crc32"] and entry["size"] is not None:
            key = ("crc32+size", f"{entry['crc32']}:{entry['size']}")
        else:
            continue
        table.setdefault(key, []).append(entry)
    return table


def matches(hashes, table):
    keys = [("sha1", hashes["sha1"]), ("md5", hashes["md5"]),
            ("crc32+size", f"{hashes['crc32']}:{hashes['size']}")]
    return [{"dat": e["dat"], "game": e["game"], "rom": e["rom"], "matched_on": on}
            for on, value in keys for e in table.get((on, value), [])]


def verify(path, table):
    """Return one result for a plain file, or one per member of a zip."""
    if os.path.splitext(path)[1].lower() != ".zip":
        with open(path, "rb") as file:
            hashes = digest(file)
        return [{"file": path, "member": None, **hashes, "matches": matches(hashes, table)}]
    results = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise VerifyError(f"bad zip member {bad}")
        for info in archive.infolist():
            if not info.is_dir():
                with archive.open(info) as member:
                    hashes = digest(member)
                results.append({"file": path, "member": info.filename, **hashes,
                                "matches": matches(hashes, table)})
    if not results:
        raise VerifyError("zip has no files")
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("files", nargs="+", metavar="FILE")
    parser.add_argument("--dat", action="append", default=[], metavar="DAT")
    args = parser.parse_args(argv)

    unsupported = [p for p in args.files if os.path.splitext(p)[1].lower() in UNSUPPORTED]
    for path in unsupported:
        print(f"{PROG}: {path}: unsupported archive; extract first", file=sys.stderr)
    if unsupported:
        return 3
    try:
        table = index([entry for dat in args.dat for entry in load_dat(dat)])
    except (VerifyError, OSError) as error:
        print(f"{PROG}: {error}", file=sys.stderr)
        return 1

    results = []
    for path in args.files:
        try:
            results += verify(path, table)
        except (VerifyError, OSError, *ZIP_ERRORS) as error:
            results.append({"file": path, "error": str(error)})
    print(json.dumps({"note": NOTE if args.dat else NO_CATALOGUE, "files": results},
                     indent=2, ensure_ascii=False))
    failed = [r for r in results if "error" in r or (args.dat and not r.get("matches"))]
    for result in failed:
        label = result["file"] + (f":{result['member']}" if result.get("member") else "")
        print(f"{PROG}: {label}: {result.get('error', 'no DAT match')}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
