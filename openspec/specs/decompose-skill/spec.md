# decompose-skill Specification

## Purpose

Defines the `butler:decompose` skill, which talks through breaking down a task
that ALREADY exists in TickTick. It resolves the target task, derives and confirms
its context, augments already-split tasks without duplication, decomposes per
context behind the interview gate, re-parents and confirms linkage, and offers the
context-appropriate next step.

## Requirements

### Requirement: decompose breaks down an existing TickTick task

The system SHALL provide a `butler:decompose` skill that talks through breaking
down a task that ALREADY exists in TickTick. It SHALL trigger on requests to
"break down / decompose / scope / think through" a named existing task. It SHALL
NOT create a new top-level work unit (that is `intake`'s job); the existing task
becomes the parent.

#### Scenario: Skill triggers on an existing-task breakdown request

- **WHEN** the user asks to break down or scope a task that is already in TickTick
- **THEN** `butler:decompose` is the skill used

### Requirement: decompose resolves the target task

The skill SHALL resolve the target task either from the user's arguments (title
search, then confirm the match) OR, when none is named, by listing undecomposed
candidates (tasks with no `childIds`) and letting the user pick.

#### Scenario: Resolve by name search

- **WHEN** the user names or describes a task
- **THEN** the skill searches TickTick, presents the best match, and confirms it before proceeding

#### Scenario: Pick from undecomposed candidates

- **WHEN** the user names no task
- **THEN** the skill lists tasks that have no children and asks the user to pick one

### Requirement: decompose derives and confirms context

The skill SHALL derive the resolved task's context from its project and confirm it
with the user before decomposing, per the task-contexts capability.

#### Scenario: Context confirmed before decomposing

- **WHEN** a task is resolved from a project mapped to a context
- **THEN** the skill states the derived context and confirms it with the user before generating any chunk

### Requirement: decompose augments an already-split task

When the resolved task already has children, the skill SHALL read the existing
chunks, talk through gaps, and augment or refine WITHOUT duplicating existing
chunks.

#### Scenario: Augment rather than duplicate

- **WHEN** the resolved task already has child chunks
- **THEN** the skill reads them, discusses what is missing, and adds only new chunks, leaving existing chunks intact

### Requirement: decompose decomposes per context

After the interview gate, the skill SHALL decompose according to the confirmed
context. Work tasks SHALL be split into pipeline stages (`stage: qualifier`, with
`intensity`/`ai_discount`/`est0_min`). Personal tasks SHALL be split into free-form
session steps OR, when the work is a single action, SHALL NOT be decomposed — the
skill SHALL instead offer to schedule/cue it. The default for personal tasks SHALL
be to not over-shred.

#### Scenario: Work task split into stages

- **WHEN** the confirmed context is `work`
- **THEN** chunks are pipeline stages titled `stage: qualifier` carrying intensity, ai_discount, and est0

#### Scenario: Personal task split into free-form steps

- **WHEN** the confirmed context is `personal` and the work is multi-step
- **THEN** chunks are 2–4 concrete session-sized steps with no stage/intensity/ai_discount

#### Scenario: Single-action personal task is not decomposed

- **WHEN** the confirmed context is `personal` and the work is a single action
- **THEN** the skill does not create child chunks and instead offers to schedule or cue the single task

### Requirement: decompose re-parents and confirms linkage

On confirmation, the existing task SHALL become the parent (its title/content
optionally tidied to parent form). Chunks SHALL be created as child tasks with
`parentId` set, `kind: TEXT`, and the `ai` tag. The skill SHALL re-read the parent
(`get_task_by_id`) to confirm `childIds` are linked, because the create response is
stale.

#### Scenario: Children created and linkage re-read

- **WHEN** the user confirms the proposed chunks
- **THEN** the skill creates each chunk with `parentId` set, `kind: TEXT`, and the `ai` tag
- **AND** it re-reads the parent and asserts `childIds` contains the new chunks before reporting success

### Requirement: decompose offers the next step

After building the tree, the skill SHALL offer the context-appropriate next action:
`butler:plan` for work, or setting a light reminder for personal.

#### Scenario: Next step matches context

- **WHEN** decomposition completes for a work task
- **THEN** the skill offers `butler:plan`
- **AND WHEN** it completes for a personal task, it offers to set a light reminder
