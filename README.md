# lgu2-www-django

Front-end website for [legislation.gov.uk](https://www.legislation.gov.uk) v2 — a
Django app that consumes the legislation REST API (a separate Spring Boot service)
and renders UK legislation for the browser.

## Requirements

- Python 3.12+
- Poetry
- Access to the legislation REST API, configured via `API_BASE_URL`

## Getting started

```bash
poetry install                 # creates ./.venv and installs deps (incl. dev tools)
cp .env.example .env           # then edit values as needed
./.venv/bin/python manage.py runserver
```

The app serves on http://127.0.0.1:8000/. The committed `poetry.toml` keeps the
virtualenv at `./.venv`; use it directly (`./.venv/bin/…`) for local commands.

## Dependencies

Manage dependencies with Poetry (`poetry add`, `poetry remove`, `poetry lock`), which
updates `pyproject.toml` and `poetry.lock`. Don't edit `requirements.txt` by hand — it's
generated from the lockfile.

## Formatting & linting

Code is formatted with **black** and linted with **flake8**. The shared checks are
defined in `.pre-commit-config.yaml` and run in CI on every pull request, which
fails if the code is unformatted or has lint errors.

Run the same checks locally:

```bash
./.venv/bin/pre-commit run --all-files
```

Optionally, install the git hook so they run automatically on each commit. This is
convenience only — not required, since CI is the enforcement:

```bash
./.venv/bin/pre-commit install
```

## Testing

```bash
./.venv/bin/python manage.py test
```
