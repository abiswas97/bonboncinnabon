---
name: sync
description: >
  Push repo state to Notion project page and Product Spec.
  Contains page layout knowledge and sync procedure.
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash
---

# DevLab Sync

<prerequisites>
  <gate name="config">
    Read `.claude/devlab-notion.yaml`. Extract project_page, product_spec.
    If missing: STOP. Tell user to run `/devlab:setup`.
  </gate>
</prerequisites>

<notion-page-layout>
  Entry Page (Content Tab):
  1. Hero callout with flat icon + one-liner
  2. Overview paragraph (2-3 sentences)
  3. Roadmap table (Pillar, Feature, Status: Done/In Progress/Planned/Next)
  4. Release and Distribution table (version, platform, distribution, framework)
  5. Divider
  6. Product Spec sub-page link

  Product Spec Sub-Page:
  1. Mission Statement (editorial, do not overwrite)
  2. Core Problem (editorial, do not overwrite)
  3. Vision and Scope (V1, V1.x, Long-Term)
  4. Key Features (shipped features with descriptions)
  5. Competitive Positioning (editorial, do not overwrite)
  6. Use-cases
  7. Original Ideation (toggle, historical)
</notion-page-layout>

<sync-rules>
  <rule name="editorial-protection">
    NEVER overwrite: Competitive Positioning, Mission Statement,
    Core Problem, Original Ideation, Use-cases.
    Only sync these if user explicitly requests.
  </rule>
  <rule name="additive-features">
    If openspec has a shipped change not in Key Features, add it.
    Do not remove features that exist in Notion but not in openspec.
  </rule>
  <rule name="roadmap-authoritative">
    CLAUDE.md Change Plan is the roadmap source of truth.
    Replace Notion roadmap table entirely when syncing.
  </rule>
  <rule name="version-always">
    Version and dates are factual. Sync without confirmation.
  </rule>
  <rule name="diff-first">
    Always show diffs before pushing. Get confirmation for content changes.
  </rule>
</sync-rules>

<procedure>
  <step name="gather">
    Read repo sources:
    - CLAUDE.md: architecture, conventions, change plan, version
    - openspec/changes/archive/: completed features (each dir = shipped change)
    - docs/plans/: implementation plans
    - package.json or tauri.conf.json: current version
    - git log --oneline -20: recent commits
    - git tag --sort=-creatordate | head -5: recent releases
  </step>

  <step name="build">
    Build content for each Notion section:

    Entry page:
    - Overview: synthesize from CLAUDE.md architecture + version + recent activity
    - Roadmap table: from CLAUDE.md Change Plan (archived = Done)
    - Release and Distribution: version from package config
    - Last Updated: today

    Product Spec (if product_spec is set):
    - Key Features: from CLAUDE.md + openspec archive
    - Vision and Scope: update only if repo has diverged
  </step>

  <step name="diff">
    Fetch current Notion page content. Compare section by section.
    Show: sections that will change (old -> new), sections in sync (skip),
    sections in Notion but not in repo (leave unchanged).
  </step>

  <step name="push">
    After user confirms, apply changes via Notion MCP notion-update-page.
    Report what was updated and skipped.
  </step>
</procedure>

<source-notion-mapping>
  | Repo Source | Notion Target | Section |
  |---|---|---|
  | CLAUDE.md Change Plan | Roadmap table | Entry page |
  | package.json / tauri.conf.json | Release and Distribution + Overview | Entry page |
  | CLAUDE.md Architecture | Overview paragraph | Entry page |
  | openspec/changes/archive/ | Roadmap (Done) + Key Features | Entry + Product Spec |
  | docs/plans/ | Roadmap (planned) | Entry page |
  | git tag | Current version | Entry page |
  | git log | Recent activity context | Overview |
</source-notion-mapping>
