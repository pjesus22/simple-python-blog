# ADR-004: `BaseModel` With Slug Generation

## Status

Accepted

## Context

Every domain model needs `created_at`/`updated_at` plus a URL slug for audit
purposes; avoids repeating fields/boilerplate across `Post` and `Category`.

## Decision

Abstract `BaseModel` in `core` holding the three fields; save-time `slugify`
from `slug_source` attribute; slug unique plus `blank=True` (generation deferred
to save, only when unset). `core` stays a plain module (no `apps.py`, not in
`INSTALLED_APPS`).

## Consequences

Less boilerplate, centralized place for slug logic; every collision raise an
`IntegrityError` (not uniquer); slug immutable after set (regenerated only if
blank).

## Alternatives Considered

Explicit slug field per model (rejected - duplication); DRF-style serializer
slug (N/A, no DRF); unique auto-suffix on collision (rejected for v1)
