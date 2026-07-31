# Clean code

- Use names that reveal domain meaning and units.
- Keep control flow shallow and effects explicit.
- Split modules by cohesive responsibility, not arbitrary line limits.
- Remove obsolete paths and placeholders when the replacement is complete.

## Durable comments

Comments should preserve information that the code cannot express clearly and
that remains true after the current task ends. Use them for:

- Non-obvious invariants, constraints, or trade-offs.
- External contracts, protocol details, and migration rationale.
- Safety reasoning and required public API documentation.
- Upstream workarounds with the live constraint and removal condition.
- Test-fixture behavior that would otherwise be misleading.

Good comments explain facts such as why a Rust `unsafe` block upholds its
safety contract, why a Go encoder must retain a legacy wire format, or why
Python timeout logic uses a monotonic clock. They describe the present
constraint rather than the work that introduced it.

Do not narrate the task, ticket, bug-fix history, phase, session, review
conversation, edit sequence, or obvious code behavior. For example, remove
comments such as `Fix 2: handle ENG-123`, `Phase 3: add validation`, or
`Increment retry counter`. A ticket reference is appropriate only when it
identifies a current external constraint or actionable workaround.

Generated headers, licenses, linter directives, safety comments, and required
API documentation are contracts, not narrative clutter. Judge comments by the
information they preserve, not their count, length, density, or vocabulary.
