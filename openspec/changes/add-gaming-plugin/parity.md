# Parity map

Every rule and effect of the replaced skills, and every lesson recorded since, with its new home. Personal values are not copied here. Rows marked "profile" are carried by the owner's profile, outside the repository.

Sources:
- **O**: `onboard-game/SKILL.md`
- **D**: its `device-installation.md`
- **L**: its `library-layout.md`
- **S**: `sync-and-backups.md` and `backup-contract.md` (near-identical)
- **G**: `sync-games/SKILL.md`
- **T**: `sync_tree.py`
- **B**: `retrobackup` (`SKILL.md` and `backup.py`)
- **X**: lessons from 2026-10-09

Destinations:
- **sk:** a skill body (for example sk:onboard)
- **ref:** a plugin reference (for example ref:library-layout)
- **tool:** a tool reference such as `references/tools/retroarch.md` (for example tool:retroarch)
- **scr:** a script (for example scr:sync_tree)
- **prof:** a profile field

Approved change: rows O3, O6 and G10 move from a model verifier at every stage to scripted checks plus one fresh-context reviewer (design D4, owner approval 2026-10-09). Every judgment those verifiers made is listed in `ref:reviewer`.

## onboard-game

| ID | Rule or effect | New home |
|---|---|---|
| O1 | Prepare the package on the selected library; default to the profile's canonical library; verify the volume is mounted before writing | sk:onboard, prof:libraries, scr:checks `mounted` |
| O2 | Follow the canonical layout strictly; no franchise-first layout; a chat workspace is never the final library | ref:library-layout |
| O3 | Each stage needs direct evidence and independent verification before the next relies on it | scr checks per stage + ref:reviewer at publish and install (approved change) |
| O4 | Give the verifier the request, raw sources and acceptance criteria, never a conclusion to agree with | ref:reviewer |
| O5 | Verifiers are read-only; the primary agent owns mutations | ref:reviewer |
| O6 | Reuse the verifier with fresh evidence; batch independent checks without skipping a gate | ref:reviewer (one batched review per gate) |
| O7 | Record observed facts, failed checks and unresolved gaps | Staging `run.json` ledger, ref:verification |
| O8 | A prior report, folder name, successful command or manifest entry is not fresh proof | ref:verification |
| O9 | Without subagents, only staging and read-only discovery continue; report the limitation | sk:onboard, ref:verification |
| O10 | Never advance on an unverified identity; a failed gate stops dependent work until fixed and rechecked | sk:onboard stop rules, scr non-zero exits |
| O11 | Missing optional assets pass only as recorded gaps | sk:onboard done-check |
| O12 | Resolve title, system, edition or revision, region, language, original versus remake or hack, destination and components; ask only about material ambiguity | sk:onboard stage 1 |
| O13 | Storage only by default; install needs explicit or standing opt-in from the profile; never inferred from a game name | sk:onboard, prof:devices[].install_opt_in |
| O14 | Inspect requested collection and backup coverage as part of scope | sk:onboard stage 1 |
| O15 | Prefer user files, then the library, then extra backup libraries; absence in one root is not absence on the drive | sk:onboard, prof:libraries[].extra_sources |
| O16 | Download only when needed, from an appropriate source within scope; authentication stays temporary and out of artifacts | sk:onboard |
| O17 | Check archive integrity (always), size and identity against reference catalogues where they exist; SHA-256 the prepared file; keep catalogue identity, transfer integrity and achievement compatibility distinct | scr:verify_rom, sk:onboard (hacks: base ROM against DAT plus patch identity), ref:verification |
| O18 | Normalisation or patching preserves the original and needs edition-specific evidence | sk:onboard, ref:library-layout |
| O19 | Artwork: cover, screenshot, title screen, marquee or logo and metadata; videos optional; keep existing preferred art; match the exact ROM stem and edition; check decoding and hashes; store in canonical Media | sk:onboard stage 3, scr:checks `images`, ref:reviewer (category coverage) |
| O20 | Documents: original colour scans matching language, region and edition; In Box, Guides and Documentation classification; hack docs never presented as retail; integrity, page count, rendering, provenance; no modern abbreviated manuals; state missing material; reader import and conversion are separate opt-ins | sk:onboard stage 4, ref:library-layout, ref:reviewer |
| O21 | Publish: stage, manifest with path, source and hash, collision check, preserve unrelated files, saves, history and versions, recovery before replacing, copy, re-read and hash, update the manifest without losing schema or history, mark verified and gaps separately, never fabricate provenance, never delete original art or backups to consolidate | sk:onboard stage 5 (per-folder publish from `Staging/<run>/files`), scr:sync_tree, scr:checks `manifest --hash` and `manifest-preserved`, ref:library-layout |
| O22 | Install only on request: verify from the actual target, preserve choices, recovery copies first, verify files, metadata and membership; a launch command is not runtime proof; require an observed launch or report it pending | sk:onboard stage 6, ref:device-install (reviewer on the plan; scr:checks `device-hashes`, play-history comparison and baseline check after writing) |
| O23 | With collection upkeep or extra destinations enabled, run the sync workflow; prepared device edits are never reported as current; no full-backup claim from staging or upload queues | sk:onboard stage 7 → sk:sync |
| O24 | Final report: location, verified components, gaps, install and runtime status; missing requested parts mean incomplete; keep evidence without credentials; repeat runs reuse verified files and fill gaps, never duplicate or silently replace | sk:onboard done-check, ledger |

