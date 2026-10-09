# Installing on a device

Install only when the owner asks, or when the device's `install_opt_in` in the profile already says yes. Preparing a library package never implies installation, and never implies importing documents into a reader app (that is a separate opt-in).

Paths are relative to the plugin root.

## Before writing to a device

1. **Identify the device** by its profile id. Read its `connect`, `paths`, `systems`, `emulators`, `frontend` and `notes`. The notes hold quirks learned earlier; follow them.
2. **Connect the way the profile says.**
   - For `ssh`, use the alias (`ssh <alias>`, `scp`, or `ssh <alias> 'cat > "path"' < file` when remote paths need careful quoting). Do not reach for ADB or USB debugging by default.
   - If the connection fails, give the owner the profile's `connect.hints`.
3. **Read the device's live configuration to find real paths:** system or BIOS folder, save and state folders, override hierarchy. A path in the profile is a starting point, not proof. For RetroArch, see `references/tools/retroarch.md`.
4. **Back up first.** Run `scripts/snapshot.py --device ID --scope full` before installing, since installs touch games, BIOS, saves or frontend metadata. Take scoped recovery copies of any file you will replace.
5. **Check the frontend before touching its metadata.** Run the frontend baseline check, and get the owner's confirmation that the frontend is stopped. See `references/frontend-baseline.md`.
6. **Reviewer gate on the plan.** Write the install plan into the run ledger: each library file and its device path, metadata and collection edits, BIOS. Then run the reviewer gate from `references/verification.md` before writing anything.

## Writing

- **Game files.** Copy only the verified library files into the folder the device uses for that system (`systems.<system>.folder`, defaulting to the library system id).
- **Artwork.** Copy from the library's `Media/<system>/<category>/` into the frontend's media folders under the same ROM stem. For ES-DE, see `references/tools/es-de.md`.
- **Manuals.** Copy into the frontend's manuals category only when requested. The canonical PDF stays in the library's `Documents`.
- **BIOS.** Copy only what the system needs and only from the owner's files. Never copy BIOS speculatively.
- **Existing state.** Preserve gamelist entries, play history, collection presentation and every existing setting.
- **Collections.** Membership follows existing rules in the profile or a concrete choice the owner made. Edits waiting for the frontend to stop stay in the library's `Frontends/<app>/<device>/Prepared/`. Never describe them as current device state.

## After writing

- **Re-hash** every transferred file on the device and compare it with the library: `scripts/checks.py device-hashes --device ID --map <run>/install-map.json`, where the map is `{"<device path>": "<library path>"}`.
- **Re-read** frontend metadata and collection files. Compare play counts and last-played times in each touched gamelist with the pre-install snapshot; none may go backwards. Then run the baseline check again.
- **Snapshot again.** Take a `full` snapshot after the change, so the new state is recoverable too.
- **Report each kind of evidence separately:** files verified, frontend display (seen by the owner or in a window-only capture), and an observed game launch. Without an observed launch, report runtime as pending.

## A new kind of device

For a device or emulator the plugin has not seen before:
- **Discover before assuming:** its supported file formats, storage paths, artwork mapping, BIOS needs and a safe way to update its metadata. Do not carry assumptions over from another device.
- **Record what you learn** as profile entries (`systems`, `emulators`, `frontend`) and notes.
- **Add a `references/tools/<tool>.md`** when the knowledge is about the tool rather than the owner's setup.
