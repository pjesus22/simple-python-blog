# Simple Python Blog

A small REST API for a personal blog, built with Django and the Python standard
library only. It is an exploratory project that tests how far Django's core
HTTP, JSON, authentication, and ORM features can go without a third-party REST
framework such as Django REST Framework.

## Scope

Version 1 provides:

- Session-based login and logout for administrator accounts.
- Post CRUD with a generated slug and a `draft` / `published` / `deleted`
  lifecycle.
- Soft deletion with restore and a retention-based purge command.
- Public read access to published posts and categories.
- Category filtering and pagination for public post listings.
- JSON error responses with consistent status codes.

Public registration, comments, multiple authors, and permanent deletion through
the API are out of scope. See [`docs/PROJECT.md`](docs/PROJECT.md) for the full
specification and acceptance criteria.

## Documentation

- [Project specification](docs/PROJECT.md)
- [API reference](docs/API.md)
- [Roadmap](docs/ROADMAP.md)
- [Architecture decision records](docs/ADR/README.md)

## Requirements

- Python 3.14.6 (see `.python-version`)
- [uv](https://docs.astral.sh/uv/)
- SQLite, which is bundled with Python; no database server is required

## Setup

Install the dependencies:

```bash
uv sync
```

Create the local environment file and generate a secret key:

```bash
cp .env.example .env
uv run python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Put the generated value in `SECRET_KEY` in `.env`. For local development, keep:

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1
```

Load `.env` with `uv run --env-file .env` for every management command. The
development settings require `SECRET_KEY`; they do not read `.env` on their own.

### Environment variables

| Variable                 | Required            | Default                              | Purpose                                      |
| ------------------------ | ------------------- | ------------------------------------ | -------------------------------------------- |
| `DJANGO_SETTINGS_MODULE` | Yes                 | `config.settings.development`        | Selects development, production, or test     |
| `SECRET_KEY`             | Yes (dev and prod)  | Test-only fallback in test settings  | Django secret key                            |
| `ALLOWED_HOSTS`          | Yes (production)    | `localhost,127.0.0.1` in development | Comma-separated host names                   |
| `DATABASE_PATH`          | No                  | `db.sqlite3` in the project root     | SQLite file location                         |
| `LOG_LEVEL`              | No                  | `DEBUG` in development, `INFO` in production | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `POST_RETENTION_DAYS`    | No                  | `30`                                 | Days a soft-deleted post is kept             |
| `API_PAGE_SIZE`          | No                  | `20`                                 | Collection page size                         |

`.env` is ignored by Git. `.env.example` contains no real secrets.

### Database and administrator

Apply the migrations:

```bash
uv run --env-file .env manage.py migrate
```

Create the administrator account:

```bash
uv run --env-file .env manage.py createsuperuser
```

Start the development server:

```bash
uv run --env-file .env manage.py runserver
```

The API is served under `http://127.0.0.1:8000/api/v1/`. The Django admin is at
`http://127.0.0.1:8000/admin/`.

## API Quick Start

Log in and keep the session cookie:

```bash
export BASE=http://127.0.0.1:8000/api/v1

curl -sS -c cookies.txt -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"change-me"}' \
  "$BASE/auth/login"
```

Create a category and a draft post:

```bash
curl -sS -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"name":"Science","description":"Science posts"}' \
  "$BASE/categories"

curl -sS -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"title":"Hello World","summary":"First post.","content":"Hello from the API.","category":1}' \
  "$BASE/posts"
```

Publish the post and read the public listing:

```bash
curl -sS -b cookies.txt -X POST "$BASE/posts/hello-world/publish"
curl -sS "$BASE/posts?status=published"
```

See [`docs/API.md`](docs/API.md) for every endpoint, payload, status code, and
lifecycle rule.

## Tests and Quality Checks

Run the test suite:

```bash
uv run pytest
```

Run it with coverage:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

The coverage gate is `fail_under = 80`, configured in `pyproject.toml`. The suite
includes unit, contract, query-count, and end-to-end tests.

Run the linters and type checker:

```bash
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
```

Run the pre-commit hooks:

```bash
uv run pre-commit run --all-files
```

## Retention

Posts are soft-deleted through `DELETE /api/v1/posts/{slug}`. The maintenance
command permanently removes posts that have been deleted for at least
`POST_RETENTION_DAYS`:

```bash
uv run --env-file .env manage.py purge_deleted_posts --dry-run
uv run --env-file .env manage.py purge_deleted_posts
```

`--dry-run` prints the slugs that would be removed and changes nothing. The
command does not run automatically; schedule it externally and review the
dry-run output before a real run. Draft and published posts are never purged.

## Production

Select the production settings and provide the required environment variables:

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<long random value>
ALLOWED_HOSTS=example.com,www.example.com
DATABASE_PATH=/var/lib/simple-python-blog/db.sqlite3
LOG_LEVEL=INFO
```

Then apply migrations and collect static files:

```bash
uv run --env-file .env manage.py migrate --noinput
uv run --env-file .env manage.py collectstatic --noinput
```

Serve the `config.wsgi:application` WSGI application with a production WSGI
server. `manage.py runserver` is for development only. Production settings set
`DEBUG=False`, emit JSON logs, and require `SECRET_KEY` and `ALLOWED_HOSTS`.
