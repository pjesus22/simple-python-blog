# ADR-005: Centralized Error Handling

## Status

Accepted

## Context

API routes live under `/api/v1/`. Errors must return the JSON envelope defined
in ADR-003 instead of Django's default HTML pages, while non-API routes (e.g.
`/admin/`) keep Django's HTML errors.

## Decision

Use Django's native root URLconf error handlers (`handler400`, `handler403`,
`handler404`, `handler500`) registered in `config/urls.py`.

- A small dispatcher in `config/errors.py` decides by `request.path_info`
  whether the response is API JSON (existing envelope from `blog.views.helpers`)
  or Django's default HTML handler.
- No custom middleware and no custom exception hierarchy are introduced.
- `Json404Mixin` is removed; detail views rely on `Http404` reaching
  `handler404`.

Scope is limited to errors Django dispatches to the 400/403/404/500 handlers. It
does not cover every response with those status codes, errors rejected before
URLconf dispatch, or CSRF failures. Django has no URLconf `handler405`, so
method not allowed responses are handled by the shared `ApiView` base class
instead (`blog/views/base.py`), which returns the same JSON envelope.

`DEBUG` behavior is exception-specific:

- `DEBUG=True` bypasses `handler404` and `handler500` (technical 404/traceback
  pages).
- `PermissionDenied` reaches `handler403` even with `DEBUG=True`.
- Malformed/suspicious-operation paths reach `handler400` under `DEBUG=False`;
  `DEBUG=True` may render a technical response instead.
- `DEBUG_PROPAGATE_EXCEPTIONS=True` re-raises uncaught exceptions on the 500
  path only; it does not bypass the 400/403/404 handlers.

## Consequences

- API error responses are uniform and JSON; non-API routes are unaffected.
- No new dependencies or framework layers.
- `DEBUG=True` responses are a development tradeoff, not a production API
  guarantee.
