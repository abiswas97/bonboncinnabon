# ES-DE

Verified against ES-DE 3.5.0 on Android and macOS on 2026-10-09. Sources: https://gitlab.com/es-de/emulationstation-de (USERGUIDE.md, INSTALL.md, THEMES.md). Re-check when a device runs a different version. Each device's ES-DE home, settings file and baseline are in the profile under `frontend`.

## Files

- **Home folder:** `~/ES-DE` on macOS. On Android it is wherever the app was pointed, often on the SD card.
- **`settings/es_settings.xml`:**
  - holds every setting as `<bool|int|float|string name=".." value=".." />` elements, with no single root element
  - `ROMDirectory` and `MediaDirectory` point at games and artwork
  - may hold scraper account fields, so never print it whole
- **`gamelists/<system>/gamelist.xml`:** per-game metadata and play history (play count, last played) and per-game alternative emulators.
- **`collections/custom-<name>.cfg`:** one absolute ROM path per line (or `%ROMPATH%/...`). These are device-specific projections of the library manifest's collections.
- **`custom_systems/es_systems.xml` and `es_find_rules.xml`:** override the bundled system definitions and emulator lookup.
- **`downloaded_media/<system>/<category>/<ROM stem>.<ext>`** (or the configured `MediaDirectory`). Categories include `covers`, `screenshots`, `titlescreens`, `marquees`, `videos`, `miximages` and `manuals`.
- **Logs:** `logs/es_log.txt` shows startup, which confirms a restart.

## Behaviour that matters

- **ES-DE rewrites its settings, gamelists and collections while running and on exit.** Edit them only after the owner confirms ES-DE is stopped, then re-read and rebase so newer play history survives (`references/frontend-baseline.md`).
- **Custom sort names are shared.** A game's custom collection sort name applies in every custom collection containing it, so per-collection ordering cannot be set independently.
- **Grouping custom collections.** Custom collections can be grouped under one "Collections" entry. Keep the owner's grouping and startup and carousel choices.
- **Art is matched by stem.** Artwork is matched by the exact ROM stem, so copy library `Media/<system>/<category>/<stem>.<ext>` into the same category and stem.
- **One manual per game.** The `manuals` category takes one PDF per game. To combine several documents, put them in this order: the In Box booklet, other In Box material, then Documentation, then Guides. Convert hack readmes to pages. The canonical PDFs stay in the library's `Documents/`.
- **Artwork for Android apps** imported into ES-DE goes to `miximages`. A theme that shows only covers will hide those icons unless its image types include `miximage`.

## Themes

- **Variants can be tied to one aspect ratio.**
  - A theme variant defined only in one aspect-ratio file (for example `aspect-ratio-8-7.xml`) falls back to a bare text list on screens with other ratios.
  - When the same theme runs on devices with different screens, pick a variant defined for every ratio in use, and record the variant per device in its baseline.
- **Media-dependent layouts.** A variant's `noMedia` trigger switches to a basic layout when the configured `mediaType` is missing. Check which media types the trigger lists when art seems to vanish.
- **Video autoplay.** Some list variants play game videos after a delay. An `iterationCount` of `0` loops forever, and a very long delay is not a reliable way to stop playback. Use a still-image variant when the owner wants no video.
- **Local theme edits are lost on reinstall.** Keep the modified theme in the library's `Frontends/<app>/<device>/Current/` and note the edits in the device baseline.

## macOS

- **No windowed flag.** ES-DE 3.5 has no `--windowed` option. `--resolution W H` runs it in a window, for example from a small launcher app that runs `open -a ES-DE --args --resolution 1600 900`. Useful test flags: `--fullscreen-padding 0` and `--no-update-check`.
- **Windowed emulators lose focus.** This is a known macOS bug: windowed emulators launched by ES-DE stay behind its window. The working fix is to launch through LaunchServices:
  1. Add a find rule in `custom_systems/es_find_rules.xml` whose staticpath entry is `<emulator binary>|/usr/bin/open -W -n -a <Emulator.app> --args`.
  2. Point the system commands in `custom_systems/es_systems.xml` at that rule (`%EMULATOR_<RULE-NAME>%`).
  3. Quitting the emulator returns to ES-DE. Closing content alone does not.
- **Removable-volume permission.** The first launch that reads a removable volume makes macOS ask the owner to allow access. Ask them to click Allow; you cannot.
- **Keep ROMs and media on the library drive.** Point `ROMDirectory` and `MediaDirectory` at the library drive so the Mac stores neither. ES-DE then needs the drive mounted.
- **Visual checks.** Capture only the ES-DE window (find its window id, then `screencapture -l <id>`), never the full screen.

## Android

- **Turning ES-DE off.** ES-DE is usually the home app. The owner may use a key-mapper shortcut to switch home apps and stop ES-DE before metadata edits; the device notes record how.
- **Adding Android apps.** ES-DE's built-in Game importer (Start, Utilities, Game importer) replaced the old ES AppLauncher, which is obsolete since 2025-07-15. It saves app icons as `miximages`.
- **macOS sidecar files.** `._*` files copied from macOS make ES-DE log skipped-file warnings. Clean them from the folder you copied.
- **What can't be checked over SSH.** Termux over SSH can read and write ES-DE files on shared storage. It cannot stop other apps or read Android settings, so ask the owner for those steps.
