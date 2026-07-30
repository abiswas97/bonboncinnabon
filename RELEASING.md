# Releasing

Local plugins are versioned and tagged independently.

1. Update the canonical `plugins/<name>/plugin.json` version.
2. Add the matching `plugins/<name>/CHANGELOG.md` entry.
3. Run `npm run plugins:sync` and commit every projection.
4. Run `npm run validate`.
5. Create an immutable `<plugin>--v<version>` tag only after validation.

Current intended tags:

- `butler--v0.11.0`
- `standards--v0.1.0`

Never reuse or move a published tag. Release a corrected patch version instead.
