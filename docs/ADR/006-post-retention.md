# ADR-006: Deleted Post Retention and Permanent Deletion

## Status

Accepted

## Context

ADR-001 defines soft deletion: a deleted post stays in the database and can be
restored. Deleted rows therefore accumulate unless a maintenance process removes
them. Permanent deletion is destructive and must not be reachable from the
public API.

## Decision

- The retention period is configured by `POST_RETENTION_DAYS` and defaults to 30
  days.
- The cutoff is `timezone.now() - timedelta(days=POST_RETENTION_DAYS)`.
- The `purge_deleted_posts` management command permanently deletes only rows
  with `status=deleted` and `deleted_at` at or before the cutoff.
- `--dry-run` reports the matching post slugs and deletes nothing.
- The command runs manually as a maintenance operation. No API endpoint exposes
  permanent deletion.
- Draft and published posts are never purged.

## Consequences

### Positive

- Retention is configurable per environment without a code change.
- Soft-deleted posts stay recoverable for a known period.
- Permanent deletion stays outside the request path and outside authorization
  rules for the API.
- `--dry-run` allows an operator to inspect the purge set before it runs.

### Negative

- Purge requires an external scheduler or manual run; the application does not
  schedule it.
- Permanent deletion is irreversible and has no audit trail beyond the command
  output.

### Alternatives Considered

#### Run the Purge from a Request or Signal

Rejected because a destructive bulk delete must not depend on request traffic,
and the public API must not expose permanent deletion.

#### Purge On `updated_at`

Rejected because any later write would extend retention and make the deletion
date inaccurate.

#### Hard Delete Immediately

Rejected by ADR-001: deleted posts must remain recoverable.
