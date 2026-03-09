---
name: devlab-sync
description: >
  Knowledge of Dev Lab Notion page layout and sync logic for pushing repo state to Notion.
  Used by the /devlab:sync command and potentially by automated sync workflows.
---

# DevLab Sync Skill

## Dev Lab Page Layout

Every Dev Lab project page follows this structure:

### Entry Page (Content Tab)
1. **Hero callout** — flat icon + one-liner description
2. **Overview** — 2-3 sentences: what is this, current version, what's next
3. **Roadmap table** — columns: Pillar, Feature, Status (Done/In Progress/Planned/Next)
4. **Release & Distribution table** — columns: Field, Value (version, platform, distribution, auto-update, CI/CD, framework)
5. **Divider**
6. **Product Spec sub-page link**

### Product Spec Sub-Page
1. **Mission Statement** — one paragraph
2. **Core Problem** — the "why"
3. **Vision and Scope** — V1, V1.x, Long-Term
4. **Key Features** — bullet list of shipped features with descriptions
5. **Competitive Positioning** — landscape analysis + honest strengths/gaps
6. **Use-cases** — bullet list of target users
7. **Original Ideation** — toggle, historical context

### View Tabs (database views, auto-filtered by project relation)
- Tasks (collection://713f8ed9-13cd-4610-bcba-4dd80d83a67e)
- Features (collection://956f9882-1327-42c3-8104-35fef255ae2b)
- Existing Solutions (collection://c08ea5db-5512-4ef1-95b7-48892e8fac80)
- Resources (collection://9805f844-e132-4427-899c-36695e565061)
- Tech Stack Items (collection://8282046b-3a66-4148-b113-b94ebba884ea)

### Dev Lab Database Properties
Each project in Dev Lab has:
- Key: short 2-4 letter project identifier (e.g. FAM)
- Features relation → Features DB
- Tasks relation → Tasks DB
- Existing Solutions, Resources, Tech Stack Items → centralized DBs
- Courses, Papers and Notes, Videos → centralized learning DBs

## Source → Notion Mapping

| Repo Source | Notion Target | Section |
|---|---|---|
| `CLAUDE.md` Change Plan | Roadmap table | Entry page |
| `tauri.conf.json` / `package.json` version | Release & Distribution + Overview | Entry page |
| `CLAUDE.md` Architecture | Overview paragraph | Entry page |
| `openspec/changes/archive/` | Roadmap (Done items) + Key Features | Entry + Product Spec |
| `docs/plans/` | Roadmap (planned items) | Entry page |
| `git tag` | Current version | Entry page |
| `git log` | Recent activity context | Overview |

## Sync Rules

1. **Never overwrite editorial content** — Competitive Positioning, Mission Statement, Core Problem, Original Ideation, and Use-cases are editorial. Only sync these if the user explicitly requests it.
2. **Additive for features** — if openspec has a shipped change not in Key Features, add it. Don't remove features that exist in Notion but not in openspec (they may have been added manually).
3. **Roadmap is authoritative from CLAUDE.md** — the Change Plan in CLAUDE.md is the roadmap source of truth. Replace the Notion roadmap table entirely when syncing.
4. **Version and dates are always synced** — these are factual, no confirmation needed.
5. **Show diffs before pushing** — always show what will change and get confirmation for content changes.

## Features DB Schema

Collection: `collection://956f9882-1327-42c3-8104-35fef255ae2b`

| Property | Type | Values |
|---|---|---|
| Feature Name | title | — |
| Status | status | Idea, Brainstormed, Specced, In Progress, Shipped, Parked |
| Project | relation | → Dev Lab (limit 1) |
| Tasks | relation | → Tasks DB (1:many) |
| Priority | select | P0 — Critical, P1 — High, P2 — Medium, P3 — Low |
| Area | multi_select | Core, UX, Infrastructure, Performance, Growth, Integration, DX |
| Effort | select | XS, S, M, L, XL |
| Dates | date | Target date/range |
| Description | text | One-liner summary |
| Feature Key | formula | Project key + ID (e.g. FAM-1) |
| ID | auto_increment | Sequential |

## Config File Format

`.claude/devlab-notion.yaml`:

```yaml
project_name: <string>
notion:
  project_page: <uuid>
  product_spec: <uuid or null>
  features_db: <uuid>
  tasks_db: <uuid>
sync:
  sources:
    - CLAUDE.md
    - openspec/
    - docs/plans/
```
