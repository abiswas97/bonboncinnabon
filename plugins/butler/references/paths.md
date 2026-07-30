# Portable plugin paths

Butler runs in Claude Code and Codex.

- Bundled resources are relative to a skill's `SKILL.md`: plugin root `../..`, references `../../references/`, schemas `../../schemas/`, scripts `../../scripts/`, and template `../../config.example.yaml`.
- Resolve the persistent plugin data directory from the host-substituted `${PLUGIN_DATA}` token in Codex or `${CLAUDE_PLUGIN_DATA}` token in Claude. Use whichever token has become an absolute path. If neither token is substituted, stop and report that the host did not provide plugin data storage.
- Use the resolved literal data path for reads, writes, and directory creation. Do not rely on a similarly named shell environment variable because a bare agent shell may not be scoped to Butler.
- Store user configuration only at `<resolved-plugin-data>/config.yaml`. Never write it into the installed plugin package.
