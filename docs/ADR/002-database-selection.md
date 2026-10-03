# ADR-002: Database Selection

## Status

Accepted

## Context

The application requires persistent relational storage for posts, categories,
and Django authentication data.

The primary purpose of this project is to explore the capabilities and limits of
Django's core framework when building a REST API without third-party REST
frameworks.

The project is exploratory and educational rather than a production system.
Therefore, minimizing infrastructure and operational complexity is more
important than optimizing for production scalability.

The database should:

- Be supported directly by Django.
- Require minimal configuration.
- Allow the project to run locally without additional services.
- Provide sufficient relational functionality for the application's scope.
- Avoid introducing infrastructure that is unrelated to the project's primary
  experiment.

## Decision

The project will use SQLite as its database.

SQLite will be accessed through Django ORM, and the application will avoid
database-specific functionality unless required by the project.

The database will be stored as a local file and will not be committed to source
control.

SQLite is sufficient for the expected dataset and usage of the application. It
also minimizes the infrastructure required to run the project, allowing the
experiment to focus on Django's core capabilities rather than database
configuration or administration.

## Consequences

### Positive

- No external database server is required.
- Minimal configuration and setup.
- Simple local development environment.
- Fully supported by Django.
- Easy to reset the database during development.
- Keeps the experiment focused on Django rather than infrastructure.
- The complete application can be run locally with minimal dependencies.

### Negative

- SQLite is not intended to represent the behavior of a production-scale
  database server.
- Concurrent write workloads are more limited than with server-based databases.
- Some database-specific behavior cannot be evaluated using SQLite.
- A future migration to another database could expose differences in database
  behavior or supported features.

## Alternatives Considered

### PostgreSQL

It was not selected because production scalability and database infrastructure
are outside the scope of this experiment.

### MySQL/MariaDB

MySQL/MariaDB would also provide a server-based relational database, but the
same reasoning applies: the additional infrastructure is unnecessary for the
scope and purpose of this project.