## device-installation

| ID | Rule or effect | New home |
|---|---|---|
| D1 | Only on explicit request; identify the target; storage preparation implies neither integration nor reader import | sk:onboard stage 6 |
| D2 | Consult the device's recorded setup before changes | prof:devices[].notes, frontend baseline |
| D3 | Prefer SSH and SCP through the alias; do not default to ADB | ref:device-install, prof:devices[].connect |
| D4 | Inspect the active system directory and override hierarchy before placing BIOS or changing core options | tool:retroarch |
| D5 | Check community setup guides and official core and frontend docs before config changes | sk:configure |
| D6 | Never copy unnecessary BIOS | ref:device-install |
| D7 | Frontend art matches the ROM stem; deploy Media categories to the target's media folders | tool:es-de |
| D8 | Manuals go into the frontend manuals category when requested; the canonical PDF stays in Documents | tool:es-de |
| D9 | Preserve gamelist entries, play history and collection presentation | tool:es-de, ref:frontend-baseline |
| D10 | The owner confirms the frontend is stopped before external gamelist, collection or settings writes; process checks are not proof | ref:frontend-baseline, prof:devices[].frontend.requires_stopped_confirmation |
| D11 | Keep collections grouped; preserve carousel, startup and theme; still-image lists; no autoplay or appearance changes during onboarding | prof frontend baseline, ref:frontend-baseline |
| D12 | Collection membership follows existing authorisation or a concrete agreed choice | sk:sync, prof:collections |
| D13 | Other devices: discover formats, paths, art mapping, BIOS needs and a safe metadata workflow; do not transplant assumptions; keep file checks, visible display and launch evidence separate | ref:device-install |

## library-layout

| ID | Rule or effect | New home |
|---|---|---|
| L1 | Root comes from the profile; a different medium changes the root, not the layout; lowercase frontend-compatible system IDs | ref:library-layout, prof:libraries |
| L2 | The full layout tree (ROMs, Media categories, Documents subfolders, BIOS, Archives, Frontends Current and Prepared, Recovery, Tools, manifest) | ref:library-layout (tree adds `Staging/` and `Tools/profile.json`) |
| L3 | Create only needed folders; the ROM stem names the media and document folders; multi-file games keep one canonical folder and list constituent files | ref:library-layout |
| L4 | Never rename ROMs casually (frontend references, saves, achievements) | ref:library-layout |
| L5 | Media holds the canonical art; frontend copies are projections; portable metadata goes in the manifest | ref:library-layout |
| L6 | Preserve the PC folder, BIOS conventions and the manifest schema including `files` and `additions`; add source, bytes, SHA-256, mapping, classification and evidence; no competing catalogue | ref:library-layout, scr:checks `manifest` |
| L7 | Migration copies with hash verification; backup libraries stay backups; compare newer deployed bytes against evidence; never assume an old backup matches a device; unavailable sources are gaps | ref:library-layout |
| L8 | Collection definitions live in the manifest with root-relative IDs; observed and desired memberships are separate; frontend `.cfg` files are device projections with absolute paths | ref:library-layout, tool:es-de |

## sync-and-backups / backup-contract

