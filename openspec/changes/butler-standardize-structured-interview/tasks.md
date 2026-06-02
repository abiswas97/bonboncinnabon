## 1. Shared convention (references/interview.md)

- [x] 1.1 Strengthen the "Presentation" section to state it is the SINGLE SOURCE of the choice/open convention and applies to ALL interview-driven skills (intake, decompose, plan, reschedule) (D1).
- [x] 1.2 Define the canonical pointer sentence (D2) verbatim in Presentation so skills can quote it.
- [x] 1.3 Tag the **Target day** bank `[choice]` (today / tomorrow) with option labels.
- [x] 1.4 Tag the **Plan / reconcile** bank: keep-or-park `[choice]` (keep / park); commitment must/should/want `[choice, multiSelect]`; "what got in the way?" `[open]`; deep-vs-shallow `[choice, multiSelect]`.
- [x] 1.5 Tag the **Reschedule** bank: "what's done / left" `[open]`; "anything new today?" `[choice]` (nothing new / add something → then open); "drop a passed block?" `[choice]`.
- [x] 1.6 Tag the **Fixed duties** bank: calendar read-back `[choice]` (still on / adjust); lunch/commute/family confirms `[choice]` with an open escape for specifics.

## 2. Standardize intake + decompose to the pointer (DRY)

- [x] 2.1 `skills/intake/SKILL.md`: replace the 0.4.0 inlined AskUserQuestion mechanics in the interview/decompose steps with the canonical pointer (keep the hard-gate "do not proceed" salience).
- [x] 2.2 `skills/decompose/SKILL.md`: replace the top-of-procedure mechanics note + inlined per-step choice instructions with the canonical pointer (keep gate salience and the re-parent/re-read steps).

## 3. plan skill (skills/plan/SKILL.md)

- [x] 3.1 Add the canonical pointer to the plan interview/reconcile steps.
- [x] 3.2 Instruct structured forks: target-day (today/tomorrow), keep-or-park per reconciled chunk, must/should/want commitment (multiSelect), fixed-duties read-back — per the bank tags; keep "what got in the way?" prose and the capped no-blame discipline.

## 4. reschedule skill (skills/reschedule/SKILL.md)

- [x] 4.1 Add the canonical pointer to the reschedule interview step.
- [x] 4.2 Instruct structured forks: "anything new today?" and "drop a passed block?" as choices; keep "what's done/left" prose.

## 5. Validate

- [x] 5.1 Confirm only `interview.md` + the four SKILL.md changed (plus version/changelog later); no code/schema/config. Packer + schema tests unaffected.
- [x] 5.2 `claude plugin validate ./plugins/butler --strict` and `claude plugin validate . --strict`.
- [x] 5.3 `openspec validate butler-standardize-structured-interview --strict`.
- [x] 5.4 Grep check: the canonical pointer phrase appears in all four SKILL.md interview steps; no skill restates the AskUserQuestion mechanics (single-source requirement).

## 6. Release (0.5.0)

- [x] 6.1 Bumped `version` to `0.5.0` in `plugins/butler/.claude-plugin/plugin.json` AND the marketplace entry (equal).
- [x] 6.2 Updated `plugins/butler/CHANGELOG.md` ([0.5.0] - 2026-06-02) and root `CHANGELOG.md`.
- [x] 6.3 `claude plugin tag ./plugins/butler` created `butler--v0.5.0` (version agreement validated).
- [x] 6.4 Pushed `origin main` and `refs/tags/butler--v0.5.0`.
