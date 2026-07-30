# Standards

Portable engineering commandments and low-noise lifecycle guidance for Claude Code and Codex.

## What it does

- Loads all ten commandments in root sessions, after compaction, and for newly started subagents.
- Selects supporting rules by lifecycle, role, and affected path.
- Uses compact rule IDs after the initial load.
- Keeps successful or irrelevant hooks silent.
- Stores only minimal delivery metadata for deduplication and prunes it after seven days.
- Never blocks a tool, approves a permission, or forces a continuation loop in version 1.

Hooks provide the automatic behavior. You do not need to invoke a command or
skill to receive Standards. `/standards:standards` in Claude and `$standards` in
Codex are optional inspection tools; the initialization skill only proposes a
repository overlay and must ask before writing.

The canonical policy is under `standards/`. Generated host manifests, skill metadata, and hook maps are produced from the repository's neutral plugin records.

Claude Code and Codex may request a one-time hook review after installation or
whenever hook definitions change. Marketplace addition, plugin installation, and
hook confirmation remain separate host-controlled steps. Codex CLI and Desktop
share the installed plugin but maintain explicit hook trust.

## Repository overlays

Place an overlay at `.standards/standards.json`:

```json
{
  "schemaVersion": 1,
  "extends": "default",
  "rules": []
}
```

With `extends: "default"`, repository rules add to or override supporting defaults. Without it, repository rules replace supporting defaults. The ten commandments and precedence rule are immutable.

## Boundaries

Version 1 supports macOS and Linux with Node 22. It is language-neutral and does
not run formatters, compilers, linters, regex security scans, or an MCP server.
