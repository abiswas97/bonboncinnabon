---
description: Break a Linear ticket or described work into a durable human task tree in TickTick
argument-hint: '[linear-ticket-id or description]'
---

Invoke the `intake` skill. It turns the work in $ARGUMENTS into human,
session-sized chunks and builds a durable task tree in TickTick. If a Linear
ticket ID is named it pulls that ticket (read-only); with no ID it uses the
described work. Idempotent — resumes an existing tree rather than duplicating it.

$ARGUMENTS
