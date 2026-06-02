---
description: Set up or reconfigure butler: interview and write the global config
---

Invoke the `setup` skill. It interviews you for butler's user-specific values
(timezone, TickTick work/personal projects, planning list, calendar source, work
window) and writes them to the global, machine-wide config at
`${CLAUDE_PLUGIN_DATA}/config.yaml`, which survives plugin updates. Idempotent:
re-run to change individual fields. It validates what it writes.

$ARGUMENTS
