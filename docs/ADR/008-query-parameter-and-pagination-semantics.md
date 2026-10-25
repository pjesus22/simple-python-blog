# ADR-008: Query Parameter and Pagination Semantics

## Status

Accepted

## Context

The public post list and the category list accept query parameters without a
REST framework to validate or normalize them. Django's `Paginator.get_page`
already defines fallback behavior, but the API contract must state it explicitly
and keep it stable across endpoints.

The post list adds `status` and `category` filters on top of pagination. Those
filters change what is counted and sliced, so their order and error behavior are
part of the public contract.

## Decision

- Collection page size comes from `API_PAGE_SIZE` (default `20`). The
  `page_size` query parameter is ignored and is not client-configurable.
- `page` is 1-based. A missing value or a non-integer value falls back to page
  1. A value below 1 or beyond the last page returns the last page. An empty
  collection returns page 1 with `total_pages` 1.
- Pagination metadata is always present, including for empty and out-of-range
  pages: `page`, `page_size`, `total`, and `total_pages`.
- `status` must be `draft`, `published`, or `deleted`. Any other value returns
  `400 validation_error` with a `status` field error.
- An anonymous request for a non-published `status` returns `403 forbidden`.
  An anonymous request without `status` is treated as `status=published`.
- An authenticated request without `status` returns all statuses.
- `category` is a category slug. An unknown slug returns `200` with an empty
  collection, not `404`.
- Filters are applied before counting and slicing, so `total` and
  `total_pages` describe the filtered collection.
- Collections are ordered by `-created_at`, then `-id`, to keep pagination
  stable when records share a timestamp.
- No other query parameter changes the response.

## Consequences

### Positive

- Clients get predictable fallbacks instead of endpoint-specific errors.
- Pagination metadata is always available.
- Filters and counts agree.
- Deterministic ordering prevents duplicate or skipped rows between pages.

### Negative

- Invalid `page` values do not produce an error, so a client bug can be silent.
- Page size cannot be tuned per request.
- The contracted behavior depends on Django's `Paginator.get_page` and must be
  retested when Django is upgraded.

## Alternatives Considered

### Reject invalid `page` values with 400

Rejected because the current behavior is a deliberate tolerant fallback for
public listings; clients that omit or mistype `page` still receive content.

### Use cursor pagination

Rejected for v1 because page numbers and total counts are part of the expected
response and SQLite datasets are small.

### Make `page_size` client-configurable

Rejected because it would require an upper bound and additional validation
without a current use case.
