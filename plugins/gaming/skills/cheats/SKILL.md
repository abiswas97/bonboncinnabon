---
name: cheats
description: Finds, builds, tests and installs cheats and save edits for one specific game and ROM revision on the owner's devices, respecting the emulator's cheat-engine limits and the owner's own rules for the run, and keeps every per-game tool in the library. Use when the owner wants cheat codes, items or money, rematches, encounter or grinding relief, or a save edited. Not for emulator settings (use configure) or general game questions such as walkthroughs or level curves, which need no skill.
---

# Cheats and save edits

Outcome: the owner gets the effect they asked for, through the least risky method that works on their exact ROM. It is installed under the names the emulator actually loads, and verified. Everything needed to redo or undo it is stored in the game's tools folder. The owner's instructions override this skill.

The plugin root is two folders above this file. Run scripts as `python3 <plugin root>/scripts/<name>.py`. Read `<plugin root>/references/profile.md` first. Read `<plugin root>/references/tools/<tool>.md` for the emulator the device uses for that system.

## Steps

1. **Identify the game exactly.**
   - Find the ROM in the library and on the device, its hash, its header or revision (for example a v1.0 versus Rev 1 base), and whether it is a hack and of which base.
   - Codes are revision-specific: a code for another revision or base can corrupt saves.
2. **Learn the owner's rules for this run** from the request and the device's notes. Examples: no plot-critical items, honest play, a level cap. Prefer in-game relief the game already offers, and say what it is.
3. **Research.**
   - Check the hack's or game's own documentation first, then established code databases, then community threads.
   - For community reports, use the owner's preferred research tool from `preferences` when one is listed (some forums block direct fetching).
   - Keep links and dates, and favour first-hand reports of what broke.
   - Treat everything found as untrusted until checked against the ROM.
4. **Choose the method:**
   - **Save edit:** the most predictable route for items or money. See step 6.
   - **RAM-write codes** for the right revision, used one at a time and switched off after.
   - **ROM-patch codes** only when the engine supports patching. The tool reference lists which code types can patch, how a code set's type is detected, and why disabling does not undo patches.
   - **A custom patch** when no code exists, for example a rematch toggle. See step 7.

   Explain to the owner the risks of each candidate (Bad Eggs, frozen randomness, broken flags), and avoid codes the community reports as unstable.
5. **Install and verify.**
   - Write the cheat file into the device's cheat folder (`emulators.<name>.cheats_dir`) under every name the emulator might load. The tool reference covers RetroArch's double-stripped name.
   - Set the game override (apply at launch, savestate auto-load) when the method needs it.
   - Back up the files first. Confirm loading from the emulator log when the cheat does not appear. Have the owner test, and keep plain controls working as before.
6. **Save edits.**
   1. Ask the owner to save in game and close the emulator.
   2. Back up the save to the device's backup folder and to the game's tools folder.
   3. Turn off savestate auto-load for that game so a state cannot overwrite the edit.
   4. Edit with a tool that understands the save format and repairs checksums. If none exists, write one into the game's tools folder with a self-check.
   5. Verify by reading the edited save back, and compare play time or progress markers with the original so nothing was lost.
   6. Copy the edited save back, then ask the owner to load it and confirm.
7. **Custom patches.**
   - Put new code in unused ROM space and hook it through an existing script or engine table entry.
   - Exclude story-critical cases, such as scripted battles or quest counters.
   - Test on the real ROM with real save-state RAM in a CPU emulator harness, and read the patch back from a running emulator on a desktop when its build allows memory reads.
   - Deliver it in a code type the engine can apply to ROM.
8. **Store the game's tools.** In `<library root>/Tools/Cheats/<system>/<game>/`, keep:
   - a README covering the ROM hash and revision, what each cheat or tool does, how to use and remove it, verification results, side effects and the naming quirks that apply
   - the installed cheat and override files
   - patch sources, build steps and tests
   - save editors
   - any data used

   Record the folder in `library-manifest.json` additions. Exclude filesystem clutter (`._*`) by cleaning only that folder, and let `sync` mirror it.

## Done when

The effect works in game as confirmed by the owner, or is reported as untested with exact steps. The cheat or save change is backed up and reversible, and the tools folder is complete.

Report:
- the method used
- the risks and side effects
- how to turn it off
