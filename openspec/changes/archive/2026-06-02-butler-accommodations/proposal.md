## Why

butler schedules well but is psychologically naive: it has no codified stance on
*how* it speaks to a user under executive-function load, no instinct to catch
overcommitment before burnout, and no reduced mode for a depleted day. A planner
for people with ADHD / BPD / depression / executive dysfunction that gets the tone
or the pacing wrong actively harms — a guilt-based miss, a packed-streak
"congrats," an imposed rest block. The behaviors that help are well-evidenced
(behavioral activation, implementation intentions, the shame-vs-guilt distinction,
the Maslach overload-without-recovery model, SDT autonomy). This change codifies
that evidence as a single, reusable accommodations layer plus a standing
burnout instinct.

Evidence base: `docs/research/butler-accommodations-evidence.md` (five reviews,
every behavior tied to a named source + confidence grade + a do-NOT-codify list).

## What Changes

- **New accommodations reference.** A single `references/accommodations.md` holding one evidence-tagged `<accommodations>` XML block: six principles (action-first, if-then-cue, mastery+pleasure, flexibility-with-spine, non-punitive, tone), each with the behavior, the evidence anchor, and a confidence grade. All four skills reference it; none restate it (single source).
- **Skills apply the principles.** intake / decompose / plan / reschedule gain a one-line pointer to the accommodations layer and apply it where they already speak to the user (miss-handling becomes no-blame + a small next step; the day blends mastery + pleasure; commitments carry an if-then cue; partial completion is valued; tone never ties worth to output).
- **Burnout detection (auto, inside plan).** plan reads a rolling 5–7 day TickTick-derived window during reconciliation and, only when *all* signals hold (sustained packed streak + no recovery day + high completion, on the user's *own* baseline), surfaces one no-blame prompt asking whether to keep the next day lighter. Anti-nag cool-down. **Never adds a task, never auto-inserts rest, never reschedules unasked.**
- **Low-energy reduced mode.** User-invokable ("I'm low energy") and auto-*offered* (never forced) when the burnout signal fires: plan cuts the day to ~one mastery + one pleasure item and leads with the smallest concrete step.
- The do-NOT-codify list becomes explicit anti-requirements so future changes don't reintroduce guilt streaks, productivity-as-worth, nagging, auto-rest, or absolute-hour thresholds.

No code changes (the packer is untouched). Reference + skill prose + config defaults only.

## Capabilities

### New Capabilities
- `accommodations`: the evidence-tagged principle layer skills apply when speaking to the user, plus low-energy reduced mode and the anti-requirements.
- `burnout-detection`: the rolling-window overload signal, its fire conditions, and the single autonomy-preserving prompt.

### Modified Capabilities
- `context-aware-scheduling`: plan applies the accommodations layer, runs the burnout check at reconciliation, and offers/accepts low-energy mode.

## Impact

- New: `plugins/butler/references/accommodations.md`; `docs/research/butler-accommodations-evidence.md` (already written).
- Modified: `skills/{intake,decompose,plan,reschedule}/SKILL.md` (one-line pointer + applied behavior in miss-handling / selection / tone steps); `references/heuristics.md` (burnout signal + low-energy under a Pacing section); `config.yaml` + `schemas/config.schema.json` (burnout-window defaults; config_version bump).
- No packer code change; existing tests unaffected.
- Release: 0.9.0.
