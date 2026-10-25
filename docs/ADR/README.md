# Architecture Decision Records

Each ADR records a decision that affects the architecture, data model, security,
or API contract. All listed decisions are currently accepted.

| ADR | Title                                                        | Status   |
| --- | ------------------------------------------------------------ | -------- |
| 001 | [Post lifecycle state transitions](001-post-lifecycle.md)     | Accepted |
| 002 | [Database selection](002-database-selection.md)               | Accepted |
| 003 | [JSON response format](003-json-response-format.md)           | Accepted |
| 004 | [`BaseModel` with slug generation](004-base-model-slug.md)    | Accepted |
| 005 | [Centralized error handling](005-centralized-error-handling.md) | Accepted |
| 006 | [Deleted post retention and permanent deletion](006-post-retention.md) | Accepted |
| 007 | [CSRF exemption and authorization](007-csrf-exemption-and-authorization.md) | Accepted |
| 008 | [Query parameter and pagination semantics](008-query-parameter-and-pagination-semantics.md) | Accepted |

New records use the same structure: Context, Decision, Consequences, and
Alternatives Considered, with an explicit status.
