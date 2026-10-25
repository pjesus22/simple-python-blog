# ADR-004: `BaseModel` With Slug Generation

## Status

Accepted

## Context

`Post` and `Category` both need a URL slug, `created_at` / `updated_at`
timestamps, and a deterministic default ordering. Repeating those fields in both
models adds boilerplate and makes the slug rules easy to diverge.

## Decision

Use an abstract `BaseModel` in the `core` module:

- `created_at` is set automatically on creation; `updated_at` on every save.
- `slug` is a unique `SlugField` with `blank=True`.
- `Meta.ordering` is `["-created_at", "-id"]`, so equal timestamps still page
  deterministically.
- `save()` generates the slug with `slugify` only when `slug_source` is set and
  the slug is empty. A slug is never regenerated after it has been set.
- `core` remains a plain module: it has no `apps.py` and is not listed in
  `INSTALLED_APPS`.

## Consequences

### Positive

- Shared fields and slug behavior live in one place.
- Lists have a deterministic newest-first order.
- Slugs stay stable when a post title or category name changes.

### Negative

- A slug collision raises `IntegrityError`; there is no automatic suffix or
  retry.
- The generic base model hides the slug source from the database schema, so the
  generating field must be found in the model class.

## Alternatives Considered

### Declare the fields separately in each model

Rejected because it duplicates the timestamp and slug logic.

### Use a serializer-level slug field

Not applicable because the project does not use a third-party REST framework.

### Generate a unique suffix on collision

Rejected for v1. A collision is an error, not a silently renamed resource.
