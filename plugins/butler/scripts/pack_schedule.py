#!/usr/bin/env python3
"""
pack_schedule.py — deterministic day packer for the `butler` planning skills.

Places a target day's work chunks into the free time of a work window, around
fixed commitments, applying transition buffers, recharge breaks, a focus cap,
and a day-slack reserve. Used by `butler:plan` and `butler:reschedule`.

Why a script, not freehand: placing blocks around busy intervals while
respecting buffers, a focus cap, and mode ordering is fiddly and easy to get
subtly wrong by hand. Doing it deterministically keeps the schedule honest and
reproducible.

I/O: reads ONE JSON object (file-path arg or stdin) and writes ONE JSON object
to stdout. Stdlib only — no network, no third-party packages — so it runs
anywhere Python 3.9+ is available. The contract is pinned by
schemas/packer-input.schema.json and schemas/packer-output.schema.json.

Field meanings and the TickTick mapping live in references/template.md; the
reasoning behind the defaults lives in references/heuristics.md (Time-blocking).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

# --- Defaults. Every value is overridable via the input "config" block. -------
# These mirror the skill's config defaults; the script never assumes a user.
DEFAULTS = {
    # Longest single focus block before a break is expected. ~50 min sits
    # between a Pomodoro (25) and an ultradian dip (~90); good for dev work.
    "max_block_min": 50,
    # Gap left after each block for context-switching/notes. Transitions are
    # where unbuffered schedules quietly fall apart.
    "transition_min": 10,
    # A real recharge break after this many consecutive focus blocks.
    "recharge_after_blocks": 2,
    "recharge_min": 15,
    # Share of the free window left unscheduled for interrupts and overrun.
    "day_slack_pct": 20,
    # Hard ceiling on committed focus minutes per day.
    "focus_cap_min": 270,
    # More than this many substantial musts is a flag, not a plan.
    "max_musts": 3,
    # Place deep-mode chunks in the earliest (freshest) slots; batch comms/review.
    "deep_first": True,
    # Pomodoro length, used only to suggest a TickTick pomo estimate per chunk.
    "pomo_len_min": 25,
}

PRIORITY_RANK = {"must": 0, "should": 1, "want": 2}
# deep_first True -> deep pulled earliest, comms/review batched last.
MODE_RANK_DEEP_FIRST = {"deep": 0, "shallow": 1, "review": 2, "comms": 3}
MODE_RANK_FLAT = {"deep": 1, "shallow": 1, "review": 0, "comms": 0}

# Overflow reasons, defined once so the skill and tests can match on them.
NO_ESTIMATE = "no estimate; set one during planning"
NO_FREE_TIME = "no free time in the window today"
OVER_CAP = "exceeds today's focus cap"
NO_SLOT = "no free slot long enough today"


@dataclass
class Interval:
    start: datetime
    end: datetime

    @property
    def minutes(self) -> int:
        return minutes_between(self.start, self.end)


def minutes_between(a: datetime, b: datetime) -> int:
    return int((b - a).total_seconds() // 60)


def parse_dt(value: str) -> datetime:
    """Parse an ISO-8601 string. Require a timezone offset so blocks are unambiguous."""
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError(f"datetime must include a timezone offset: {value!r}")
    return dt


def window_bounds(now: datetime, window: dict):
    """window['start']/['end'] are 'HH:MM' on the same date/tz as `now`.

    The script assumes fixed-offset, same-day inputs (the Calendar mapping
    guarantees this): a commitment dated on another day is simply ignored.
    """
    def at(hhmm: str) -> datetime:
        h, m = (int(x) for x in hhmm.split(":"))
        return now.replace(hour=h, minute=m, second=0, microsecond=0)

    start, end = at(window["start"]), at(window["end"])
    if end <= start:
        raise ValueError("window end must be after window start")
    return start, end


def free_intervals(now, win_start, win_end, busy):
    """Window minus busy intervals, never starting before `now` (so a reschedule
    from mid-day just works)."""
    cursor = max(now, win_start)
    busy_sorted = sorted(
        (Interval(parse_dt(b["start"]), parse_dt(b["end"])) for b in busy),
        key=lambda i: i.start,
    )
    free = []
    for b in busy_sorted:
        if b.end <= cursor or b.start >= win_end:
            continue
        if b.start > cursor:
            free.append(Interval(cursor, min(b.start, win_end)))
        cursor = max(cursor, b.end)
    if cursor < win_end:
        free.append(Interval(cursor, win_end))
    return [iv for iv in free if iv.minutes > 0]


def order_chunks(chunks, deep_first):
    """Priority, then mode (energy), then larger-first, then id for a fully
    deterministic order independent of input list order."""
    mode_rank = MODE_RANK_DEEP_FIRST if deep_first else MODE_RANK_FLAT

    def key(c):
        return (
            PRIORITY_RANK.get(c.get("priority", "should"), 1),
            mode_rank.get(c.get("mode", "deep"), 1),
            -int(c.get("estimate_min", 0) or 0),
            str(c.get("id", "")),
        )

    return sorted(chunks, key=key)


def find_slot(frees, start_idx: int, start_cursor: Optional[datetime], minutes: int):
    """Earliest (interval_index, block_start) at or after (start_idx, start_cursor)
    that can hold `minutes`. Pure — mutates nothing — so a chunk that fits
    nowhere never strands the chunks after it. Returns None if nothing fits."""
    i = start_idx
    cursor = start_cursor
    while i < len(frees):
        iv = frees[i]
        block_start = iv.start if cursor is None or cursor < iv.start else cursor
        if minutes_between(block_start, iv.end) >= minutes:
            return i, block_start
        i += 1
        cursor = None
    return None


def brief(c: dict) -> dict:
    return {
        "id": c.get("id"),
        "title": c.get("title"),
        "ticket": c.get("ticket"),
        "mode": c.get("mode"),
        "priority": c.get("priority"),
        "estimate_min": c.get("estimate_min"),
    }


def pack(data: dict) -> dict:
    cfg = {**DEFAULTS, **(data.get("config") or {})}
    now = parse_dt(data["now"])
    win_start, win_end = window_bounds(now, data["window"])
    frees = free_intervals(now, win_start, win_end, data.get("fixed_commitments") or [])

    total_free = sum(iv.minutes for iv in frees)
    slack_reserve = int(total_free * cfg["day_slack_pct"] / 100)
    effective_cap = max(min(cfg["focus_cap_min"], total_free - slack_reserve), 0)

    ordered = order_chunks(data.get("chunks") or [], cfg["deep_first"])

    scheduled, breaks, overflow, warnings = [], [], [], []

    musts = [c for c in ordered if c.get("priority") == "must"]
    if len(musts) > cfg["max_musts"]:
        warnings.append(
            f"{len(musts)} musts today; more than {cfg['max_musts']} substantial "
            "musts rarely all land — consider demoting some to 'should'."
        )

    # Lay chunks out strictly in sequence so clock order == priority/mode order.
    # Crossing into a new free interval (i.e. past a meeting) resets the focus
    # run, since the meeting was itself a break.
    focus_used = 0
    consecutive = 0
    idx = 0
    cursor = frees[0].start if frees else None

    for c in ordered:
        est = int(c.get("estimate_min", 0) or 0)
        if est <= 0:
            overflow.append({**brief(c), "reason": NO_ESTIMATE})
            continue
        if total_free <= 0:
            overflow.append({**brief(c), "reason": NO_FREE_TIME})
            continue
        if focus_used + est > effective_cap:
            overflow.append({**brief(c), "reason": OVER_CAP})
            continue
        slot = find_slot(frees, idx, cursor, est)
        if slot is None:
            overflow.append({**brief(c), "reason": NO_SLOT})
            continue

        new_idx, block_start = slot
        if new_idx != idx:
            consecutive = 0  # we crossed a gap/meeting -> it served as the break
        idx = new_idx
        iv = frees[idx]
        block = Interval(block_start, block_start + timedelta(minutes=est))
        focus_used += est
        scheduled.append({
            **brief(c),
            "block": {"start": block.start.isoformat(), "end": block.end.isoformat()},
            "pomo_estimate": max(1, round(est / cfg["pomo_len_min"])),
        })

        consecutive += 1
        if consecutive >= cfg["recharge_after_blocks"]:
            buf = cfg["recharge_min"]
            # Only materialize the break if it fits before this interval ends;
            # otherwise the upcoming interval boundary already serves as the break.
            if minutes_between(block.end, iv.end) >= buf:
                breaks.append({
                    "start": block.end.isoformat(),
                    "end": (block.end + timedelta(minutes=buf)).isoformat(),
                    "kind": "recharge",
                })
            consecutive = 0
        else:
            buf = cfg["transition_min"]
        cursor = block.end + timedelta(minutes=buf)

    musts_overflowed = [o for o in overflow if o.get("priority") == "must"]
    if musts_overflowed:
        warnings.append(
            f"{len(musts_overflowed)} MUST chunk(s) could not fit today and are "
            "surfaced as overflow — never silently dropped. Make them smaller, "
            "free up the window, or move them to the next day deliberately."
        )
    if overflow:
        warnings.append(
            f"{len(overflow)} chunk(s) did not fit today — they stay unscheduled "
            "for a later day, not dropped."
        )

    summary = {
        "focus_min_scheduled": focus_used,
        "focus_cap_min": effective_cap,
        "window_free_min": total_free,
        "slack_reserved_min": slack_reserve,
        "musts_scheduled": sum(1 for s in scheduled if s.get("priority") == "must"),
        "packed_pct": round(100 * focus_used / total_free) if total_free else 0,
        "warnings": warnings,
    }
    return {"scheduled": scheduled, "breaks": breaks, "overflow": overflow, "summary": summary}


def main(argv) -> int:
    raw = open(argv[1]).read() if len(argv) > 1 else sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"invalid JSON input: {e}"}), file=sys.stderr)
        return 2
    try:
        result = pack(data)
    except (KeyError, ValueError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
