## 1. Lifecycle Contracts

- [x] 1.1 Add failing adapter and runtime tests for startup, compact, prompt, edit, subagent, output-field, malformed-input, traversal, deduplication, budget, and Git-safety contracts
- [x] 1.2 Implement registered event mapping, source-aware session delivery, subagent delivery, and event-aware native responses
- [x] 1.3 Remove the neutral complete lifecycle from registry records, schemas, validators, fixtures, skills, and canonical specifications

## 2. Generated Host Artifacts

- [x] 2.1 Add failing generator tests for intentionally different hook maps, explicit Codex hook discovery, and host-correct command invocations
- [x] 2.2 Generate purpose-specific Claude and Codex hook maps and the explicit Codex hooks manifest field
- [x] 2.3 Upgrade the pinned Codex validator to 0.146.0 and derive its expected version from package metadata

## 3. Validation

- [x] 3.1 Keep deterministic installation tests scoped to installation shape and expand replay/schema/path-safety coverage
- [x] 3.2 Add an authenticated opt-in macOS lifecycle smoke command covering Claude and Codex lifecycle delivery and Codex app-server exact-hash trust
- [x] 3.3 Run the deterministic validation suite and authenticated lifecycle smoke

## 4. Documentation and Delivery

- [x] 4.1 Update README, Standards documentation, and the 0.1.0 changelog with automatic/advisory behavior and host confirmation requirements
- [x] 4.2 Sync the changed requirements into the main OpenSpec specifications and verify the implementation
- [x] 4.3 Archive the completed OpenSpec change after verification
