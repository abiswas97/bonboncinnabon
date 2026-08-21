#!/usr/bin/env python3
"""Provider-neutral DevLab domain and configuration contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

TERMINAL = {"Done", "Won't Do"}
LEVELS = {"Epic", "Task", "Sub-task"}
POINTS = {1, 2, 3, 5}
REQUIRED_NOTION_CAPABILITIES = {"search", "fetch", "query", "create", "update"}
TRANSITIONS = json.loads((Path(__file__).parents[1] / "domain/transitions.json").read_text())
STATUSES = set(TRANSITIONS)


class ContractError(ValueError):
    pass


def require_capabilities(available: set[str], required: set[str] | None = None) -> None:
    missing = sorted((required or REQUIRED_NOTION_CAPABILITIES) - available)
    if missing:
        raise ContractError(f"authenticated Notion connector is missing: {', '.join(missing)}")


def transition_kind(source: str, target: str) -> str:
    if source not in TRANSITIONS:
        raise ContractError(f"unknown source status: {source}")
    for kind in ("normal", "confirmation"):
        if target in TRANSITIONS[source][kind]:
            return kind
    raise ContractError(f"transition rejected: {source} -> {target}")


def transition_effects(task: dict[str, Any], target: str, today: str, blocker_ids: list[str] | None = None) -> dict[str, Any]:
    source = task.get("status")
    transition_kind(source, target)
    result = {"Status": target}
    if target == "In Progress" and not task.get("start_date"):
        result["Start Date"] = today
    if target in TERMINAL:
        result["End Date"] = today
    elif source in TERMINAL:
        result["End Date"] = None
    if target == "Blocked":
        if not blocker_ids:
            raise ContractError("entering Blocked requires at least one blocker relation")
        result["Blocked By"] = blocker_ids
    elif source == "Blocked":
        result["Blocked By"] = []
    return result


def validate_hierarchy(tasks: list[dict[str, Any]]) -> None:
    by_id = {task.get("id"): task for task in tasks}
    if len(by_id) != len(tasks) or None in by_id:
        raise ContractError("task IDs must be present and unique")
    children: dict[str, list[dict[str, Any]]] = {task_id: [] for task_id in by_id}
    for task in tasks:
        level = task.get("level")
        points = task.get("points")
        if not isinstance(task.get("name"), str) or not task["name"]:
            raise ContractError(f"{task['id']}: name must be a non-empty string")
        if level not in LEVELS:
            raise ContractError(f"{task['id']}: invalid level {level}")
        if task.get("status") not in STATUSES:
            raise ContractError(f"{task['id']}: invalid status {task.get('status')}")
        if level == "Epic" and points is not None:
            raise ContractError(f"{task['id']}: Epics cannot have story points")
        if level != "Epic" and (not isinstance(points, int) or isinstance(points, bool) or points not in POINTS):
            raise ContractError(f"{task['id']}: Tasks and Sub-tasks require 1, 2, 3, or 5 points")
        blocked_by = task.get("blocked_by")
        if not isinstance(blocked_by, list) or not all(isinstance(item, str) and item for item in blocked_by):
            raise ContractError(f"{task['id']}: blocked_by must be a list of task IDs")
        if task["status"] == "Blocked" and not blocked_by:
            raise ContractError(f"{task['id']}: Blocked task requires a blocker relation")
        if task["status"] != "Blocked" and blocked_by:
            raise ContractError(f"{task['id']}: non-Blocked task cannot retain an active blocker relation")
        parent_id = task.get("parent_id")
        if level == "Epic" and parent_id is not None:
            raise ContractError(f"{task['id']}: Epic cannot have a parent")
        if level == "Sub-task" and parent_id is None:
            raise ContractError(f"{task['id']}: Sub-task requires a Task parent")
        if parent_id is not None:
            parent = by_id.get(parent_id)
            if parent is None:
                raise ContractError(f"{task['id']}: missing parent {parent_id}")
            expected = {"Task": "Epic", "Sub-task": "Task"}.get(level)
            if parent.get("level") != expected:
                raise ContractError(f"{task['id']}: {level} must have a {expected} parent")
            children[parent_id].append(task)
    for task in tasks:
        descendants = _descendants(task["id"], children)
        if task["level"] == "Sub-task" and descendants:
            raise ContractError(f"{task['id']}: Sub-task cannot have children")
        if task.get("status") in TERMINAL and any(child.get("status") not in TERMINAL for child in descendants):
            raise ContractError(f"{task['id']}: terminal parent has a non-terminal descendant")
        direct = children[task["id"]]
        if task["level"] == "Task" and direct and sum(child["points"] for child in direct) != task["points"]:
            raise ContractError(f"{task['id']}: Sub-task points must equal the Task's points")


def _descendants(task_id: str, children: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for child in children[task_id]:
        result.append(child)
        result.extend(_descendants(child["id"], children))
    return result


def closure_targets(task_id: str, tasks: list[dict[str, Any]], recursive: bool) -> list[str]:
    validate_hierarchy(tasks)
    by_id = {task["id"]: task for task in tasks}
    if task_id not in by_id:
        raise ContractError(f"unknown task: {task_id}")
    children = {item_id: [] for item_id in by_id}
    for task in tasks:
        if task.get("parent_id"):
            children[task["parent_id"]].append(task)
    open_descendants = [task for task in _descendants(task_id, children) if task["status"] not in TERMINAL]
    if open_descendants and not recursive:
        raise ContractError("parent cannot close while descendants are open")
    return [task["id"] for task in open_descendants] + [task_id]


def velocity(tasks: list[dict[str, Any]]) -> tuple[int, int]:
    validate_hierarchy(tasks)
    planning_tasks = [task for task in tasks if task["level"] == "Task"]
    return sum(task["points"] for task in planning_tasks if task["status"] == "Done"), sum(task["points"] for task in planning_tasks)


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("schema_version") != 1:
        raise ContractError("schema_version must be 1")
    if not isinstance(config.get("project_name"), str) or not config["project_name"].strip():
        raise ContractError("project_name must be a non-empty string")
    notion = config.get("notion")
    if not isinstance(notion, dict):
        raise ContractError("notion must be a mapping")
    for key in ("project_page", "tasks_db", "task_template"):
        if not isinstance(notion.get(key), str) or not notion[key].strip():
            raise ContractError(f"notion.{key} must be a non-empty string")
        try:
            UUID(notion[key])
        except ValueError as error:
            raise ContractError(f"notion.{key} must be a UUID") from error
    if notion.get("product_spec") is not None and not isinstance(notion["product_spec"], str):
        raise ContractError("notion.product_spec must be a string or null")
    if notion.get("product_spec") is not None:
        try:
            UUID(notion["product_spec"])
        except ValueError as error:
            raise ContractError("notion.product_spec must be a UUID or null") from error
    sources = config.get("sync", {}).get("sources")
    if not isinstance(sources, list) or not all(isinstance(source, str) and source for source in sources):
        raise ContractError("sync.sources must be a list of non-empty paths")
    return config


def parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    lines = text.splitlines()
    for index, raw in enumerate(lines):
        number = index + 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        content = raw.strip()
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if content.startswith("- "):
            if not isinstance(parent, list):
                raise ContractError(f"line {number}: list item outside a list")
            parent.append(_scalar(content[2:]))
            continue
        if ":" not in content or not isinstance(parent, dict):
            raise ContractError(f"line {number}: unsupported YAML")
        key, raw_value = content.split(":", 1)
        key, raw_value = key.strip(), raw_value.strip()
        if not raw_value:
            following_is_list = False
            for following in lines[index + 1:]:
                if not following.strip() or following.lstrip().startswith("#"):
                    continue
                following_indent = len(following) - len(following.lstrip(" "))
                following_is_list = following_indent > indent and following.strip().startswith("- ")
                break
            value: Any = [] if following_is_list else {}
            parent[key] = value
            stack.append((indent, value))
        else:
            parent[key] = _scalar(raw_value)
    return root


def _scalar(value: str) -> Any:
    if value in {"null", "~"}:
        return None
    if value.isdigit():
        return int(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def migrated_config(legacy: dict[str, Any]) -> dict[str, Any]:
    config = {
        "schema_version": 1,
        "project_name": legacy.get("project_name"),
        "notion": legacy.get("notion"),
        "sync": legacy.get("sync", {"sources": ["AGENTS.md", "CLAUDE.md", "openspec/", "docs/plans/"]}),
    }
    return validate_config(config)


def dump_config(config: dict[str, Any]) -> str:
    notion = config["notion"]
    lines = [
        "schema_version: 1",
        f"project_name: {json.dumps(config['project_name'])}",
        "notion:",
        f"  project_page: {json.dumps(notion['project_page'])}",
        f"  product_spec: {json.dumps(notion['product_spec']) if notion['product_spec'] is not None else 'null'}",
        f"  tasks_db: {json.dumps(notion['tasks_db'])}",
        f"  task_template: {json.dumps(notion['task_template'])}",
        "sync:",
        "  sources:",
    ]
    lines.extend(f"    - {source}" for source in config["sync"]["sources"])
    return "\n".join(lines) + "\n"
