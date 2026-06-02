## 1. Interview bank convention (references/interview.md)

- [x] 1.1 Add a short "Presentation" note at the top of `references/interview.md`: discrete decisions use AskUserQuestion with suggested options; open prompts stay free text; obey one-thread-at-a-time; phrase choices so they read as prose when the tool is absent (D1, D4, D5).
- [x] 1.2 Tag each question in the Hard gate, Intake, and Decompose banks as **[choice]** or **[open]** per design D3 (prior-progress, shape, stage/tree confirm, context = choice; done-criteria, first action, fuzzy/blocked, estimates = open).
- [x] 1.3 For each [choice] question, list its suggested option labels inline in the bank (e.g. prior-progress → "Fresh start" / "Already begun").

## 2. intake skill (skills/intake/SKILL.md)

- [x] 2.1 In the hard-gate / interview procedure step, instruct: present the prior-progress and single-vs-multi-step confirmations as AskUserQuestion choices (reference interview.md tags); keep done-criteria and first-action as prose.
- [x] 2.2 In the decompose-stage step, instruct: present the proposed stage tree as an AskUserQuestion confirm (build as proposed / adjust granularity / fewer stages), not a prose yes/no.

## 3. decompose skill (skills/decompose/SKILL.md)

- [x] 3.1 Instruct: present the derive-and-confirm context step as a work/personal AskUserQuestion choice.
- [x] 3.2 Instruct: present the hard-gate confirmations and the augment-vs-leave (already-split) decision as choices; keep open prompts as prose.
- [x] 3.3 Instruct: present the final tree confirm as a structured choice.

## 4. Validate

- [x] 4.1 Confirmed no code/schema/config changed: `git status` shows only interview.md + the two SKILL.md. Packer (26) + schema (16) tests still pass, unaffected.
- [x] 4.2 `claude plugin validate ./plugins/butler --strict` and `claude plugin validate . --strict` — both pass.
- [x] 4.3 `openspec validate butler-structured-interview-questions --strict` — valid.

## 5. Release (0.4.0)

- [ ] 5.1 Bump `version` to `0.4.0` in `plugins/butler/.claude-plugin/plugin.json` AND the marketplace entry (keep equal).
- [ ] 5.2 Update `plugins/butler/CHANGELOG.md` and root `CHANGELOG.md` with the 0.4.0 entry.
- [ ] 5.3 `claude plugin tag ./plugins/butler` → `butler--v0.4.0` (validates version agreement).
- [ ] 5.4 `git push origin main && git push origin refs/tags/butler--v0.4.0`.
