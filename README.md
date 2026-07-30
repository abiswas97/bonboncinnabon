# bonboncinnabon

A portable plugin marketplace for Claude Code and Codex. The repository keeps host-neutral metadata as the source of truth and commits generated Claude and Codex packages so consumers do not need a build step.

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
Claude Code may ask you to review hook definitions once after installation or
when those definitions change; marketplace addition and plugin installation do
not bypass that host confirmation.

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

Start a new task after installing or refreshing so Codex reloads the plugin's skills and hooks. Codex may ask you to review the exact hook definitions once after installation or when they change.

## Codex Desktop

Codex Desktop and the CLI share the configured local marketplaces and installed packages. Add the marketplace with the CLI command above, then open **Settings → Plugins**, select Bonboncinnabon, and install Butler or Standards. Start a new task after installation. Hook trust is explicit and may require one-time review in either surface.

For an imported workspace plugin, use **Refresh** on the plugin to pull a newer marketplace version. Installation availability can depend on workspace policy and role; see OpenAI's current [plugins documentation](https://help.openai.com/en/articles/20001256-plugins-in-codex).

## Standards behavior

Standards is automatic: hooks inject all ten commandments at root session start,
after compaction, and when a subagent starts. Subagents receive the commandments
and precedence rule without the supporting index or Git context. Planning and
editing guidance uses compact rule IDs, is capped, and is deduplicated when host
session storage is available. If a Codex surface does not report Plan mode,
session guidance remains the portable fallback.

The Standards command and skills are optional inspection and overlay-initialization
tools; normal use does not require invoking them. Version 1 is advisory: hooks do
not deny tools, auto-approve permissions, request confirmation, or force
continuation. Verification guidance arrives during planning and editing, while
deterministic repository and CI validators are the hard release gates.

Adding the marketplace, installing the plugin, and confirming hooks are separate
steps controlled by each host. Claude Code and Codex may request a one-time hook
review after installation or whenever definitions change. Codex CLI and Desktop
share the plugin but retain explicit hook trust.

Repository overlays live at `.standards/standards.json`. `extends: "default"` retains portable supporting rules; omitting it replaces supporting defaults. Commandments cannot be removed or redefined.

Session state contains only a host name, hashed session identifier, delivered rule IDs, and timestamps. It is pruned after seven days. No prompts, diffs, source, environment values, or credentials are stored.

## Requirements and boundaries

- macOS or Linux
- Node 22 for plugin hooks and repository tooling
- Windows support is deferred
- Language-specific Rust, Python, Go, TypeScript, and other analyzers are deferred; version 1 remains language-neutral
- Standards has no MCP server
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
- **Standards hooks need review:** confirm the exact current definitions in the host; installing or updating a plugin never auto-approves hook trust.
- **Butler cannot find its config:** run the setup skill and confirm the host substituted one of the persistent plugin-data tokens described in `plugins/butler/references/paths.md`.
