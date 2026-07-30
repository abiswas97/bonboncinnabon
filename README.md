# bonboncinnabon

A portable personal plugin marketplace for Claude Code and Codex. The repository keeps host-neutral metadata as the source of truth and commits generated Claude and Codex packages so consumers do not need a build step.

## Plugins

| Plugin | Claude | Codex | Purpose |
|---|---:|---:|---|
| `butler` | yes | yes | Executive-function-friendly task decomposition and daily planning |
| `standards` | yes | yes | Ten engineering commandments and scoped, advisory lifecycle guidance |
| `devlab` | yes | no | External repository; native Codex package not published here |
| `postgres` | yes | no | External repository; native Codex package not published here |

## Claude Code

From a Claude Code session:

```text
/plugin marketplace add abiswas97/bonboncinnabon
/plugin install standards@bonboncinnabon
/plugin install butler@bonboncinnabon
```

Or from a shell:

```sh
claude plugin marketplace add abiswas97/bonboncinnabon
claude plugin install standards@bonboncinnabon
claude plugin install butler@bonboncinnabon
```

In the Claude Desktop Code surface, open the plugin manager in a Code session and use the same marketplace and plugin identifiers. Restart Claude after an update so the new package is loaded.

Refresh or remove:

```sh
claude plugin marketplace update bonboncinnabon
claude plugin update standards@bonboncinnabon
claude plugin uninstall standards@bonboncinnabon
```

`claude plugin update` requires a restart to apply.

## Codex CLI

```sh
codex plugin marketplace add abiswas97/bonboncinnabon
codex plugin add standards@bonboncinnabon
codex plugin add butler@bonboncinnabon
```

Refresh or remove:

```sh
codex plugin marketplace upgrade bonboncinnabon
codex plugin add standards@bonboncinnabon
codex plugin remove standards@bonboncinnabon
```

Start a new task after installing or refreshing so Codex reloads the plugin's skills and hooks.

## Codex Desktop

Codex Desktop and the CLI share the configured local marketplaces and installed packages. Add the marketplace with the CLI command above, then open **Settings → Plugins**, select Bonboncinnabon, and install Butler or Standards. Start a new task after installation.

For an imported workspace plugin, use **Refresh** on the plugin to pull a newer marketplace version. Installation availability can depend on workspace policy and role; see OpenAI's current [plugins documentation](https://help.openai.com/en/articles/20001256-plugins-in-codex).

## Standards behavior

Standards injects all ten commandments only at session start and after compaction. Planning, editing, and completion guidance uses compact rule IDs, is capped, and is deduplicated when host session storage is available.

Version 1 is advisory: hooks do not deny tools, request confirmation, or force continuation. Deterministic repository and CI validators are the hard gates.

Repository overlays live at `.standards/standards.json`. `extends: "default"` retains portable supporting rules; omitting it replaces supporting defaults. Commandments cannot be removed or redefined.

Session state contains only a host name, hashed session identifier, delivered rule IDs, and timestamps. It is pruned after seven days. No prompts, diffs, source, environment values, or credentials are stored.

## Requirements and boundaries

- macOS or Linux
- Node 22 for plugin hooks and repository tooling
- Windows support is deferred
- Language-specific Rust, Python, Go, TypeScript, and other analyzers are deferred; version 1 remains language-neutral
- `devlab` and `postgres` remain external Claude entries and are deliberately absent from Codex

## Development

```sh
npm ci --ignore-scripts
python3 -m pip install -r requirements-dev.txt
npm run plugins:sync
npm run validate
```

Edit canonical files under `marketplace/`, `plugins/*/plugin.json`, and `plugins/standards/standards/`. Do not edit generated manifests directly; see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Troubleshooting

- **Plugin is missing:** upgrade/update the marketplace, confirm the marketplace name is `bonboncinnabon`, and inspect `claude plugin list --available --json` or `codex plugin list --available --json`.
- **Old skill is still loaded:** restart Claude or start a new Codex task.
- **Codex does not show `devlab` or `postgres`:** intentional until those repositories publish native Codex packages.
- **Standards repeats guidance:** the host did not provide a stable session ID or writable plugin-data directory; behavior remains correct but deduplication is unavailable.
- **Butler cannot find its config:** run the setup skill and confirm the host substituted one of the persistent plugin-data tokens described in `plugins/butler/references/paths.md`.
