# Releasing

Local plugins are versioned and tagged independently.

1. Update the canonical `plugins/<name>/plugin.json` version.
2. Add the matching `plugins/<name>/CHANGELOG.md` entry.
3. Run `npm run plugins:sync` and commit every projection.
4. Run `npm run validate`.
5. Merge the version change to `main`. After both validation jobs pass, CI
   creates an immutable annotated `<plugin>--v<version>` tag on that exact merge
   commit.

Tag automation compares the pushed `main` commit with its `before` revision and
acts only when a canonical local plugin version changes. It never backfills a
missing historical tag. Existing tags are accepted only when they already point
to the release commit; tags are never moved.

Current intended tags:

- `butler--v0.11.0`
- `standards--v0.1.1`

Never reuse or move a published tag. Release a corrected patch version instead.
