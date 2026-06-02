---
description: Break down an existing TickTick task into session-sized chunks, interview-first and context-aware
argument-hint: '[task name or leave blank to pick from undecomposed]'
---

Invoke the `decompose` skill on the existing TickTick task in $ARGUMENTS. It
resolves the task (by name/search, or pick from undecomposed when none is named),
derives and confirms its context, runs a hard-gate interview, then breaks it down
context-aware — work into pipeline stages, personal into free-form steps or not at
all. The existing task becomes the parent. For NEW work not yet in TickTick, use
`/butler:intake`.

$ARGUMENTS
