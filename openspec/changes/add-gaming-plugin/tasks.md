## 1. Plugin scaffold

- [x] 1.1 Add `plugins/gaming/plugin.json` at version `0.1.0` with six skills (`setup`, `onboard`, `sync`, `backup`, `configure`, `cheats`), Codex UI fields and `hosts: ["claude", "codex"]`; add the marketplace entry; run `npm run plugins:sync`.
- [x] 1.2 Add `README.md` (install, profile location and removal, printed permissions, skill table) and `CHANGELOG.md`.
- [x] 1.3 Add `plugins/gaming/tests/portability.test.mjs` (frontmatter shape, host-only patterns, capitalised emphasis words, 8,000-byte cap) and a `test:gaming` script; wire both into `npm test` and `npm run validate`.

## 2. Profile

- [x] 2.1 Write `schemas/profile.schema.json` and `profile.example.json` with generic placeholders covering every field in the gaming-profile spec; add the example to the schema test.
- [x] 2.2 Write failing tests, then `scripts/gaming_profile.py`. Cover: XDG resolution including relative values, `path`, `show`, `set` and `--dry-run`, `note` with the 50-note cap, `validate`, `init --from`, the history copy, atomic replace, credential-shaped key rejection, and the missing-profile message.
- [x] 2.3 Write `references/profile.md`: what belongs where (D3), how to read and update the profile, the note rules, and policy meanings.

## 3. Shared references

- [x] 3.1 `references/library-layout.md` (L1-L8, staging, per-game tools folder, `Tools/profile.json`).
- [x] 3.2 `references/verification.md` (scripted checks, evidence classes, fresh-proof rule, window-only visual checks) and `references/reviewer.md` (role brief listing every judgment the old verifiers made).
- [x] 3.3 `references/device-install.md` (D1-D13, generic) and `references/frontend-baseline.md` (stopped confirmation, rebase, drift, rebuild).
- [x] 3.4 `references/tools/retroarch.md` (X1-X12, X23, B3 scope, D4) and `references/tools/es-de.md` (D7-D9, L8, S8, X13-X15), each with source links and verified versions.

## 4. Scripts

- [x] 4.1 Port `sync_tree.py` as readable stdlib code with tests for T1-T9.
- [x] 4.2 Port `backup.py` as `snapshot.py`. Device, paths, scope and timezone come from the profile. A `local` connection runs without SSH. Tests cover B2 and B4-B9 with a local fake device.
- [x] 4.3 Add `verify_rom.py` (hash against DAT, archive integrity, size) with tests.
- [x] 4.4 Add `checks.py`: mounted volume, collisions, image header sanity, manifest consistency. Add tests.
- [x] 4.5 Add `esde_baseline.py` (`check` and `capture`) with tests.

## 5. Skills

- [x] 5.1 `setup` (import existing sources, one-batch questions, connection tests, printed permissions, migration mode with report).
- [x] 5.2 `onboard` (seven stages, ledger, scripted checks, reviewer at publish and install; O1-O24, D1, D13).
- [x] 5.3 `sync` (S1-S13, G1-G12, profile copy to the library).
- [x] 5.4 `backup` (`config` and `full` scopes, B1-B14, drift check, profile copy).
- [x] 5.5 `configure` (narrowest scope, snapshot first, docs check, baseline updates, rebuild).
- [x] 5.6 `cheats` (revision identity, research, engine limits, install names, save edits X20, per-game tools X21-X22).

## 6. Validation

- [x] 6.1 Run `npm run plugins:sync`, `npm run validate` and the host validators. Fix every failure without suppressing it.
- [x] 6.2 Install the plugin locally in Claude Code and Codex. Confirm all six skills are listed in both, and confirm `gaming_profile.py path` resolves the same file from each host.

## 7. Migration (owner's machine, outside the repository)

- [x] 7.1 Finish the value inventory (sync profile, project notes, memories, the three skills, live and snapshotted frontend settings, 2026-10-09 lessons).
- [x] 7.2 Run `setup` in migration mode, produce the migration report, and get the owner's approval.
- [x] 7.3 Write the profile with `gaming_profile.py init`, then read every mapped value back.
- [x] 7.4 Capture the Mac frontend snapshot. Record both frontend baselines and run the drift check on both devices.
- [ ] 7.5 Owner adds the printed Claude and Codex permission entries.

## 8. Parity and release

- [x] 8.1 Run the fresh-context parity review: original skill files against the new plugin and the migration report, row by row against `parity.md`. Fix every gap and re-review until clean.
- [ ] 8.2 Show the owner the full diff. Commit only with explicit approval, then open a PR.
- [ ] 8.3 After merge and install, move the old Codex `onboard-game`, `sync-games` and project `retrobackup` folders to a dated archive outside the skill discovery paths. Confirm Codex no longer lists them.
