# Standards

Portable engineering commandments and low-noise lifecycle guidance for Claude Code and Codex.

## What it does

- Loads all ten commandments at session start and after compaction.
- Selects supporting rules by lifecycle, role, and affected path.
- Uses compact rule IDs after the initial load.
- Keeps successful or irrelevant hooks silent.
- Stores only minimal delivery metadata for deduplication and prunes it after seven days.
- Never blocks a tool or forces a continuation loop in version 1.

Use `/standards:standards` in Claude or `$standards` in Codex to inspect the effective rules. Use the initialization skill to propose a repository overlay; it must ask before writing.

The canonical policy is under `standards/`. Generated host manifests, skill metadata, and hook maps are produced from the repository's neutral plugin records.

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

Version 1 supports macOS and Linux with Node 22. It is language-neutral and does not run formatters, compilers, linters, or regex security scans.
