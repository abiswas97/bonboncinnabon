---
name: standards
description: Explain Bonboncinnabon's engineering commandments and resolve the effective supporting standards for a repository, task, role, or path. Use when the user asks what standards apply, requests a standards review, wants a rule ID explained, or needs a conflict between repository guidance and portable defaults resolved.
---

# Standards

Use the canonical files under `${PLUGIN_ROOT}/standards/`; do not reproduce or invent standards from memory.

## Workflow

1. Read `commandments.md`.
2. Read `registry.json`.
3. Locate the repository root without changing files.
4. If `.standards/standards.json` exists, validate and resolve it:
   - `extends: "default"` merges defaults first and lets matching supporting-rule IDs override.
   - no `extends` replaces supporting defaults.
   - commandments and precedence are always retained and cannot be overridden.
5. Filter supporting rules by the requested lifecycle, role, and path. Treat an empty selector as universal. If the user omits lifecycle or role, state the assumption and use all relevant implementation phases (`plan` and `edit`) with role `implementation`.
6. Check `AGENTS.md`, `CLAUDE.md`, and narrower repository instructions relevant to the target. Explicit repository instructions win over supporting defaults; report conflicts.
7. Lead with applicable commandment or rule IDs and concise actions. Read detailed references only for cited rules. Resolve default references under `${PLUGIN_ROOT}/standards/`; resolve overlay references under the repository's `.standards/`.

## Constraints

- Correctness, safety, and explicit requirements precede all commandments.
- Never claim an overlay is valid without checking its schema, IDs, and selectors.
- Do not treat advisory guidance as a blocking policy.
- Do not read source contents merely to classify a path.
- Use the same glob semantics as the runtime: `**` crosses directories, `*` does not, and brace alternatives such as `*.{js,mjs}` enumerate extensions.
- Interpret `enforced` as non-negotiable guidance backed by a deterministic validator, `review` as requiring explicit review or evidence, and `advisory` as situational guidance. Hooks remain non-blocking for every class.
