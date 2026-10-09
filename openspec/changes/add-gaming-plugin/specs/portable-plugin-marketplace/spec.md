## ADDED Requirements

### Requirement: Gaming plugin is portable and validated

`gaming@bonboncinnabon` MUST be discoverable and installable through both generated marketplaces. Its `SKILL.md` files MUST have only `name` and `description` frontmatter and MUST stay under 8,000 bytes. They MUST NOT contain host-only patterns (`$ARGUMENTS`, `CLAUDE_SKILL_DIR`, `mcp__` tool IDs, `/gaming:` command references, model pins) or capitalised emphasis words. Repository validation MUST run the gaming portability test and every gaming script test.

#### Scenario: Validation run

- **WHEN** `npm run validate` runs
- **THEN** the gaming projections are checked for drift
- **AND** the gaming portability test and Python script tests run and pass

#### Scenario: Host-only pattern introduced

- **WHEN** a gaming skill references `$ARGUMENTS`
- **THEN** the portability test fails and names the file and pattern
