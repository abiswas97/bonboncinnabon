#!/usr/bin/env python3
"""Tests for pack_schedule. Stdlib unittest only — run:

    python3 -m unittest test_pack_schedule        (from this dir)
    python3 scripts/test_pack_schedule.py          (from the plugin root)

They pin the load-bearing invariants: window validation, mid-day reschedule,
free-interval math around commitments, the recharge-never-overlaps guarantee,
focus-cap/slack math, deterministic ordering, and the two regressions that the
review caught (the strand bug and "a must is never silently dropped").
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pack_schedule as ps  # noqa: E402

TZ = "+05:30"


def t(hhmm):
    """An ISO datetime on 2026-06-02 at HH:MM in +05:30."""
    return f"2026-06-02T{hhmm}:00{TZ}"


def chunk(cid, est, intensity="deep", stage="backend", priority="should", ticket=None):
    c = {"id": cid, "title": cid, "intensity": intensity, "stage": stage,
         "priority": priority, "estimate_min": est}
    if ticket:
        c["ticket"] = ticket
    return c


def make_input(chunks, busy=None, window=("14:00", "21:00"), now=None, config=None):
    data = {
        "now": now or t(window[0]),
        "timezone": "Asia/Kolkata",
        "window": {"start": window[0], "end": window[1]},
        "fixed_commitments": busy or [],
        "chunks": chunks,
    }
    if config is not None:
        data["config"] = config
    return data


def busy(start, end, title="Meeting"):
    return {"title": title, "start": t(start), "end": t(end)}


def ids(items):
    return [i["id"] for i in items]


class WindowAndTime(unittest.TestCase):
    def test_window_end_not_after_start_raises(self):
        for win in [("21:00", "14:00"), ("14:00", "14:00")]:
            with self.assertRaises(ValueError):
                ps.pack(make_input([chunk("a", 30)], window=win))

    def test_naive_datetime_rejected(self):
        data = make_input([chunk("a", 30)], now="2026-06-02T14:00:00")  # no offset
        with self.assertRaises(ValueError):
            ps.pack(data)

    def test_now_mid_commitment_starts_after_it(self):
        # now is inside a meeting; placement must begin at the meeting's end.
        res = ps.pack(make_input([chunk("a", 30)], busy=[busy("14:00", "14:45")],
                                 now=t("14:20")))
        self.assertEqual(ids(res["scheduled"]), ["a"])
        self.assertTrue(res["scheduled"][0]["block"]["start"].endswith("14:45:00+05:30"))

    def test_now_after_window_end_all_overflow(self):
        res = ps.pack(make_input([chunk("a", 30)], now=t("22:00")))
        self.assertEqual(res["scheduled"], [])
        self.assertEqual(res["overflow"][0]["reason"], ps.NO_FREE_TIME)


class FreeIntervals(unittest.TestCase):
    def test_back_to_back_commitments_no_zero_gap(self):
        res = ps.pack(make_input(
            [chunk("a", 30)],
            busy=[busy("14:00", "15:00"), busy("15:00", "16:00")],
        ))
        # First free interval is 16:00 onward; the block must start there.
        self.assertTrue(res["scheduled"][0]["block"]["start"].endswith("16:00:00+05:30"))

    def test_commitment_spanning_whole_window(self):
        res = ps.pack(make_input([chunk("a", 30)], busy=[busy("14:00", "21:00")]))
        self.assertEqual(res["scheduled"], [])
        self.assertEqual(res["overflow"][0]["reason"], ps.NO_FREE_TIME)
        self.assertEqual(res["summary"]["window_free_min"], 0)


class Capacity(unittest.TestCase):
    def test_effective_cap_min_of_cap_and_free_minus_slack(self):
        # 7h window = 420 free; 20% slack = 84; cap min(270, 336) = 270.
        res = ps.pack(make_input([chunk("a", 30)]))
        s = res["summary"]
        self.assertEqual(s["window_free_min"], 420)
        self.assertEqual(s["slack_reserved_min"], 84)
        self.assertEqual(s["focus_cap_min"], 270)

    def test_packed_pct_uses_total_free(self):
        res = ps.pack(make_input([chunk("a", 50, priority="must")]))
        self.assertEqual(res["summary"]["packed_pct"], round(100 * 50 / 420))

    def test_zero_or_missing_estimate_overflows(self):
        res = ps.pack(make_input([chunk("a", 0), {"id": "b", "title": "b"}]))
        self.assertEqual(set(ids(res["overflow"])), {"a", "b"})
        for o in res["overflow"]:
            self.assertEqual(o["reason"], ps.NO_ESTIMATE)


class Ordering(unittest.TestCase):
    def test_musts_then_shoulds_then_wants(self):
        res = ps.pack(make_input([
            chunk("w", 30, priority="want"),
            chunk("m", 30, priority="must"),
            chunk("s", 30, priority="should"),
        ]))
        self.assertEqual(ids(res["scheduled"]), ["m", "s", "w"])

    def test_deep_before_shallow_within_priority(self):
        res = ps.pack(make_input([
            chunk("s", 30, intensity="shallow", priority="must"),
            chunk("d", 30, intensity="deep", priority="must"),
        ]))
        self.assertEqual(ids(res["scheduled"]), ["d", "s"])

    def test_activity_clusters_within_intensity(self):
        # same priority + intensity; activity derived from stage orders
        # build < verify < admin.
        res = ps.pack(make_input([
            chunk("admin", 30, stage="deploy", priority="must"),
            chunk("verify", 30, stage="review", priority="must"),
            chunk("build", 30, stage="backend", priority="must"),
        ]))
        self.assertEqual(ids(res["scheduled"]), ["build", "verify", "admin"])

    def test_stage_rank_tiebreak_within_activity(self):
        # same priority + intensity + activity(build); pipeline order decides:
        # backend (rank 2) before frontend (rank 3).
        res = ps.pack(make_input([
            chunk("fe", 30, intensity="deep", stage="frontend", priority="must"),
            chunk("be", 30, intensity="deep", stage="backend", priority="must"),
        ]))
        self.assertEqual(ids(res["scheduled"]), ["be", "fe"])

    def test_stable_for_equal_keys_uses_id(self):
        res = ps.pack(make_input([chunk("b", 30), chunk("a", 30)]))
        self.assertEqual(ids(res["scheduled"]), ["a", "b"])  # id breaks the tie


class Recharge(unittest.TestCase):
    def test_recharge_after_n_consecutive_blocks(self):
        res = ps.pack(make_input(
            [chunk("a", 50, priority="must"), chunk("b", 50, priority="must")],
            config={"recharge_after_blocks": 2, "recharge_min": 15, "day_slack_pct": 0},
        ))
        self.assertEqual(len(res["breaks"]), 1)
        self.assertTrue(res["breaks"][0]["start"].endswith("15:50:00+05:30"))  # after b
        self.assertEqual(res["breaks"][0]["kind"], "recharge")

    def test_recharge_never_overlaps_commitment(self):
        # Two blocks land exactly against a commitment; the break must be dropped,
        # never placed over the meeting.
        res = ps.pack(make_input(
            [chunk("a", 50, priority="must"), chunk("b", 50, priority="must")],
            busy=[busy("15:50", "16:30")],
            config={"recharge_after_blocks": 2, "recharge_min": 15, "day_slack_pct": 0},
        ))
        meeting = ps.Interval(ps.parse_dt(t("15:50")), ps.parse_dt(t("16:30")))
        for b in res["breaks"]:
            bs, be = ps.parse_dt(b["start"]), ps.parse_dt(b["end"])
            self.assertFalse(bs < meeting.end and be > meeting.start, "break overlaps meeting")

    def test_crossing_interval_resets_focus_run(self):
        # A meeting after block 1 resets the run, so the recharge appears only
        # after block 3 (the 2nd consecutive block in the new interval), >=16:00.
        res = ps.pack(make_input(
            [chunk("a", 50, priority="must"), chunk("b", 50, priority="must"),
             chunk("c", 50, priority="must")],
            busy=[busy("14:50", "15:00")],
            config={"recharge_after_blocks": 2, "recharge_min": 15, "day_slack_pct": 0},
        ))
        for b in res["breaks"]:
            self.assertGreaterEqual(ps.parse_dt(b["start"]), ps.parse_dt(t("16:00")))


class MustNeverDropped(unittest.TestCase):
    def test_strand_bug_fixed_small_want_still_scheduled(self):
        # Three 40-min free gaps; an oversized must fits none, a small want fits.
        # The must must NOT strand the want (the regression the review caught).
        res = ps.pack(make_input(
            [chunk("big_must", 90, priority="must"), chunk("small_want", 30, priority="want")],
            busy=[busy("14:40", "15:40"), busy("16:20", "17:20"), busy("18:00", "21:00")],
            config={"focus_cap_min": 500, "day_slack_pct": 0},
        ))
        self.assertIn("small_want", ids(res["scheduled"]))
        self.assertIn("big_must", ids(res["overflow"]))

    def test_overflowed_must_emits_loud_warning(self):
        res = ps.pack(make_input(
            [chunk("big_must", 90, priority="must"), chunk("small_want", 30, priority="want")],
            busy=[busy("14:40", "15:40"), busy("16:20", "17:20"), busy("18:00", "21:00")],
            config={"focus_cap_min": 500, "day_slack_pct": 0},
        ))
        self.assertTrue(any("MUST" in w for w in res["summary"]["warnings"]))


class CoverageGaps(unittest.TestCase):
    def test_empty_chunks_no_crash(self):
        res = ps.pack(make_input([]))
        self.assertEqual(res["scheduled"], [])
        self.assertEqual(res["overflow"], [])
        self.assertEqual(res["breaks"], [])
        self.assertEqual(res["summary"]["packed_pct"], 0)

    def test_more_than_max_musts_warns(self):
        res = ps.pack(make_input([
            chunk("a", 30, priority="must"), chunk("b", 30, priority="must"),
            chunk("c", 30, priority="must"), chunk("d", 30, priority="must"),
        ]))
        self.assertTrue(any("musts today" in w for w in res["summary"]["warnings"]))

    def test_deep_first_false_flattens_intensity(self):
        # With deep_first off, intensity no longer orders; the id tiebreak wins,
        # so shallow "a" precedes deep "z" — the opposite of the default ordering.
        res = ps.pack(make_input(
            [chunk("z", 30, intensity="deep", priority="must"),
             chunk("a", 30, intensity="shallow", priority="must")],
            config={"deep_first": False},
        ))
        self.assertEqual(ids(res["scheduled"]), ["a", "z"])

    def test_recharge_dropped_at_window_end(self):
        # Two blocks fill to within 5 min of the window end (no commitment there);
        # the recharge break can't fit before the boundary, so it is dropped.
        res = ps.pack(make_input(
            [chunk("a", 50, priority="must"), chunk("b", 50, priority="must")],
            window=("14:00", "15:55"),
            config={"recharge_after_blocks": 2, "recharge_min": 15, "day_slack_pct": 0},
        ))
        self.assertEqual(ids(res["scheduled"]), ["a", "b"])
        self.assertEqual(res["breaks"], [])

    def test_overlapping_commitments_collapse(self):
        # True overlap (not just back-to-back): 14:00-15:00 and 14:30-16:00 merge
        # to a single 14:00-16:00 busy span, so free time starts at 16:00.
        res = ps.pack(make_input(
            [chunk("a", 30)],
            busy=[busy("14:00", "15:00"), busy("14:30", "16:00")],
        ))
        self.assertTrue(res["scheduled"][0]["block"]["start"].endswith("16:00:00+05:30"))

    def test_unfittable_must_reason_is_no_slot(self):
        # A 90-min must with only 40-min gaps overflows specifically as NO_SLOT
        # (the cap is high, so it is not OVER_CAP, and free time exists).
        res = ps.pack(make_input(
            [chunk("big_must", 90, priority="must")],
            busy=[busy("14:40", "15:40"), busy("16:20", "17:20"), busy("18:00", "21:00")],
            config={"focus_cap_min": 500, "day_slack_pct": 0},
        ))
        reasons = {o["id"]: o["reason"] for o in res["overflow"]}
        self.assertEqual(reasons.get("big_must"), ps.NO_SLOT)

    def test_off_day_commitment_ignored(self):
        # A commitment on a different calendar day must not subtract from today's
        # window — full-datetime comparison places it entirely outside.
        off_day = {"title": "Tomorrow", "start": "2026-06-03T14:00:00+05:30",
                   "end": "2026-06-03T16:00:00+05:30"}
        res = ps.pack(make_input([chunk("a", 30)], busy=[off_day]))
        self.assertEqual(ids(res["scheduled"]), ["a"])
        self.assertTrue(res["scheduled"][0]["block"]["start"].endswith("14:00:00+05:30"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