| ID | Rule or effect | New home |
|---|---|---|
| S1 | Sync never bypasses onboarding gates for new games | sk:sync |
| S2 | Read the profile and keep standing opt-ins; no credentials in it | sk:sync, ref:profile |
| S3 | Confirm the real mount; ground the cloud destination with connector metadata before writing | sk:sync (no connector: write nothing to that target, report pending) |
| S4 | Backup scope per target (owner: entire library plus device recovery) | prof:backup_targets[].scope |
| S5 | After each addition review sports, tactics and strategy, cozy and franchise collections with the agreed rules; never pad a collection; reuse an existing sports collection | sk:sync, prof:collections |
| S6 | Desired membership in the manifest; snapshots of actual frontend files kept separately | ref:library-layout, tool:es-de |
| S7 | Stopped-frontend confirmation; prepare while waiting; re-read and rebase after closure to keep newer play history | ref:frontend-baseline |
| S8 | Grouped collections, carousel, startup and still-image preferences; custom sort names are shared across collections | prof frontend baseline, tool:es-de |
| S9 | Full library backup scope list | sk:sync (one whole-library `sync_tree.py` per target with `--exclude Staging`, so root-level files such as the manifest are included), ref:library-layout |
| S10 | Device recovery scope: frontend tree, installed ROMs, emulator main config, core options, overrides and remaps, BIOS, saves and states at configured paths, resolved without printing configs; never described as a full OS image | sk:backup `full` scope, scr:snapshot (`data_keys` resolve save, state and system folders from the active config) |
| S11 | Inventory and checksum before and after live reads; reject changed captures; keep incomplete artifacts; verify archive members; timestamped versions before overwrites | scr:snapshot (builds in `Staging/snapshots`, moves into `Recovery/` only when verified), scr:sync_tree `--recovery-root` |
| S12 | Cloud sync is additive; conflicts keep a recovery copy and need an established owner | scr:sync_tree, prof:policies, sk:sync (the library is the established owner of its own manifest and profile copy; every other conflict waits for the owner) |
| S13 | Local hashes, cloud presence and cloud bytes are proven separately; a desktop mirror is staging; report checksum gaps; store per-target results and restore paths | sk:sync (manifest `backup_verification`, reviewer before any verified claim), ref:verification |

## sync-games

| ID | Rule or effect | New home |
|---|---|---|
| G1 | Maintain the existing library and enabled destinations; acquisition belongs to onboarding | sk:sync |
| G2 | Read profile, manifest and live device state; never invent targets | sk:sync |
| G3 | Owner's drive root, device alias and cloud scope | prof |
| G4 | Read-only discovery and a concrete change set before any write | sk:sync |
| G5 | Preserve user edits and overlapping memberships; keep the policy collections current; keep requested franchise introduction order | sk:sync, prof:collections |
| G6 | Verify target paths from active config before copying BIOS, saves, states or overrides | sk:sync, sk:backup |
| G7 | Scripts with bounded parallel transfers; no deletions; cloud mirrors are staging until server verification | scr:sync_tree |
| G8 | Preserve conflicts first; `--preserve-conflicts` only after establishing authority and never automatically for saves; no save merging, timestamp winners or mirrored deletions | scr:sync_tree, prof:policies, sk:sync |
| G9 | Recovery snapshots before and after device changes, including configured paths outside defaults | sk:sync and ref:device-install (`full` scope before and after each device change), sk:configure (`config` scope for settings-only changes), scr:snapshot `data_keys` |
| G10 | Independent verification of copies, membership, play history and archive members; stage only without it | scr checks + ref:reviewer (approved change) |
| G11 | Keep local, cloud-presence, cloud-byte and runtime evidence distinct; report counts, scope, pending targets and restore steps; no full-backup claim with gaps | sk:sync done-check |
| G12 | No recurring automation unless requested; onboarding consults the profile and syncs enabled targets | sk:sync, sk:onboard |
| G13 | For the handheld, prefer SSH and SCP; verify device copies, membership and play history | sk:sync (device targets go through ref:device-install "Writing" and "After writing": `checks.py device-hashes`, play-history comparison, baseline check) |

## sync_tree.py

| ID | Effect | New home |
|---|---|---|
| T1 | Excludes `.DS_Store` and `._*`, listing them as excluded | scr:sync_tree + test |
| T2 | Refuses directory symlinks, non-regular files and unfinished-operation markers | scr:sync_tree + tests |
| T3 | Refuses overlapping roots; evidence must sit outside both | scr:sync_tree + tests |
| T4 | SHA-256 and MD5 per file; source stability check; reused, copy or conflict | scr:sync_tree + test |
| T5 | Conflicts fail unless preserved; preserved copies go to a timestamped recovery path and are verified | scr:sync_tree + test (default `<destination>/Recovery/Previous Cloud Files`, as before, for whole-library syncs; `--recovery-root` for per-folder publishing and `Current/` refreshes) |
| T6 | Temp file, hash check, destination-unchanged check, atomic replace, final and source re-verification | scr:sync_tree + test |
| T7 | Progress evidence every 30 s; final re-inventory and re-hash of sources | scr:sync_tree |
| T8 | Status `plan` or `local-copy-verified`; cloud flags false | scr:sync_tree + test |
| T9 | Plan by default, `--apply` to write | scr:sync_tree + test |
| T10 | (new) Whole-tree runs can leave out top-level entries such as `Staging/`, and keep their evidence there | scr:sync_tree `--exclude` + test |

## retrobackup

