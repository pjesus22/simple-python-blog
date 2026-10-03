# ADR-003: JSON Response Format

## Status

Accepted

## Context

The API will be implemented using Django's core HTTP and JSON functionality
rather than Django REST Framework.

A consistent response format is required across endpoints so that API clients
can predict the structure of successful and failed requests.

The format should remain simple and should not reproduce abstractions that would
normally be provided by a REST framework without a clear reason.

## Decision

Successful responses will return JSON representations of the requested resources
directly, without an additional top-level `data` wrapper.

A single resource response will have the following general structure:

```json
{
  "id": 1,
  "title": "Example post"
}
```

Collection responses will contain the resources and pagination metadata:

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

Error responses will use a consistent top-level `error` object:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "The request is invalid."
  }
}
```

Validation errors may additionally include field-specific information:

```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more fields are invalid.",
    "fields": {
      "title": ["This field is required."]
    }
  }
}
```

HTTP status codes will communicate the general result of the operation, while
the JSON error code will provide an application-level description.

## Consequences

### Positive

- All endpoints expose predictable response structures.
- API clients do not need endpoint-specific error parsing rules.
- The format is simple enough to implement using Django's built-in
  `JsonResponse`.
- The format can be tested independently of the underlying Django views.

### Negative

- The response format must be maintained manually.
- Pagination and validation behavior require explicit implementation.
- Additional conventions may be necessary as the API grows.

## Alternatives Considered

### Return Django-generated responses without a common format

Rejected because different endpoints could produce inconsistent response
structures and error payloads.

### Wrap all successful responses in a `data` property

Not selected because the project does not currently need the additional
abstraction and the simpler representation is sufficient for the API's scope.

### Use a third-party REST framework

Out of scope for this project because evaluating how much of this behavior can
be implemented with Django core is one of the project's primary objectives.
