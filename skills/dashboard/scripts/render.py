#!/usr/bin/env python3
"""DevLab dashboard renderer. Reads JSON from stdin, outputs ASCII dashboard."""

import json
import sys
import argparse
from datetime import datetime, timedelta
from collections import defaultdict


def parse_date(s):
    """Parse ISO date string, return datetime or None."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None


def compute_velocity(tasks, weeks=4):
    """Compute points completed per week over last N weeks."""
    now = datetime.now()
    weekly = []
    for w in range(weeks):
        start = now - timedelta(weeks=w + 1)
        end = now - timedelta(weeks=w)
        pts = sum(
            t.get("story_points", 0) or 0
            for t in tasks
            if t.get("status") == "Done"
            and start <= (parse_date(t.get("end_date")) or datetime.min) < end
        )
        weekly.append(pts)
    weekly.reverse()
    return weekly


def bar(filled, total, width=10):
    """Render a progress bar."""
    if total == 0:
        return "░" * width
    n = round(filled / total * width)
    return "▓" * n + "░" * (width - n)


def render_project(data):
    """Render per-project dashboard."""
    name = data.get("name", "Unknown")
    key = data.get("key", "???")
    tasks = data.get("tasks", [])
    today = datetime.now().strftime("%Y-%m-%d")

    done = [t for t in tasks if t.get("status") == "Done"]
    active = [t for t in tasks if t.get("status") == "In Progress"]
    blocked = [t for t in tasks if t.get("status") == "Blocked"]

    total_tasks = len(tasks)
    done_count = len(done)
    total_pts = sum(t.get("story_points", 0) or 0 for t in tasks)
    done_pts = sum(t.get("story_points", 0) or 0 for t in done)

    velocity = compute_velocity(tasks)
    avg_vel = sum(velocity) / len(velocity) if velocity else 0
    last_vel = velocity[-1] if velocity else 0

    types = defaultdict(int)
    for t in tasks:
        types[t.get("type", "Other")] += 1

    pct = round(done_count / total_tasks * 100) if total_tasks else 0

    w = 62
    lines = []
    lines.append("╔" + "═" * w + "╗")
    lines.append(f"║  DEVLAB :: {name} ({key}){' ' * (w - 16 - len(name) - len(key) - len(today))}{today}  ║")
    lines.append("╠" + "═" * w + "╣")
    lines.append("║" + " " * w + "║")

    prog_bar = bar(done_count, total_tasks, 10)
    type_str = "  ".join(f"{k}: {v}" for k, v in sorted(types.items()))
    lines.append(f"║  PROGRESS            VELOCITY         BREAKDOWN{' ' * (w - 49)}║")
    lines.append(f"║  {prog_bar} {done_count}/{total_tasks:<5}  {avg_vel:.1f} pts/wk avg     {type_str[:20]:<20} ║")
    lines.append(f"║  {pct}% complete        Last: {last_vel} pts{' ' * (w - 40)}║")
    lines.append(f"║  {done_pts} of {total_pts} pts done{' ' * (w - 20 - len(str(done_pts)) - len(str(total_pts)))}║")
    lines.append("║" + " " * w + "║")

    lines.append(f"║  ACTIVE NOW{' ' * (w - 11)}║")
    if active:
        for t in active[:5]:
            ik = t.get("issue_key", "???")
            tn = t.get("name", "")[:30]
            pts = t.get("story_points", "?")
            line = f"  {ik:<8} {tn:<30} {pts}pts  In Progress"
            lines.append(f"║{line:<{w}}║")
            for st in t.get("sub_tasks", []):
                sik = st.get("issue_key", "")
                stn = st.get("name", "")[:26]
                spts = st.get("story_points", "?")
                sst = st.get("status", "")
                mark = "●" if sst == "Done" else "◌"
                sub_line = f"    └─ {sik}  {mark} {stn:<26} {spts}pt  {sst}"
                lines.append(f"║{sub_line:<{w}}║")
    else:
        lines.append(f"║  (none){' ' * (w - 8)}║")
    lines.append("║" + " " * w + "║")

    if blocked:
        lines.append(f"║  BLOCKED{' ' * (w - 9)}║")
        for t in blocked[:3]:
            ik = t.get("issue_key", "???")
            tn = t.get("name", "")[:30]
            pts = t.get("story_points", "?")
            bb = t.get("blocked_by", "unknown")
            line = f"  {ik:<8} {tn:<30} {pts}pt  Blocked by {bb}"
            lines.append(f"║{line:<{w}}║")
        lines.append("║" + " " * w + "║")

    now = datetime.now()
    attention = []
    for t in blocked:
        edited = parse_date(t.get("last_edited"))
        if edited and (now - edited).days >= 2:
            attention.append(f"! {t.get('issue_key', '???')}  Blocked {(now - edited).days}d")
    for t in active:
        edited = parse_date(t.get("last_edited"))
        if edited and (now - edited).days >= 5:
            attention.append(f"! {t.get('issue_key', '???')}  Stale {(now - edited).days}d (no update)")

    if attention:
        lines.append(f"║  ATTENTION NEEDED{' ' * (w - 17)}║")
        for a in attention[:3]:
            lines.append(f"║  {a:<{w - 2}}║")
        lines.append("║" + " " * w + "║")

    courses = data.get("courses", 0)
    papers = data.get("papers", 0)
    resources = data.get("resources", 0)
    if courses or papers or resources:
        learn = f"Courses: {courses}  Papers: {papers}  Resources: {resources}"
        lines.append(f"║  LEARNING & RESOURCES{' ' * (w - 21)}║")
        lines.append(f"║  {learn:<{w - 2}}║")
        lines.append("║" + " " * w + "║")

    lines.append("╚" + "═" * w + "╝")
    return "\n".join(lines)


def render_overview(data):
    """Render cross-project overview dashboard."""
    projects = data.get("projects", [])
    knowledge = data.get("knowledge", {})
    today = datetime.now().strftime("%Y-%m-%d")

    w = 62
    lines = []
    lines.append("╔" + "═" * w + "╗")
    lines.append(f"║  DEVLAB :: All Projects{' ' * (w - 23 - len(today))}{today}  ║")
    lines.append("╠" + "═" * w + "╣")
    lines.append("║" + " " * w + "║")

    lines.append(f"║  PROJECT HEALTH{' ' * (w - 15)}║")
    lines.append(f"║  ┌{'─' * 10}┬{'─' * 8}┬{'─' * 7}┬{'─' * 6}┬{'─' * 7}┬{'─' * 9}┐{' ' * (w - 52)}║")
    lines.append(f"║  │{'Project':<10}│{'Status':<8}│{'Tasks':<7}│{'Done':<6}│{'Pts':<7}│{'Blocked':<9}│{' ' * (w - 52)}║")
    lines.append(f"║  ├{'─' * 10}┼{'─' * 8}┼{'─' * 7}┼{'─' * 6}┼{'─' * 7}┼{'─' * 9}┤{' ' * (w - 52)}║")

    for p in projects:
        pn = p.get("name", "?")[:10]
        ps = p.get("status", "?")[:8]
        tt = p.get("total_tasks", 0)
        td = p.get("done_tasks", 0)
        tp = f"{p.get('done_pts', 0)}/{p.get('total_pts', 0)}"
        bl = p.get("blocked", 0)
        lines.append(f"║  │{pn:<10}│{ps:<8}│{tt:<7}│{td:<6}│{tp:<7}│{bl:<9}│{' ' * (w - 52)}║")

    lines.append(f"║  └{'─' * 10}┴{'─' * 8}┴{'─' * 7}┴{'─' * 6}┴{'─' * 7}┴{'─' * 9}┘{' ' * (w - 52)}║")
    lines.append("║" + " " * w + "║")

    lines.append(f"║  VELOCITY (last 4 weeks){' ' * (w - 24)}║")
    for p in projects:
        pn = p.get("name", "?")[:10]
        vel = p.get("velocity_total", 0)
        vbar = bar(vel, max(p.get("total_pts", 1), 1), 10)
        lines.append(f"║  {pn:<10} {vbar}  {vel}pts{' ' * (w - 28 - len(str(vel)))}║")
    lines.append("║" + " " * w + "║")

    kr = knowledge.get("resources", 0)
    kc = knowledge.get("courses", 0)
    kp = knowledge.get("papers", 0)
    kt = knowledge.get("tech_stack", 0)
    kb_line = f"{kr} resources  {kc} courses  {kp} papers  {kt} tech stack items"
    lines.append(f"║  KNOWLEDGE BASE{' ' * (w - 15)}║")
    lines.append(f"║  {kb_line:<{w - 2}}║")
    lines.append("║" + " " * w + "║")

    attention = data.get("attention", [])
    if attention:
        lines.append(f"║  ATTENTION NEEDED{' ' * (w - 17)}║")
        for a in attention[:5]:
            lines.append(f"║  {a:<{w - 2}}║")
        lines.append("║" + " " * w + "║")

    lines.append("╚" + "═" * w + "╝")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="DevLab dashboard renderer")
    parser.add_argument("--mode", choices=["project", "overview"], required=True)
    parser.add_argument("--name", default="Unknown")
    parser.add_argument("--key", default="???")
    args = parser.parse_args()

    data = json.load(sys.stdin)

    if args.mode == "project":
        data["name"] = args.name
        data["key"] = args.key
        print(render_project(data))
    else:
        print(render_overview(data))


if __name__ == "__main__":
    main()
