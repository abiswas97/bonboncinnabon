# Frontend baselines

A device's frontend setup (theme, variant, collections, startup and carousel behaviour, launch rules) took deliberate work. It is recorded so that it can be checked, kept and rebuilt.

Paths are relative to the plugin root.

## Where the setup is recorded

The setup lives in two places, and both stay in step:
- **The profile:** `devices.<id>.frontend.baseline.settings` holds the settings the owner chose on purpose, as exact string values. Other `baseline` fields hold the theme, variant, collection presentation, custom systems and launch rules, plus free-text notes. It is a deliberate subset, not a copy of every setting.
- **The library:** `<root>/Frontends/<app>/<device label>/Current/` holds the full current frontend files (settings, collections, gamelists, custom systems, find rules, theme changes, launcher scripts). `Prepared/` holds edits that are waiting to be deployed.

## Check for drift

Before and after touching a device's frontend:

1. Get the live settings file. Locally, use the device's `frontend.settings_file` directly. Over SSH, copy it into the run's staging folder without printing it, for example `ssh <alias> 'cat "<settings_file>"' > <staging>/es_settings.xml`.
2. Run `scripts/esde_baseline.py check --settings <file> --device <id>`.
3. If the check reports drift, show the owner each key with its expected and found values, and ask whether to restore the baseline or adopt the new value. Adopting means updating the baseline with `scripts/gaming_profile.py set`.

## Changing a baselined value

Change a baselined value only when the owner asks. Update the device and the baseline in the same step, then refresh `Current/` from the device.

Onboarding and sync never change appearance: no new theme, variant, video autoplay or carousel change as a side effect. Approval to add games is not approval to change presentation. Discuss navigation, startup and theme changes first, and explain a theme edit before making it.

## Writing while the frontend runs

Frontends rewrite their metadata (gamelists, collections, settings) when they exit, so an external edit made while the frontend runs can be lost, or can overwrite newer play history.

- **Wait for the owner to confirm the frontend is stopped** before external writes to gamelists, collections or settings, when the device's `requires_stopped_confirmation` is true. A process check from a shell is not proof.
- **Prepare changes in `Prepared/` while waiting.**
- **After the owner confirms,** re-read the live files and rebase the prepared changes on them, so newer play counts and last-played times survive. Then deploy, re-read and re-check.

## Rebuild a frontend

For example, after a reinstall or a reset to defaults:

1. **Snapshot first.** Take a snapshot: `scripts/snapshot.py --device ID --scope config`.
2. **Confirm it is stopped.** Have the owner confirm the frontend is stopped.
3. **Restore from `Current/`:**
   - settings, collections, custom systems, find rules, launcher scripts and theme changes
   - gamelists, after rebasing them on any live play history
4. **Verify the result:**
   - Run the drift check.
   - Compare restored file hashes with `Current/`.
   - Ask the owner to confirm the frontend looks right, or use a window-only capture.

## Refreshing the library copy

After any change on a device:
1. Stage remote files first (`scp` into `<root>/Staging/<run>/frontend/`). Local frontends are read in place.
2. Refresh `Current/` one subfolder at a time (`settings`, `collections`, `custom_systems`, `gamelists`, `themes`, and each launcher app folder), with `scripts/sync_tree.py <source>/<sub> <Current>/<sub> <run>/evidence/<sub>.json --apply --preserve-conflicts --recovery-root <root>/Recovery/<device label>/<timestamp>-current-before-refresh`. Earlier versions are kept there, not inside `Current/`.
3. A subfolder that is a symlink (for example a theme shared from another device's `Current/`) is not copied. Record the link target in the device baseline notes instead.
4. A single launcher script file is copied with `cp` and checked by comparing SHA-256 hashes, because `sync_tree.py` copies folders.
5. Before updating the manifest, copy it to `<run>/manifest-before.json`. Re-record the entries for changed `Current/` files, then run `scripts/checks.py manifest-preserved <run>/manifest-before.json <root>/library-manifest.json --updated <file>` (once per re-recorded file) and `manifest --hash`.