| ID | Effect | New home |
|---|---|---|
| B1 | Read-only: never launches, closes, stops or tells the emulator to save | sk:backup, scr:snapshot |
| B2 | Requires the library drive mounted; never creates a substitute mount folder | scr:snapshot + test |
| B3 | Config scope: `.cfg .opt .rmp .slangp .glslp .cgp` from the app folder, standard config folders and configured override, remap, autoconfig and core-option paths; relative paths are an error | scr:snapshot `config` scope, tool:retroarch, prof device emulator paths |
| B4 | Canonical paths avoid duplicate storage aliases; missing paths recorded | scr:snapshot |
| B5 | Hash inventory before; main config hash must match what was read | scr:snapshot |
| B6 | New timestamped folder, never reused, private permissions | scr:snapshot + test (stamp to the second, matching existing `Recovery/` names; a same-second rerun fails rather than reuses) |
| B7 | Stream to `.incomplete`, fsync, re-inventory; changes leave a marked incomplete archive | scr:snapshot + test |
| B8 | Every archive member verified; no unexpected or duplicate members | scr:snapshot + test |
| B9 | `manifest.json` with status, scope, missing paths, records and archive hash, written exclusively; only `status: verified` means success | scr:snapshot + test, sk:backup done-check (fields renamed: `device` for `source`, scope `config` or `full`) |
| B10a | Bounded timeouts (180 s per command originally) | scr:snapshot (180 s for small commands, 1 h per hash batch, 6 h per archive) |
| B10 | Never echo commands or output that could contain config data; contents stay opaque; never copied into notes or memory | scr:snapshot, sk:backup, ref:profile |
| B11 | Connection failure hints (wake device, VPN, SSH server) | prof:devices[].connect.hints |
| B12 | Never overwrites old backups, restores or changes settings; restore is a separate request; never substitutes an older project copy when the device is unreachable | sk:backup |
| B13 | Report folder, verified file count and missing scope | sk:backup done-check |
| B14 | Timestamps in the owner's timezone with a zone suffix | prof:timezone, scr:snapshot |

## Lessons from 2026-10-09

| ID | Lesson | New home |
|---|---|---|
| X1 | RetroArch overrides stack (core, content folder, game); remaps do not, only one loads (game, then folder, then core) | tool:retroarch |
| X2 | `remap_save_on_exit` rewrites active remap files; keep it off | tool:retroarch, prof device baseline |
| X3 | Main-config saves are refused while an override is active | tool:retroarch |
| X4 | Hotkey enable is all-or-nothing per config; drop it per core via override | tool:retroarch |
| X5 | Gamepad combo codes for quit and menu toggle | tool:retroarch |
| X6 | Android keycodes for face, shoulder, Start and Select buttons | tool:retroarch |
| X7 | Android 1.21 strips the extension twice when naming game cheat files; keep both names | tool:retroarch, sk:cheats |
| X8 | Android builds lack network commands; desktop builds allow memory reads for testing | tool:retroarch, sk:cheats |
| X9 | `--appendconfig` values are written back to the main config on exit | tool:retroarch |
| X10 | mGBA cheat engine: which code types can patch ROM, autodetect from the first line, one hook per set, reset does not undo patches | tool:retroarch (mGBA section), sk:cheats |
| X11 | Savestate auto-load overrides an edited save; disable it per game before save edits | sk:cheats, tool:retroarch |
| X12 | RetroArch savestate container format for reading RAM | tool:retroarch |
| X13 | ES-DE on macOS: windowed emulators lose focus unless launched through `open`; `--resolution` gives a windowed frontend | tool:es-de, prof Mac baseline |
| X14 | Theme variants defined for one aspect ratio fall back to a no-art layout elsewhere | tool:es-de, prof baselines |
| X15 | macOS asks the owner to allow removable-volume access on first emulator launch | tool:es-de |
| X16 | Remapping apps lose their accessibility service under battery optimisation | prof device notes |
| X17 | Copies to exFAT create `._*` files; clean only the target folder | scr:sync_tree (excluded), ref:library-layout |
| X18 | Visual checks capture only the app window, never the full screen | ref:verification |
| X19 | Community research (for example Reddit) through whatever research tool the owner prefers | prof:preferences, sk:cheats |
| X20 | Save edits: back up, disable auto-load, edit with checksum repair, compare play time to confirm no lost progress | sk:cheats |
| X21 | Per-game tools folder `Tools/Cheats/<system>/<game>/` with README, emulator files, tools and data, mirrored to cloud | ref:library-layout, sk:cheats |
| X22 | ROM-patch cheats: free ROM space, hook a script special, block story-critical cases, test on real ROM and RAM | sk:cheats (technique), per-game folder (specifics) |
| X23 | Low-pass audio filter for harsh handheld audio | tool:retroarch, sk:configure |
| X24 | Preferences: standalone apps over store builds, windowed play, ROMs and media on the library drive | prof:preferences |
