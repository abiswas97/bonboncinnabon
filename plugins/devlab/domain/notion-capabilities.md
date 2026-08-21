# Notion capability contract

Before reading project data, map the active host's authenticated Notion connector to these operations:

| Capability | Required behavior |
|---|---|
| `search` | Find a project or task by name, issue key, or URL. |
| `fetch` | Fetch a page or database schema and content. |
| `query` | Query task records with filters, sorting, and pagination. |
| `create` | Create a page with properties and body content. |
| `update` | Update page content or properties. |

Use connector capabilities, not exact tool names. At the start of a workflow, enumerate the operations it needs and verify that each can be mapped. If one is absent, stop with `DevLab cannot continue: the authenticated Notion connector is missing <capability>.` Do not use web browsing as a substitute, request or persist credentials, or claim that a write succeeded without a connector result.

Every write remains an explicit effect: show the proposed change and obtain confirmation immediately before invoking `create` or `update`.
