# Releasing

Local plugins are versioned and tagged independently.

1. Update the canonical `plugins/<name>/plugin.json` version.
2. Add the matching `plugins/<name>/CHANGELOG.md` entry.
3. Run `npm run plugins:sync` and commit every projection.
4. Run `npm run validate`.
5. For Standards on macOS, run the authenticated host smoke:
   `BONBON_AUTHENTICATED_LIFECYCLE_SMOKE=1 npm run validate:lifecycle`.
6. Create an immutable `<plugin>--v<version>` tag only after validation.

The authenticated smoke installs into temporary Claude and Codex homes. Runtime
calls load the temporary Claude plugin through the existing authenticated profile
without copying credentials, while Codex links only the existing auth file. The
smoke trusts only the exact hook hashes returned by the current app-server and
records no prompt, source, or secret contents. It is deliberately excluded from
ordinary CI because it makes credentialed model calls.

Current intended tags:

- `butler--v0.11.0`
- `standards--v0.1.0`

Never reuse or move a published tag. Release a corrected patch version instead.
