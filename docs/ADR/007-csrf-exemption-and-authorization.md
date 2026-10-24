## Status

Accepted

## Context

The API uses Django session-cookie authentication. Every API view is decorated
with `csrf_exempt`, so `CsrfViewMiddleware` does not validate a CSRF token on
state-changing requests.

Writes are protected by `login_required_json`, which accepts any authenticated
user. The project has no registration flow; accounts are provisioned as
administrators through `createsuperuser` or the Django admin.

A decision is required on the CSRF exemption and on whether write access needs
an additional `is_staff` check.

## Decision

- Keep `csrf_exempt` on the API views.
- Treat the CSRF risk as accepted for `v1` because three conditions hold
  together:
  - Write requests must use `Content-Type: application/json`, enforced by
    `parse_json` (`NFR-004`). An HTML form cannot send that content type.
  - A cross-origin `fetch` with `application/json` triggers a CORS preflight.
    The project configures no CORS headers, so the browser does not send the
    request.
  - `SESSION_COOKIE_SAMESITE` is not overridden and keeps Django's default of
    `Lax`, so a cross-site request does not carry the session cookie.
- Grant write access to any authenticated user. Only administrator accounts
  exist, so a separate `is_staff` check adds no security boundary in `v1`.
- Keep `/admin/` under Django's normal CSRF protection.

Unsafe endpoints and their guards:

| Method | Path                      | Guard                       |
| ------ | ------------------------- | --------------------------- |
| POST   | `/auth/login`             | Public by design            |
| POST   | `/auth/logout`            | Explicit `is_authenticated` |
| POST   | `/posts`                  | `login_required_json`       |
| PUT    | `/posts/{slug}`           | `login_required_json`       |
| PATCH  | `/posts/{slug}`           | `login_required_json`       |
| DELETE | `/posts/{slug}`           | `login_required_json`       |
| POST   | `/posts/{slug}/publish`   | `login_required_json`       |
| POST   | `/posts/{slug}/unpublish` | `login_required_json`       |
| POST   | `/posts/{slug}/restore`   | `login_required_json`       |
| POST   | `/categories`             | `login_required_json`       |
| PATCH  | `/categories/{slug}`      | `login_required_json`       |
| DELETE | `/categories/{slug}`      | `login_required_json`       |

This decision must be revisited before any of these changes:

- Enabling CORS or adding a cross-origin browser client;
- Setting `SESSION_COOKIE_SAMESITE` to `None` or `"None"`;
- Accepting form-encoded or `text/plain` write requests;
- Exposing registration or non-administrator accounts.

## Consequences

### Positive

- No token bootstrap endpoint, token header, or client change is required.
- The API stays usable from non-browser clients such as `curl` and the end to
  end suite.
- Authentication and authorization rules remain in one helper,
  `login_required_json`.

### Negative

- CSRF protection depends on configuration that is not itself enforced by a
  test: JSON-only content type, no CORS, and `SameSite=Lax`.
- Any authenticated account can write. This is safe only while account creation
  stays administrator-controlled.
- The exemption is invisible to API clients unless they read this `ADR`.

## Alternatives Considered

### Add a CSRF Token Bootstrap Endpoint

Rejected for `v1` because it adds a new endpoint, requires clients to fetch a
cookie and send `X-CSRFToken`, and changes every documented `curl` example. The
current content-type and cookie policy already blocks the browser CSRF paths.

### Enforce CSRF Except on Login and Logout

Rejected because it still leaves login and logout unprotected and requires the
same client changes as full enforcement.

### Enforce `is_staff` on Every Write

Rejected because the application provisions only administrator accounts. It
would require fixture and end to end changes without closing a reachable gap.
