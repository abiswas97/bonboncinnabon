# Contributing

## Canonical and generated files

Edit these sources:

- `marketplace/marketplace.json`
- `plugins/<name>/plugin.json`
- each skill's `SKILL.md`
- `plugins/standards/standards/**`

Do not directly edit these projections:

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `plugins/<name>/.claude-plugin/plugin.json`
- `plugins/<name>/.codex-plugin/plugin.json`
- `plugins/<name>/skills/*/agents/openai.yaml`
- `plugins/standards/hooks/claude.json`
- `plugins/standards/hooks/hooks.json`

Run `npm run plugins:sync` after changing canonical metadata and commit the resulting projections. Run `npm run plugins:check` to verify that committed output is current.

The generator supports macOS and Linux with Node 22. Plugin runtime code uses Node built-ins and has no package-install step.
