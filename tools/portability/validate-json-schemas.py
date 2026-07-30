#!/usr/bin/env python3
"""Validate repository JSON Schemas and their canonical documents."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def read_json(relative):
    with (ROOT / relative).open(encoding="utf-8") as file:
        return json.load(file)


def validate(schema_relative, document, label):
    schema = read_json(schema_relative)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(document),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        details = "\n".join(
            f"{label}{''.join(f'[{part!r}]' for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        raise SystemExit(details)


marketplace = read_json("marketplace/marketplace.json")
validate("schemas/marketplace.schema.json", marketplace, "marketplace/marketplace.json")

for entry in marketplace["plugins"]:
    if entry["kind"] != "local":
        continue
    relative = Path(entry["path"]) / "plugin.json"
    validate("schemas/plugin.schema.json", read_json(relative), str(relative))

validate(
    "schemas/standards-registry.schema.json",
    read_json("plugins/standards/standards/registry.json"),
    "plugins/standards/standards/registry.json",
)
Draft202012Validator.check_schema(read_json("schemas/standards-overlay.schema.json"))

print("Canonical documents satisfy valid Draft 2020-12 schemas.")
