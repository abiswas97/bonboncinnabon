---
description: "Set up or reconfigure butler: interview and write the global config"
---

Invoke the `setup` skill. It interviews you for Butler's user-specific values
(timezone, TickTick work/personal projects, planning list, calendar source, work
window) and writes them to the host-provided persistent plugin-data config, which
survives plugin updates. Idempotent:
re-run to change individual fields. It validates what it writes.

$ARGUMENTS
---
-description: Set up or reconfigure butler: interview and write the global config
+description: "Set up or reconfigure butler: interview and write the global config"
---
