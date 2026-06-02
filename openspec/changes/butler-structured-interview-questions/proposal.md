## Why

butler's `intake` and `decompose` interviews are authored in
`references/interview.md` as free-text question banks, and the skills render them
as prose the user answers by typing. The harness provides a native structured-choice
tool (AskUserQuestion) — the one `superpowers:brainstorming` uses — that renders
selectable option cards with an automatic "Other" escape and multi-select. butler
never invokes it, so discrete decisions (fresh-vs-started, single-vs-multi-step,
which pipeline stages apply, confirm-the-tree, work-vs-personal context) cost the
user a paragraph of typing instead of a tap, and the choices are less legible than
they could be. Adopting the tool for the *discrete* forks — while keeping free text
for genuinely open prompts — makes the interview faster and clearer without losing
its conversational character.

## What Changes

- **Introduce a structured/open convention** in `references/interview.md`: each
  interview question is tagged as a discrete choice (present via **AskUserQuestion**,
  with suggested options) or open-ended (free text). The existing question banks are
  annotated accordingly.
- **`intake` and `decompose` use AskUserQuestion for discrete decisions**: the
  hard-gate confirmations (fresh-vs-already-begun, single-action-vs-multi-step),
  stage selection / tree-shape confirmation, and (decompose) the work-vs-personal
  context confirmation. Open-ended prompts (done-criteria, "first physical action",
  what's fuzzy/blocked, estimates) stay free text.
- **Preserve the conversational discipline**: structured prompts still obey
  interview.md's "one main thread at a time, never a wall of questions" rule — the
  tool's 4-question batch is a ceiling, not a target.
- **Graceful degradation**: questions remain phrased so they read as answerable
  prose when AskUserQuestion is unavailable (non-Claude-Code harness), so the skill
  never hard-depends on the tool.
- **Scope: `intake` + `decompose` only.** `plan`/`reschedule` interview steps
  (target-day, must/should/want, keep-or-park) are out of scope this release.
- **0.4.0 release**: version bump in `plugin.json` + marketplace entry, CHANGELOGs,
  `claude plugin tag`, push.

No change to the task model, schemas, packer, config, or scheduling behavior — this
is purely how the interview is *presented*.

## Capabilities

### New Capabilities
- `structured-interview`: discrete interview decisions in intake/decompose are
  presented as structured choice prompts (AskUserQuestion) with a graceful prose
  fallback, while open-ended prompts stay free text; the conversational
  one-thread-at-a-time discipline is preserved.

### Modified Capabilities
<!-- interview-gate is unchanged: the gate stays blocking and mandatory. This change
     governs HOW questions are presented, not WHETHER the gate stops decomposition.
     No existing requirement's behavior changes, so no delta to interview-gate. -->

## Impact

- **References**: `references/interview.md` gains a short "presentation" convention
  and per-question structured/open annotations.
- **Skills**: `skills/intake/SKILL.md` and `skills/decompose/SKILL.md` procedure
  steps point at the structured steps and name AskUserQuestion for the discrete
  forks. No change to `plan`/`reschedule`.
- **No code**: schemas, `pack_schedule.py`, `config.yaml` untouched; all 26+16 tests
  stay green by construction.
- **Release**: `plugins/butler/.claude-plugin/plugin.json` + marketplace entry +
  both CHANGELOGs + `butler--v0.4.0` tag.
- **Compatibility**: additive and harness-aware — on a harness without
  AskUserQuestion the prose fallback keeps intake/decompose fully usable.
