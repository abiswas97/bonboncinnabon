# Legacy configuration migration

The legacy source is `.claude/devlab-notion.yaml`. It is read only when `.devlab/config.yaml` is absent.

Validate the legacy project name, Notion identifiers, nullable Product Spec, and source list before showing a neutral migration preview. Writing requires explicit confirmation, is refused when the neutral output already exists, and never deletes or changes the legacy file.
