# The gaming profile

One JSON file holds what the owner would otherwise repeat every session: libraries, backup targets, devices and how to reach them, frontend baselines, policies and preferences. Claude Code and Codex share it.

Paths in this file are relative to the plugin root.

## Find and read it

- `python3 scripts/gaming_profile.py path` prints the location: `$XDG_CONFIG_HOME/bonboncinnabon/gaming/profile.json`, or `~/.config/...` when that variable is unset or relative.
- `python3 scripts/gaming_profile.py show [POINTER]` prints the whole profile or one part, for example `/devices/handheld/connect`.
- Exit code 2 means there is no profile yet. Stop and tell the owner to run the gaming `setup` skill. Never fall back to `profile.example.json`, whose placeholder paths would point work at folders that do not exist.

Read the profile at the start of every gaming task. Ask the owner only for what it lacks.

## What lives where

| Kind of information | Home |
|---|---|
| Library roots, mount volumes, extra folders to search, folders on the drive never to touch (`off_limits`) | `libraries` |
| Backup destinations, their scope and verification rules | `backup_targets` |
| How to connect (SSH alias or local), connection hints, storage paths | `devices.<id>.connect`, `paths` |
| Which emulator and core runs each system, emulator config locations | `devices.<id>.systems`, `emulators` |
| Frontend app, home, settings file, the deliberately chosen settings | `devices.<id>.frontend` (see `frontend-baseline.md`) |
| Standing permission to install games on a device | `devices.<id>.install_opt_in` |
| Durable device facts learned while working | `devices.<id>.notes` |
| Collection rules, policies, owner preferences | `collections`, `policies`, `preferences` |
| Game catalogue, collection membership, verification evidence | the library's `library-manifest.json`, not the profile |
| Actual frontend files and device snapshots | the library's `Frontends/` and `Recovery/` |

## Change it

Only `scripts/gaming_profile.py` writes the profile. It validates, keeps a copy of the previous file in `history/`, and replaces the file atomically.

1. Tell the owner what will change, then preview it: `set POINTER JSON --dry-run`, `unset POINTER --dry-run` or `note DEVICE TEXT --dry-run`.
2. Apply the same command without `--dry-run`.
3. If the write is refused for permissions, show the owner the entries from `skills/setup/SKILL.md` step 7. Do not work around the refusal.

Add a note when a fact will matter again, for example a connection quirk, an app that must stay whitelisted, or a setting that only works one way. A note is one dated line of at most 300 characters, with at most 50 per device. When the cap is reached, merge related notes with `set` rather than dropping information.

Never store:
- credentials of any kind (connections use SSH aliases, and secrets stay in SSH config or the host's credential store)
- the contents of emulator or frontend config files (they can hold account details)
- logs, run progress or verification evidence (those go in the run ledger or the library manifest)

## Policies and standing choices

- `no_automatic_deletions`: never delete, prune or mirror deletions. To retire something, move it to an archive or the Trash after the owner agrees.
- `preserve_conflicts`: when two versions differ, keep both until the owner names the authoritative one.
- `recovery_before_overwrite`: take a timestamped copy before replacing any file.
- `no_timestamp_winner_for_saves`: never pick the newer save by date, and never merge saves.
- Standing opt-ins (`install_opt_in`, enabled `backup_targets`, `collections.upkeep`) are honoured without asking again. Do not invent new targets, and never infer permission to install from a game's name.
- Apply `preferences` whenever they bear on a choice, for example windowed play or the owner's preferred research tool.

## Keep a copy in the library

After a successful `sync` or `backup`, copy the profile to `<library root>/Tools/profile.json` and compare SHA-256 hashes. The `~/.config` file stays the source of truth. On a new machine, `setup` can import the library copy.
