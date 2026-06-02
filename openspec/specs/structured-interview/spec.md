# structured-interview

## Purpose

Define how butler's interview-driven skills present questions: discrete decisions as
structured choice prompts (the harness AskUserQuestion tool), open-ended prompts as
free text, while preserving conversational discipline and degrading gracefully when
the tool is unavailable.

## Requirements

### Requirement: Discrete interview decisions are presented as structured choices

Discrete interview decisions in `intake` and `decompose` SHALL be presented using
the harness AskUserQuestion tool with suggested options rather than free-text prose.
A discrete decision is one that resolves to a choice from a known, finite set; this
SHALL cover at minimum the hard-gate confirmations (fresh-start vs already-begun;
single-action vs multi-step), stage selection / tree-shape confirmation, and
(decompose) the work-vs-personal context confirmation.

#### Scenario: Hard-gate confirmations offered as choices

- **WHEN** intake or decompose reaches the hard-gate questions of prior-progress and single-vs-multi-step
- **THEN** they are presented as structured options (e.g. "Fresh start" / "Already begun"; "Single action" / "Multi-step")
- **AND** the user can pick without typing, with an "Other" escape available

#### Scenario: Tree-shape confirmation offered as choices

- **WHEN** the skill has a proposed decomposition to confirm
- **THEN** the build/adjust decision is presented as structured options rather than asking the user to reply in prose

#### Scenario: Context confirmation in decompose offered as a choice

- **WHEN** decompose has derived a task's context from its project
- **THEN** the work-vs-personal confirmation is presented as a structured choice

### Requirement: Open-ended prompts remain free text

Interview prompts that elicit novel, unbounded input SHALL remain free text and
SHALL NOT be forced into structured options. This covers at least: done-criteria,
the first physical action, what is fuzzy or blocked, and estimate discussion.

#### Scenario: Open prompt stays conversational

- **WHEN** the skill asks what "done" looks like or what the first physical action is
- **THEN** it asks in prose and accepts a free-text answer, not a fixed option list

### Requirement: Structured prompts preserve conversational discipline and degrade gracefully

Structured prompts SHALL obey the existing interview discipline — one main thread at
a time, never a wall of questions — so the AskUserQuestion batch limit is a ceiling,
not a target. Questions SHALL also be phrased so they remain answerable as prose when
AskUserQuestion is unavailable (e.g. a non-Claude-Code harness); the skills SHALL NOT
hard-depend on the tool.

#### Scenario: No wall of questions

- **WHEN** several discrete decisions are pending
- **THEN** the skill still advances one main thread at a time rather than dumping the maximum batch of unrelated questions at once

#### Scenario: Prose fallback when the tool is absent

- **WHEN** the interview runs on a harness without AskUserQuestion
- **THEN** the same questions are still answerable as free-text prose and the interview completes
