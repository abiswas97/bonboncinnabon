# Safety

- Keep secrets and sensitive values out of prompts, logs, state, fixtures, and generated files.
- Prefer reversible operations and resolve destructive targets before acting.
- Make timeout, cancellation, retry, and idempotency behavior explicit.
- Preserve compatibility during migrations and mixed-version deployment.
- Fail with actionable context; do not silently substitute success.
