# Verification and evidence

Scripts establish mechanical facts, and one fresh reviewer checks the judgment calls before anything irreversible. Paths are relative to the plugin root.

## Evidence rules

- **Fresh proof only.** A prior report, a folder name, a command that exited 0 or an existing manifest entry is not proof. Re-read or re-hash.
- **A failed check stops dependent work** until it is fixed and checked again. Never advance on an unverified game identity.
- **Record what you observed** in the run ledger: facts, failed checks and unresolved gaps.
- **Missing optional items** (videos, for example) pass only as recorded gaps. Missing requested items mean the result is incomplete.
- **Keep different kinds of proof separate.** Never let one stand in for another:
  - catalogue identity (a DAT match), transfer integrity (hashes after copying), and achievement-hash compatibility
  - local copy verified, cloud presence verified, cloud bytes verified
  - files and configuration checked, the frontend visibly showing them, a game observed launching (a launch command is not runtime proof; report runtime as pending until the owner or a window capture shows it)
- **Visual checks** capture only the specific app window, never the full screen. Other windows can hold private content.
- **Cloud evidence has limits.** Cloud connectors may list files without checksums; report that as a checksum gap. Desktop sync clients can show a file as different while it is still downloading. Re-read it before calling a mismatch.

## Scripted checks

| Fact | Command |
|---|---|
| Library drive mounted, root present | `scripts/checks.py mounted --library ID` |
| ROM matches a catalogue entry; archive members intact | `scripts/verify_rom.py FILE --dat DAT` (DATs live in `<root>/Tools/DATs/`; for hacks, check the base ROM; without `--dat`, hash and archive test only) |
| New, same, conflicting or case-colliding paths | `scripts/checks.py collisions STAGING ROOT` |
| Images decode with real dimensions | `scripts/checks.py images FILE...` |
| Manifest entries exist with recorded sizes and hashes | `scripts/checks.py manifest ROOT [--hash]` |
| Manifest kept every earlier key and entry | `scripts/checks.py manifest-preserved OLD NEW [--moved OLD=NEW] [--updated PATH]` |
| Files on a device match the library | `scripts/checks.py device-hashes --device ID --map MAP.json` |
| Non-destructive copy with hash proof | `scripts/sync_tree.py SOURCE DEST EVIDENCE [--apply] [--preserve-conflicts] [--recovery-root PATH] [--exclude NAME]` |
| Read-only device snapshot | `scripts/snapshot.py --device ID --scope config\|full` |
| Frontend settings match the baseline | `scripts/esde_baseline.py check --settings FILE --device ID` |

A non-zero exit is a failed check. Read its message, fix the cause, and run it again. For PDFs, also record the page count and render one or two representative pages to confirm that the content matches.

## The reviewer gate

Run the reviewer on the staged package before publishing it into the library, and on the install plan before writing to a device. The steps after each gate are proven by scripts (`sync_tree.py` evidence, `checks.py manifest-preserved` and `manifest --hash`, `checks.py device-hashes`, `esde_baseline.py check`), plus one manual step: the gamelist play-history comparison in `references/device-install.md`. `sync` also runs the reviewer before reporting any backup target as verified.

1. Ask the host for a subagent with **no conversation history**. Give it only:
   - the owner's request
   - the staging and destination paths
   - the run ledger
   - `references/reviewer.md`
2. The reviewer is read-only. The primary agent makes every change.
3. Act on every `fail` and `gap` it reports, then re-run the scripts the fix affects. Ask for a fresh review when a judgment item changed.
4. If the host cannot start an isolated subagent, stage and report only. Say that review is pending and publish nothing.

## Run ledger

Long jobs keep `<root>/Staging/<run id>/run.json` so work survives a new turn or a compacted conversation. Use a run id of the form `<YYYY-MM-DD>-<short-slug>`.

Keep staged files under `<run>/files/` in their final layout, and keep script evidence under `<run>/evidence/`. Publish each staged top-level folder to its counterpart (`<run>/files/ROMs` to `<root>/ROMs`), so source, destination and evidence never overlap. `Staging/` is work in progress, and `sync` never copies it to backup targets.

```json
{
  "run_id": "2026-01-01-gba-batch",
  "skill": "onboard",
  "request": "What the owner asked for, in their words",
  "items": [
    {
      "id": "ROMs/gba/Example (USA).gba",
      "stage": "documents",
      "status": "in-progress",
      "evidence": ["Staging/.../verify_rom.json"],
      "gaps": ["No original manual scan found"]
    }
  ],
  "next_step": "Prepare documents for item 6"
}
```

Update the ledger after every stage. On resume, read it first and continue from `next_step` without redoing verified work. Keep credentials out of it.

## Large transfers

Library backups run one `sync_tree.py` per target over the whole library with `--exclude Staging`, so root-level files are included and conflict copies land in `<target>/Recovery/Previous Cloud Files/`. Publishing from staging runs per top-level folder instead, because the staging area lives inside the library.
