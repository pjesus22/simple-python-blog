# Roadmap

Architecture decisions are indexed in [`docs/ADR/README.md`](ADR/README.md).

## Phase 1 - Project Foundation

- [x] Initialize the project with `uv`.
- [x] Configure Django.
- [x] Configure environment-specific settings.
- [x] Configure the database.
- [x] Create the initial Django application structure.
- [x] Establish the testing setup.
- [x] Define the initial data models.

## Phase 2 - Core Domain

- [x] Implement the Post model.
- [x] Implement the Category model.
- [x] Implement post lifecycle states.
- [x] Implement slug generation.
- [x] Implement database migrations.
- [x] Add model-level validation and tests.

## Phase 3 - Authentication and Authorization

- [x] Configure Django authentication.
- [x] Implement administrator login.
- [x] Implement logout.

## Phase 4 - REST API

- [x] Implement JSON request parsing and validation.
- [x] Implement post CRUD operations.
- [x] Implement category management.
- [x] Enforce authentication on protected (write) operations.
- [x] Implement and test unauthorized access responses.
- [x] Implement public post listing.
- [x] Implement post detail endpoints.
- [x] Implement category filtering.
- [x] Implement pagination.
- [x] Implement consistent error responses.

## Phase 5 - Post Lifecycle and Retention

- [x] Implement explicit post state transitions.
- [x] Implement soft deletion.
- [x] Implement administrator post visibility across all statuses.
- [x] Implement permanent deletion after the retention period.
- [x] Add automated tests for all lifecycle transitions.

## Phase 6 - Hardening and Documentation

- [x] Review API behavior and HTTP status codes.
- [x] Review authentication and authorization.
- [x] Review ORM queries for inefficient access patterns.
- [x] Add or improve automated tests.
- [x] Document the API.
- [x] Update the README.
- [x] Review and finalize ADRs.
- [x] Verify that the project satisfies the acceptance criteria.

## `v1` Verification

Verified 2026-10-26.

- `pytest --cov` passes with coverage above the 80% gate.
- `Ruff`, `basedpyright`, and `pre-commit` pass.
- A clean checkout completes `uv sync`, migration, administrator creation,
  `runserver`, the README API examples, and the purge dry-run.
- Every acceptance criterion in `docs/PROJECT.md` maps to the endpoint,
  lifecycle, query-count, or e2e suites; none is deferred.
- No secrets are tracked and no third-party REST framework is installed.

`v1` scope complete. That is the whole record. Tests provide the detail; the
roadmap provides the date and command result.
