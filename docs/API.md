# API

- Base path: `/api/v1/`.
- Authentication: Django session cookie. `POST /auth/login` sets it;
  `POST /auth/logout` clears it.
- Write and lifecycle operations require a session.

## Response Format

- Single resource: object, no wrapper.
- Collection: `{"items": [...], "pagination": {...}}`.
- Error: `{"error": {"code": "...", "message": "..."}}`.
- Validation errors add `error.fields`.

See `ADR-003`.

## Status Codes

| Status | Use                                                                         |
| ------ | --------------------------------------------------------------------------- |
| 200    | Read, update, lifecycle transition, soft delete                             |
| 201    | Post or category created                                                    |
| 204    | Logout, category deleted; empty body                                        |
| 400    | Invalid JSON, missing credentials, validation failure, invalid status query |
| 401    | Authentication required or bad credentials                                  |
| 403    | Anonymous request for non-published status                                  |
| 404    | Unknown slug, hidden post, unmatched `/api/` route                          |
| 405    | Method unsupported; response includes `Allow`                               |
| 409    | Disallowed lifecycle transition                                             |
| 500    | Unhandled server error                                                      |

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

## Endpoint Contract

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

## Post List Query Parameters

| Parameter  | Behavior                                                                                                                                                                                        |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `status`   | `draft`, `published`, or `deleted`. Invalid -> 400. Anonymous requesting non-published -> 403. Authenticated -> filter any status. Omitted -> anonymous sees published; authenticated sees all. |
| `category` | Category slug. Unknown slug -> 200 with empty `items`. Applies after status filtering.                                                                                                          |
| `page`     | 1-based. Missing or non-integer -> page 1. Integer `< 1` or beyond last -> last page. Empty collection -> page 1.                                                                               |

`page_size` is fixed at 20 and is not client-configurable.

Pagination metadata:

```json
{ "page": 1, "page_size": 20, "total": 0, "total_pages": 1 }
```

## Behavior Notes

- DELETE `/posts/{slug}` is a soft delete. It returns 200 with the post body,
  status: `deleted`, and `deleted_at` set. It is not 204.
- Anonymous requests for draft or deleted posts return 404, identical to an
  unknown slug, so post existence is not disclosed.
- POST `/posts/{slug}/publish` on a deleted post returns 409. Restore first.
- Category deletion is permanent. Posts keep existing with category: null.
- Unsupported methods return 405 and an `Allow` header.
