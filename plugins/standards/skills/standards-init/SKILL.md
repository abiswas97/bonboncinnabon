---
name: standards-init
description: Propose or update a minimal `.standards/standards.json` repository overlay after inspecting existing instructions and architecture. Use when the user asks to initialize, customize, migrate, or clean up repository-specific standards. Never write the overlay until the user explicitly confirms the proposal.
---

# Standards Init

Create the smallest repository overlay that captures real local variation without copying portable defaults.

## Workflow

1. Read `${PLUGIN_ROOT}/standards/commandments.md`, `registry.json`, and the overlay schema.
2. Inspect the repository's `AGENTS.md`, `CLAUDE.md`, build manifests, test layout, and existing overlay.
3. Identify only evidenced repository-specific rules: narrower paths or roles, additional domain constraints, or intentional overrides of supporting defaults. Use `enforced` only when a deterministic repository validator exists, `review` when explicit evidence is required, and `advisory` for situational guidance.
4. Prefer `extends: "default"`. Omit it only when the user explicitly wants to replace all portable supporting rules.
5. Present the proposed JSON and explain each non-default rule.
6. Stop and request explicit confirmation before creating or changing `.standards/standards.json`.
7. For new repository-specific detail, propose a concise reference under `.standards/references/` and set the rule's `reference` relative to `.standards/`. Reuse a bundled reference only when it fully expresses the rule.
8. After confirmation, write atomically and validate the completed file and any reference. Preserve unrelated configuration.

## Overlay shape

```json
{
  "schemaVersion": 1,
  "extends": "default",
  "rules": []
}
```

Commandment IDs are reserved and cannot appear in overlays.
