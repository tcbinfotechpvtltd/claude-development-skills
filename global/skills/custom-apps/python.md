# Python services and scripts

## Setup
- **Python version**: inside Frappe or Odoo, use the version the framework requires. Standalone services default to 3.14 (3.15 once every dependency supports it); 3.11 is the oldest version still getting security fixes (until 2027-10).
- **Project files**: one `pyproject.toml`, a virtual environment per project, and dependencies pinned in a committed lock file. `pip-audit` before adding or upgrading.
- **Layout**: a `src/<package>/` layout; entry points declared in `pyproject.toml`; settings read from environment variables in one module (Twelve-Factor).
- **Format and lint**: `ruff format` and `ruff check` ([coding-standards.md](../eng-review/coding-standards.md)). Type hints on public functions; run a type checker where the repo has one.

## Code
- Business rules in plain functions and classes, independent of the web framework and the database; adapters for every vendor.
- Every outbound call has a timeout and TLS verification on. Retries are bounded, with backoff, and only for idempotent calls.
- `subprocess` with argument lists only, never `shell=True` with input. No `eval`, `exec`, `pickle` or `yaml.load` on untrusted data (use `yaml.safe_load`). Parameterised SQL only.
- Money is `Decimal`, never `float`; time zones are explicit (store UTC, show IST).
- Logging uses the `logging` module with structured context; never print secrets or full personal data.

## Scripts and jobs
- Scripts that change data take `--dry-run` and run in dry-run mode first. They are idempotent, log what they changed, and run in batches with progress output.
- Scheduled jobs: a lock against overlapping runs, an alert on failure, and an owner.

## Deploy shape
A WSGI or ASGI server (gunicorn or uvicorn workers) under systemd or in a container, behind nginx with TLS. Health endpoint, structured logs and error tracking before production (skill `eng-ship`).

Sources (checked 2026-11-04): python.org/downloads (release status), peps.python.org/pep-0008, docs.astral.sh/ruff, 12factor.net.
