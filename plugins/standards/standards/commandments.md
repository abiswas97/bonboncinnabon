# The Ten Commandments

These are durable decision principles, not mechanical style rules.

## Precedence

Correctness, safety, and explicit requirements come first. When commandments compete, state the trade-off, prefer evidence over intuition, and minimize long-term change cost.

## C01. Architecture over local expedience

Preserve dependency direction, ownership, and boundaries. A locally convenient shortcut is expensive when it makes the system harder to reason about or change.

## C02. One authoritative representation

Give each behavioral fact one source of truth. Generate projections and views instead of maintaining synchronized copies by hand.

## C03. Proportional blast radius

Match the size of a change to the problem and its evidence. Avoid both speculative redesign and symptom patches that leave the cause intact.

## C04. Make variation explicit

Represent meaningful differences as data, types, strategies, or named policies. Do not hide domain variation in scattered conditionals or accidental conventions.

## C05. Prepare for evidenced change

Design changes so their behavior can be observed and verified. Define the contract, risks, and proof before relying on confidence or a green-looking command.

## C06. Legible structure

Optimize names, modules, and control flow for the reader. Prefer small cohesive units, explicit contracts, and comments only for non-obvious invariants.

## C07. Optimize for recovery of understanding

Assume the next reader has lost the current context. Leave code, tests, and decisions that let them reconstruct intent without archaeology or oral history.

## C08. Explicit effects, contract-tested seams

Keep side effects visible and dependencies directed inward. Test behavior at boundaries where data, time, concurrency, networks, files, or external systems enter.

## C09. Evidence over confidence

Do not claim completion from intuition, compilation alone, or a single happy path. Use fresh, proportionate evidence and report what remains unverified.

## C10. Model the domain; make invalid states unrepresentable

Use the type system, schemas, constructors, and state transitions to encode what is valid. Prefer designs where impossible combinations cannot be created over repeated defensive checks.
