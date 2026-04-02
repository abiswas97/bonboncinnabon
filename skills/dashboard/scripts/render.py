#!/usr/bin/env python3
"""DevLab dashboard renderer. Reads JSON from stdin, outputs ASCII dashboard."""

import json
import sys
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

W = 62


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
        return "\u2591" * width
    n = round(filled / total * width)
    return "\u2593" * n + "\u2591" * (width - n)


def row(content):
    """Pad or truncate content to W and wrap with box borders."""
    return "\u2551" + content.ljust(W)[:W] + "\u2551"


def hdr(left, right=""):
    """Row with left-aligned and optional right-aligned text (1-char margin)."""
    if right:
        gap = W - len(left) - len(right) - 1
        return row(left + " " * max(gap, 1) + right + " ")
    return row(left)


def sep_top():
    return "\u2554" + "\u2550" * W + "\u2557"


def sep_mid():
    return "\u2560" + "\u2550" * W + "\u2563"


def sep_bot():
    return "\u255a" + "\u2550" * W + "\u255d"


def blank():
    return row("")


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

    lines = [
        sep_top(),
        hdr(f"  DEVLAB :: {name} ({key})", today),
        sep_mid(),
        blank(),
    ]

    prog_bar = bar(done_count, total_tasks, 10)
    type_str = "  ".join(f"{k}: {v}" for k, v in sorted(types.items()))
    lines.append(row("  PROGRESS            VELOCITY         BREAKDOWN"))
    lines.append(row(f"  {prog_bar} {done_count}/{total_tasks:<5}  {avg_vel:.1f} pts/wk avg     {type_str[:20]}"))
    lines.append(row(f"  {pct}% complete        Last: {last_vel} pts"))
    lines.append(row(f"  {done_pts} of {total_pts} pts done"))
    lines.append(blank())

    lines.append(row("  ACTIVE NOW"))
    if active:
        for t in active[:5]:
            ik = t.get("issue_key", "???")
            tn = t.get("name", "")[:30]
            pts = t.get("story_points", "?")
            lines.append(row(f"  {ik:<8} {tn:<30} {pts}pts  In Progress"))
            for st in t.get("sub_tasks", []):
                sik = st.get("issue_key", "")
                stn = st.get("name", "")[:26]
                spts = st.get("story_points", "?")
                sst = st.get("status", "")
                mark = "\u25cf" if sst == "Done" else "\u25cc"
                lines.append(row(f"    \u2514\u2500 {sik}  {mark} {stn:<26} {spts}pt  {sst}"))
    else:
        lines.append(row("  (none)"))
    lines.append(blank())

    if blocked:
        lines.append(row("  BLOCKED"))
        for t in blocked[:3]:
            ik = t.get("issue_key", "???")
            tn = t.get("name", "")[:30]
            pts = t.get("story_points", "?")
            bb = t.get("blocked_by", "unknown")
            lines.append(row(f"  {ik:<8} {tn:<30} {pts}pt  Blocked by {bb}"))
        lines.append(blank())

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
        lines.append(row("  ATTENTION NEEDED"))
        for a in attention[:3]:
            lines.append(row(f"  {a}"))
        lines.append(blank())

    courses = data.get("courses", 0)
    papers = data.get("papers", 0)
    resources = data.get("resources", 0)
    if courses or papers or resources:
        lines.append(row("  LEARNING & RESOURCES"))
        lines.append(row(f"  Courses: {courses}  Papers: {papers}  Resources: {resources}"))
        lines.append(blank())

    lines.append(sep_bot())
    return "\n".join(lines)


def render_overview(data):
    """Render cross-project overview dashboard."""
    projects = data.get("projects", [])
    knowledge = data.get("knowledge", {})
    today = datetime.now().strftime("%Y-%m-%d")

    col_w = [10, 8, 7, 6, 7, 9]
    col_names = ["Project", "Status", "Tasks", "Done", "Pts", "Blocked"]
    tbl_w = sum(col_w) + len(col_w) + 1

    def tbl_sep(left, mid, right, fill="\u2500"):
        return left + mid.join(fill * c for c in col_w) + right

    def tbl_row(vals):
        cells = "\u2502".join(f"{v:<{col_w[i]}}" for i, v in enumerate(vals))
        return "\u2502" + cells + "\u2502"

    lines = [
        sep_top(),
        hdr(f"  DEVLAB :: All Projects", today),
        sep_mid(),
        blank(),
        row("  PROJECT HEALTH"),
        row("  " + tbl_sep("\u250c", "\u252c", "\u2510")),
        row("  " + tbl_row(col_names)),
        row("  " + tbl_sep("\u251c", "\u253c", "\u2524")),
    ]

    for p in projects:
        pn = p.get("name", "?")[:10]
        ps = p.get("status", "?")[:8]
        tt = str(p.get("total_tasks", 0))
        td = str(p.get("done_tasks", 0))
        tp = f"{p.get('done_pts', 0)}/{p.get('total_pts', 0)}"
        bl = str(p.get("blocked", 0))
        lines.append(row("  " + tbl_row([pn, ps, tt, td, tp, bl])))

    lines.append(row("  " + tbl_sep("\u2514", "\u2534", "\u2518")))
    lines.append(blank())

    lines.append(row("  VELOCITY (last 4 weeks)"))
    for p in projects:
        pn = p.get("name", "?")[:10]
        vel = p.get("velocity_total", 0)
        vbar = bar(vel, max(p.get("total_pts", 1), 1), 10)
        lines.append(row(f"  {pn:<10} {vbar}  {vel}pts"))
    lines.append(blank())

    kr = knowledge.get("resources", 0)
    kc = knowledge.get("courses", 0)
    kp = knowledge.get("papers", 0)
    kt = knowledge.get("tech_stack", 0)
    lines.append(row("  KNOWLEDGE BASE"))
    lines.append(row(f"  {kr} resources  {kc} courses  {kp} papers  {kt} tech stack items"))
    lines.append(blank())

    attention = data.get("attention", [])
    if attention:
        lines.append(row("  ATTENTION NEEDED"))
        for a in attention[:5]:
            lines.append(row(f"  {a}"))
        lines.append(blank())

    lines.append(sep_bot())
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
