# API

## Overview

- Base path: `/api/v1/`
- Request and response bodies are JSON. Requests that carry a JSON body must
  use `Content-Type: application/json`; bodyless lifecycle and delete requests
  have no such requirement.
- Authentication uses Django's session cookie. `POST /auth/login` sets
  `sessionid`; `POST /auth/logout` clears it.
- Write and lifecycle operations require an authenticated session. Only
  administrator accounts are provisioned; any authenticated user may write.
- Timestamps are ISO 8601 strings in UTC, for example
  `2026-10-25T04:22:02.768517+00:00`.
- The API is CSRF-exempt and relies on the JSON-only request rule and Django's
  default `SameSite=Lax` session cookie. See `ADR/007`.

Permanent deletion is a maintenance operation, not an API operation. See
[Retention](#retention).

## Authentication

### `POST /auth/login`

Request:

```json
{ "username": "admin", "password": "change-me" }
```

Response `200`:

```json
{ "id": 1, "username": "admin" }
```

- `username` and `password` are required non-empty strings.
- A non-JSON content type, malformed JSON, or a non-object JSON body returns
  `400 invalid_request`.
- Missing or empty credentials return `400 missing_credentials`.
- Wrong credentials return `401 invalid_credentials`.
- The response exposes only the user id and username.

### `POST /auth/logout`

- Requires an authenticated session.
- Returns `204` with an empty body and invalidates the session.
- An anonymous request returns `401 unauthenticated`.

## Response Format

- Single resource: the resource object, without a `data` wrapper.
- Collection: `{"items": [...], "pagination": {...}}`.
- Error: `{"error": {"code": "...", "message": "..."}}`.
- Validation errors add `error.fields`, mapping field names to error lists.

See `ADR/003`.

## Status Codes

| Status | Use                                                                 |
| ------ | ------------------------------------------------------------------- |
| 200    | Read, update, lifecycle transition, soft delete                     |
| 201    | Post or category created                                            |
| 204    | Logout or category deletion; empty body                             |
| 400    | Invalid JSON, missing credentials, validation failure, bad `status` |
| 401    | Authentication required or bad credentials                          |
| 403    | Anonymous request for a non-published `status`                      |
| 404    | Unknown slug, hidden post, unmatched `/api/` route                  |
| 405    | Method unsupported; response includes `Allow`                       |
| 409    | Disallowed lifecycle transition                                     |
| 500    | Unhandled server error                                              |

## Error Codes

| Code                  | Status | Cause                                                                  |
| --------------------- | ------ | ---------------------------------------------------------------------- |
| `invalid_request`     | 400    | Non-JSON content type, malformed JSON, non-object JSON, oversized body |
| `missing_credentials` | 400    | Login without username or password                                     |
| `invalid_credentials` | 401    | Wrong username or password                                             |
| `validation_error`    | 400    | Form or query parameter validation failed                              |
| `unauthenticated`     | 401    | Protected operation without a session                                  |
| `forbidden`           | 403    | Anonymous request for a non-published status                           |
| `not_found`           | 404    | Unknown or hidden resource                                             |
| `method_not_allowed`  | 405    | Unsupported HTTP method                                                |
| `invalid_transition`  | 409    | Lifecycle transition not allowed                                       |
| `internal_error`      | 500    | Unhandled exception                                                    |

Example error:

```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more fields are invalid.",
    "fields": { "title": ["This field is required."] }
  }
}
```

With `DEBUG=True` (development settings), Django may render its technical HTML
pages for 404 and 500 responses instead of the JSON envelope. The JSON error
contract applies with `DEBUG=False`. See `ADR/005`.

## Resources

### Post

```json
{
  "id": 1,
  "slug": "hello-world",
  "title": "Hello World",
  "summary": "First post.",
  "content": "Hello from the API.",
  "category": "science",
  "status": "draft",
  "published_at": null,
  "deleted_at": null,
  "created_at": "2026-10-25T04:22:02.760630+00:00",
  "updated_at": "2026-10-25T04:22:02.760644+00:00"
}
```

- `category` is the category slug or `null`.
- `status` is `draft`, `published`, or `deleted`.
- `slug` is generated from the title when the post is created and is immutable.
- `published_at` is set on the first publish and is retained afterwards.
- `deleted_at` is set by soft deletion and cleared by restore.

### Category

```json
{
  "id": 1,
  "slug": "science",
  "name": "Science",
  "description": "Science posts",
  "created_at": "2026-10-25T04:22:02.752317+00:00",
  "updated_at": "2026-10-25T04:22:02.752328+00:00"
}
```

- `slug` is generated from the name when the category is created and is
  immutable.

### Pagination

```json
{ "page": 1, "page_size": 20, "total": 0, "total_pages": 1 }
```

`page_size` comes from `API_PAGE_SIZE` (default 20) and is not
client-configurable. Collections are ordered newest first by `created_at`, then
`id`, so pagination is deterministic.

## Endpoints

| Method | Path                      | Auth    | Success | Error statuses     |
| ------ | ------------------------- | ------- | ------- | ------------------ |
| POST   | `/auth/login`             | No      | 200     | 400, 401, 405      |
| POST   | `/auth/logout`            | Session | 204     | 401, 405           |
| GET    | `/posts`                  | No      | 200     | 400, 403, 405      |
| POST   | `/posts`                  | Session | 201     | 400, 401, 405      |
| GET    | `/posts/{slug}`           | No      | 200     | 404, 405           |
| PUT    | `/posts/{slug}`           | Session | 200     | 400, 401, 404, 405 |
| PATCH  | `/posts/{slug}`           | Session | 200     | 400, 401, 404, 405 |
| DELETE | `/posts/{slug}`           | Session | 200     | 401, 404, 405, 409 |
| POST   | `/posts/{slug}/publish`   | Session | 200     | 401, 404, 405, 409 |
| POST   | `/posts/{slug}/unpublish` | Session | 200     | 401, 404, 405, 409 |
| POST   | `/posts/{slug}/restore`   | Session | 200     | 401, 404, 405, 409 |
| GET    | `/categories`             | No      | 200     | 405                |
| POST   | `/categories`             | Session | 201     | 400, 401, 405      |
| GET    | `/categories/{slug}`      | No      | 200     | 404, 405           |
| PATCH  | `/categories/{slug}`      | Session | 200     | 400, 401, 404, 405 |
| DELETE | `/categories/{slug}`      | Session | 204     | 401, 404, 405      |

Unsupported methods return `405` and an `Allow` header.

## Posts

### `GET /posts`

Returns a paginated collection. Anonymous clients see published posts only.
Authenticated clients see every status unless they filter.

Query parameters:

| Parameter  | Behavior                                                                                                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `status`   | `draft`, `published`, or `deleted`. Invalid -> `400 validation_error`. Anonymous requesting `draft` or `deleted` -> `403 forbidden`. Omitted -> anonymous sees published; authenticated sees all. |
| `category` | Category slug. Unknown slug -> `200` with an empty `items` list. Applied after the status filter.                                                                                                  |
| `page`     | 1-based. Missing or non-integer -> page 1. Integer `< 1` or beyond the last page -> the last page. Empty collection -> page 1.                                                                    |

`page_size` is ignored. Ordering is newest first by `created_at`, then `id`.

### `POST /posts`

Requires a session. Request fields:

| Field      | Required | Rules                                                         |
| ---------- | -------- | ------------------------------------------------------------- |
| `title`    | Yes      | Non-empty string, maximum 255 characters, unique across posts |
| `summary`  | Yes      | Non-empty string, maximum 255 characters                      |
| `content`  | Yes      | Non-empty string                                              |
| `category` | No       | Existing category id, or `null`; omitted means `null`         |

`slug`, `status`, `published_at`, and `deleted_at` are generated or managed by
the server and are ignored if sent. New posts start as `draft` with
`published_at` and `deleted_at` set to `null`. Returns `201` with the post.

### `GET /posts/{slug}`

Returns a published post to anonymous clients. Authenticated clients can read
posts in any status. Draft and deleted posts return the same `404 not_found`
response as an unknown slug for anonymous clients.

### `PUT /posts/{slug}`

Requires a session. Replaces the mutable fields.

- `title`, `summary`, and `content` are required.
- `category` is optional; omitting it or sending `null` clears the category.
- Title uniqueness excludes the current post.
- `slug`, `status`, `published_at`, and `deleted_at` are ignored.
- Returns `200` with the updated post.

### `PATCH /posts/{slug}`

Requires a session. Updates only the fields present in the body: `title`,
`summary`, `content`, and `category`. Send `"category": null` to clear the
category. Immutable fields are ignored. Returns `200` with the updated post.

### `DELETE /posts/{slug}`

Requires a session. Performs a soft delete.

- Allowed from `draft` or `published`.
- Returns `200` with the post, now `status: "deleted"` and `deleted_at` set.
- Deleting an already deleted post returns `409 invalid_transition`.
- The row remains until the retention command purges it.

## Lifecycle

Allowed transitions:

| Current   | Target    | Operation                    |
| --------- | --------- | ---------------------------- |
| Draft     | Published | `POST /posts/{slug}/publish`   |
| Draft     | Deleted   | `DELETE /posts/{slug}`         |
| Published | Draft     | `POST /posts/{slug}/unpublish` |
| Published | Deleted   | `DELETE /posts/{slug}`         |
| Deleted   | Draft     | `POST /posts/{slug}/restore`   |

A disallowed transition returns `409 invalid_transition`. A deleted post must be
restored before it can be published again.

- `publish` sets `published_at` on the first publish.
- `unpublish` keeps `published_at`; republishing retains the first publication
  date.
- `restore` clears `deleted_at` and returns the post to `draft`.

All lifecycle endpoints require a session, take no request body, and return
`200` with the serialized post. See `ADR/001`.

## Categories

### `GET /categories`

Returns a paginated collection of all categories. Supports `page` with the same
behavior as the post list.

### `POST /categories`

Requires a session. Request fields:

| Field         | Required | Rules                                                            |
| ------------- | -------- | ---------------------------------------------------------------- |
| `name`        | Yes      | Non-empty string, maximum 64 characters, unique across categories |
| `description` | No       | String, maximum 255 characters; omitted or empty means `""`      |

Returns `201` with the category. The slug is generated from `name`.

### `GET /categories/{slug}`

Returns one category or `404 not_found`.

### `PATCH /categories/{slug}`

Requires a session. Updates only the provided `name` and/or `description`.
`slug` is immutable and ignored. Returns `200` with the category.

### `DELETE /categories/{slug}`

Requires a session. Permanently deletes the category and returns `204` with an
empty body. Posts that referenced it keep existing with `category: null`.

## Retention

Soft-deleted posts are purged only by the `purge_deleted_posts` management
command:

```bash
uv run --env-file .env manage.py purge_deleted_posts --dry-run
uv run --env-file .env manage.py purge_deleted_posts
```

- `POST_RETENTION_DAYS` defaults to 30 days.
- Only posts with `status=deleted` and `deleted_at` at or before the cutoff are
  removed. Draft and published posts are never purged.
- `--dry-run` lists the matching slugs and deletes nothing.
- A negative `POST_RETENTION_DAYS` makes the command fail.
- Permanent deletion is not exposed by the API. See `ADR/006`.

## Examples

The examples below were checked against a running instance. Start the server and
define the base URL:

```bash
export BASE=http://127.0.0.1:8000/api/v1
```

Log in and store the session cookie:

```bash
curl -sS -c cookies.txt -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"change-me"}' \
  "$BASE/auth/login"
```

```json
{ "id": 1, "username": "admin" }
```

Create a category:

```bash
curl -sS -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"name":"Science","description":"Science posts"}' \
  "$BASE/categories"
```

Create a draft post, using the category `id` from the previous response:

```bash
curl -sS -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"title":"Hello World","summary":"First post.","content":"Hello from the API.","category":1}' \
  "$BASE/posts"
```

Publish it:

```bash
curl -sS -b cookies.txt -X POST "$BASE/posts/hello-world/publish"
```

List published posts anonymously:

```bash
curl -sS "$BASE/posts?status=published"
```

Filter by category:

```bash
curl -sS "$BASE/posts?category=science"
```

Log out:

```bash
curl -sS -b cookies.txt -X POST "$BASE/auth/logout"
```
