#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "scripts"))
from devlab_contracts import ContractError, dump_config, migrated_config, parse_simple_yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview or confirm DevLab legacy configuration migration")
    parser.add_argument("legacy", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    try:
        rendered = dump_config(migrated_config(parse_simple_yaml(args.legacy.read_text())))
    except (OSError, ContractError) as error:
        print(f"DevLab config migration failed: {error}", file=sys.stderr)
        return 2
    if not args.confirm:
        print(rendered, end="")
        print("Preview only; rerun with --confirm after user approval.", file=sys.stderr)
        return 3
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with args.output.open("x") as output:
            output.write(rendered)
    except FileExistsError:
        print(f"DevLab config migration failed: {args.output} already exists", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
