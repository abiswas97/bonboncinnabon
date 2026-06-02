## Context

0.9.0 adds a psychological layer on top of the existing scheduler: how butler
speaks (accommodations) and a standing instinct to catch overcommitment
(burnout-detection) plus a reduced mode for depleted days. No packer change.
Evidence and confidence grades: `docs/research/butler-accommodations-evidence.md`.

Two prior decisions constrain the design:
- **State lives in TickTick + config**, no separate store (the user: "just the config").
- **Breaks/rest are constraints, never tasks** — so burnout handling must never materialize a task.

## Decisions

### Accommodations as a single-source XML reference
`references/accommodations.md` holds one `<accommodations>` block. Each
`<principle>` carries `name`, the concrete `behavior`, an `evidence` anchor
(named source), and a `confidence` attribute (strong | moderate | weak). Skills
get a one-line pointer ("apply `references/accommodations.md`") at the steps where
they already speak to the user; they never restate the principles. This mirrors
the `interview.md` single-source pattern and honors the data-driven tenet: change
the doctrine in one file, every skill follows.

Why XML (not prose): the user asked for it, and the tagged structure lets each
principle pin its evidence + confidence so a future edit can't quietly downgrade a
strong behavior or smuggle in an unsupported one. The anti-requirements ride in
the same block as `<do-not>` entries.

### Burnout signal is computed, not stored
plan reads a rolling 5–7 day window from TickTick at reconciliation:
- **completed load per day** — `list_completed_tasks_by_date` over the window.
- **planned/scheduled load per day** — the day's committed focus blocks (count + `focusSummaries.estimatedPomo`).
- **baseline** — the user's own ~30-day median daily load (and top quartile for "packed"). Never absolute hours.

Signal components: packed-day streak (days above the user's top-quartile load) and
the no-recovery-day flag (no day below ~50% of median — **mandatory**). Completion
rate is **not** a gate: detection fires on sustained packing regardless of
completion, so the packed-but-falling-behind user (higher-risk) is caught too.
Completion is read only to tune the prompt's *wording* (finishing-everything vs
falling-behind); it never suppresses the prompt and the wording stays non-punitive
either way.

### Anti-nag without a state store: rising-edge firing
The cool-down requirement ("at most once per window") is satisfied **without
persisting a last-prompted date** — which would mean an LLM rewriting the user's
hand-edited `config.yaml` (clobber risk) or creating a TickTick task (forbidden).
Instead the prompt fires on the **rising edge**: only when the current
consecutive packed-day streak *equals* `min_packed_streak` on this run (with at
most one day of grace, so a single skipped planning day doesn't lose the edge).
For any longer streak the rising edge has passed, so butler stays silent. This is
fully derivable from the window data, needs zero stored state, and fires at most
once per overload episode. If the user accepts lightening, the next day drops
below threshold and the signal clears; if they decline and keep packing, the edge
is behind them, so butler does not re-nag.

The cost: firing is tied to the crossing day. If the user doesn't run plan that
day (beyond the one-day grace), the prompt is **skipped, not deferred** — it fails
safe to silence rather than catching up with a stale nag. Accepted: missing an
episode is consistent with never-nag, and the alternative (persisting a
last-prompted scalar) means an LLM rewriting the user's hand-edited config.yaml
(clobber risk) or a forbidden TickTick task.

### Low-energy mode is behavioral, not configured
No new config. Reduced mode = select ~one mastery + one pleasure item and lead
with the smallest concrete step. Triggered by a user signal ("I'm low energy") at
any point, or offered (never auto-applied) as one option when the burnout prompt
fires. It reuses the existing selection step; it does not change the packer.

### Config additions (versioned)
A top-level `pacing` block carries the burnout tunables so the thresholds are
data-driven, not buried in prose:
```
pacing:
  window_days: 7        # rolling window for the burnout signal
  min_packed_streak: 4  # consecutive packed days before the rising edge can fire
  packed_quantile: 0.75 # "packed" = above this quantile of the user's own load
  recovery_fraction: 0.5  # a "light/recovery" day is below this * median load
  high_completion: 0.8  # framing only (not a gate): above this, the prompt's wording leans "finishing everything" vs "falling behind"
```
`config_version` bumps 1 → 2; `schemas/config.schema.json` `configVersion` → 2 and
documents `pacing`. The shared preflight (0.8.0) handles migration: a v1 config is
behind → offer additive migration (insert `pacing` defaults, bump to 2). No
existing field changes.

## Risks / trade-offs

- **Rising-edge can miss an episode** whose start predates the 7-day window. Accepted: the alternative (persisting state) is worse (config clobber / forbidden task). A 7-day window catches the common case; chronic multi-week overload will still show a fresh rising edge after any recovery day.
- **Baseline needs history.** A brand-new OR sparse-history user has no reliable ~30-day baseline → the signal does not fire (fail-safe: silence, never a false alarm). The check explicitly bails to silent when history is thin.
- **Baseline is recomputed every plan run.** plan pulls the window + ~30-day history from TickTick and does the median/quantile math LLM-side on each run. This is a real but bounded data pull on a soft signal; acceptable because the output is only a *question*.
- **LLM-run detection is heuristic, not exact.** Acceptable: the output is a *question*, never an automatic action, so a soft signal can't cause harm.
- **mastery+pleasure must not invent tasks.** The blend is surfaced as an observation + offer; plan still only schedules personal items the user names (0.6.1 never-invent). The SKILL prose must not drift into auto-adding a pleasure task — that is on the do-NOT list.

## Migration

Additive only: `pacing` defaults inserted on the existing preflight migration path;
`config_version` 1 → 2. No behavior change for users who don't hit the burnout
signal. Packer and its tests are untouched.
