# RetroArch

Verified against RetroArch 1.21.0 (Android) and 1.22.2 (macOS) on 2026-10-09, using the RetroArch source and docs at https://docs.libretro.com. Re-check when a device runs a different version. The profile's `emulators.retroarch` entry holds each device's version and paths.

## Where settings live

- **Main config:**
  - Android: `/storage/emulated/0/Android/data/<package>/files/retroarch.cfg`
  - macOS: `~/Library/Application Support/RetroArch/config/retroarch.cfg`
- **Core override:** `config/<Core>/<Core>.cfg`
- **Content-folder override:** `config/<Core>/<folder>.cfg`
- **Game override:** `config/<Core>/<ROM stem>.cfg`
- **Remaps:** `config/remaps/<Core>/` with `<Core>.rmp`, `<folder>.rmp` or `<ROM stem>.rmp`
- **Core options:** `config/<Core>/<Core>.opt`, or per-game `<ROM stem>.opt`
- **Configured folders.** `rgui_config_directory`, `input_remapping_directory`, `joypad_autoconfig_dir` and `core_options_path` in the main config can move these. Read them before assuming defaults. Relative values need resolving before use.
- **System (BIOS) folder.** Read the active `system_directory` before placing BIOS.
- **Cheats:** `cheats/<Core>/` on Android and `cht/<Core>/` on macOS (check `cheat_database_path`).

## How layers combine

- **Overrides stack:** core, then content folder, then game, with the later one winning per key.
- **Remaps do not stack:** only one loads, the first found of game, content folder, core.
- **Overrides block global menu changes.** While an override is active, saving the main config is refused, or the override is unloaded and the config re-read first. When every core in use has an override, menu changes made during a game are discarded. Make lasting global changes from the main menu with no content loaded, or by editing the file while RetroArch is closed.
- **Remap files get rewritten.** `remap_save_on_exit = "true"` rewrites the active remap file on exit, which overwrites hand-written remaps. Keep it `"false"`, and save remaps explicitly from the Quick Menu when wanted.
- **`--appendconfig` values persist.** They are written back into the main config on exit when `config_save_on_exit` is on. Restore any value you appended for testing.

## Input and hotkeys

- **Hotkey enable is all-or-nothing per config.** When `input_enable_hotkey_btn` is set, every hotkey needs it. To make some hotkeys work alone for one core family:
  1. Clear the enable button in those cores' overrides.
  2. Unbind the buttons the game would otherwise also receive, with `input_player1_btn_<x> = "-1"` in the core remap.
- **Gamepad combo codes:**
  - `input_quit_gamepad_combo`: `4` = Start+Select.
  - `input_menu_toggle_gamepad_combo`: `7` = hold Start.
  - When using the combo to quit, clear Start's own exit bind.
- **Android bind values are keycodes:** 96 A, 97 B, 99 X, 100 Y, 102 L1, 103 R1, 104 L2, 105 R2, 108 Start, 109 Select.
- **One action per button.** The owner wants one action per button. When a button is both a hotkey and a turbo or game input, unbind one side.
- **Cores bring their own turbo and fast-forward options.** For example:
  - Gambatte and mGBA expose X/Y turbo A/B.
  - mGBA has L2/R2 turbo L/R.
  - Gambatte has an R2 fast-forward that blocks RetroArch's fast-forward hotkeys while held.

  Read the core options before blaming RetroArch bindings.

## Audio and video

- **Harsh handheld audio.** Enable `mgba_audio_low_pass_filter` (range around `50`) in `mGBA.opt` for GBA sound that is harsh or tinny on earphones.
- **Shaders.** `video_shader_enable` is often turned on per core by an override even when it is off globally. Check overrides before changing shaders globally.

## Cheats

- **Game cheat file naming.** RetroArch 1.21 on Android strips the extension twice when it builds the game cheat file name. `Game 1.0.2.gba` loads `cheats/<Core>/Game 1.0.cht`. Overrides, remaps and saves keep the full name. Install both names with identical content.
- **Applying cheats at launch.** `apply_cheats_after_load = "true"` in a game override applies the cheat file at launch. Turn `savestate_auto_load` off for any game whose save you edit outside RetroArch, otherwise the auto-state overwrites the edit.
- **mGBA cheat engine:**
  - All enabled cheats form one set, with at most one hook.
  - The code type is autodetected from the first `8+8` line, and a first line whose second word is `001DC0DE` forces raw GameShark mode.
  - CodeBreaker writes cannot patch ROM. GameShark v1 type 6 or Action Replay (PAR) v3 patch lines can.
  - Disabling a cheat or resetting cheats does not remove hooks or undo ROM patches. Close Content and relaunch.
  - Do not mix encrypted and raw formats in one set.
- **Debugging cheat loading.**
  1. Set `log_to_file` and `log_verbosity` to `"true"` and launch the game.
  2. Look for `[Cheats]: Load game-specific cheatfile` in `RetroArch/logs/retroarch.log`.
  3. Turn both settings back off.
- **Network commands differ by platform.** Desktop builds support network commands, such as `READ_CORE_MEMORY` with `network_cmd_enable`, which are useful to read back a patch from a running game. Android builds have none. Turn the setting back off afterwards.

## Save states and testing

- **State file format.** Save states are RZIP: a `#RZIPv\x01#` header, zlib chunks, then a `RASTATE` block, then the core's state. For mGBA, the core data starts at offset 16, with IWRAM at +0x19000, EWRAM at +0x21000 and IO at +0x400. This is useful for reading game RAM without running the emulator.
- **Headless test run (desktop):** `RetroArch -L <core> <rom> --verbose --max-frames=N --max-frames-ss`.

## Snapshot scope

A config snapshot covers `.cfg .opt .rmp .slangp .glslp .cgp` files:
- in the main config's folder
- in the standard config, autoconfig and remap folders
- in every folder named by the configured-path keys above

These map to the profile's `config_dirs`, `config_keys` and `config_extensions`.

A full snapshot adds the folders named by `savefile_directory`, `savestate_directory` and `system_directory`. These map to the profile's `data_keys`; a value of `default` falls back to the profile's `paths`. On macOS, paths in the config are stored as `~/...` and resolve to the user's home.

Some app-private folders (for example under `/data/user/0/<package>/`) are unreadable without root. Record them as gaps, not as backed up.
