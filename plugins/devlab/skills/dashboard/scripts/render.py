#!/usr/bin/env python3
"""Render a validated DevLab dashboard from one JSON document on stdin."""

from __future__ import annotations

import json
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parents[3] / "scripts"))
from devlab_contracts import ContractError, velocity

WIDTH = 76


def display_width(text: str) -> int:
    return sum(0 if unicodedata.combining(char) else 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1 for char in text)


def fit(text: str, width: int) -> str:
    text = " ".join(str(text).split())
    result = ""
    for char in text:
        if display_width(result + char) > width:
            break
        result += char
    if result != text and width >= 1:
        while result and display_width(result + "…") > width:
            result = result[:-1]
        result += "…"
    return result + " " * max(0, width - display_width(result))


def bar(done: int | float, total: int | float, width: int = 20) -> str:
    bounded_total = max(0.0, float(total))
    ratio = 0.0 if bounded_total == 0 else max(0.0, min(1.0, float(done) / bounded_total))
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


def parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{field} must be an ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError(f"{field} must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None:
        raise ContractError(f"{field} must include a timezone")
    return parsed


def validate_document(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ContractError("input must be a JSON object")
    mode = document.get("mode")
    if mode not in {"project", "overview"}:
        raise ContractError("mode must be project or overview")
    collection = "tasks" if mode == "project" else "projects"
    if not isinstance(document.get(collection, []), list):
        raise ContractError(f"{collection} must be an array")
    if mode == "project":
        for field in ("project_name", "key"):
            if not isinstance(document.get(field, ""), str):
                raise ContractError(f"{field} must be a string")
        velocity(document.get("tasks", []))
    if "as_of" in document:
        parse_timestamp(document["as_of"], "as_of")
    return document


def age_label(value: Any, as_of: datetime) -> str:
    if value is None:
        return "—"
    timestamp = parse_timestamp(value, "task date")
    delta = as_of.astimezone(timezone.utc) - timestamp.astimezone(timezone.utc)
    return f"{max(0, delta.days)}d"


def line(left: str = "", right: str = "") -> str:
    inner = WIDTH - 4
    if right:
        right = fit(right, inner).rstrip()
        room = max(1, inner - display_width(right) - 1)
        body = fit(left, room) + " " + right
    else:
        body = fit(left, inner)
    return f"│ {body} │"


def frame(lines: list[str]) -> str:
    return "\n".join(["┌" + "─" * (WIDTH - 2) + "┐", *lines, "└" + "─" * (WIDTH - 2) + "┘"])


def render_project(document: dict[str, Any], as_of: datetime) -> str:
    tasks = document.get("tasks", [])
    done, total = velocity(tasks)
    progress = 0 if total == 0 else round(done / total * 100)
    lines = [
        line(f"{document.get('project_name', '')} [{document.get('key', '')}]", as_of.isoformat()),
        line(),
        line(f"Velocity  {bar(done, total)}  {done}/{total} points ({progress}%)"),
        line(),
        line("Executable Tasks", f"{len([task for task in tasks if task['level'] == 'Task'])}"),
    ]
    for task in tasks:
        if task["level"] != "Task":
            continue
        marker = "✓" if task["status"] == "Done" else "×" if task["status"] == "Won't Do" else "•"
        details = f"{task['status']} · {task['points']}pt"
        if task["status"] == "Blocked":
            details += f" · blocked {age_label(task.get('start_date'), as_of)}"
        lines.append(line(f"{marker} {task.get('issue_key', task['id'])} {task['name']}", details))
        children = [child for child in tasks if child.get("parent_id") == task["id"]]
        for child in children:
            lines.append(line(f"  ↳ {child['name']}", f"{child['points']}pt decomposition"))
    return frame(lines)


def render_overview(document: dict[str, Any], as_of: datetime) -> str:
    lines = [line("DevLab Overview", as_of.isoformat()), line()]
    projects = document.get("projects", [])
    if not projects:
        lines.append(line("No active projects"))
    for project in projects:
        name = project.get("project_name", project.get("name", "Unnamed"))
        tasks = project.get("tasks", [])
        done, total = velocity(tasks)
        lines.append(line(name, f"{bar(done, total, 12)} {done}/{total}pt"))
    return frame(lines)


def main() -> int:
    try:
        document = validate_document(json.load(sys.stdin))
        as_of = parse_timestamp(document["as_of"], "as_of") if "as_of" in document else datetime.now().astimezone()
        output = render_project(document, as_of) if document["mode"] == "project" else render_overview(document, as_of)
    except json.JSONDecodeError as error:
        print(f"DevLab dashboard input error: malformed JSON at line {error.lineno}, column {error.colno}", file=sys.stderr)
        return 2
    except (ContractError, KeyError, TypeError) as error:
        print(f"DevLab dashboard input error: {error}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
