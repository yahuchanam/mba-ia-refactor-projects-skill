# Python — operations

Modern Python web backends (Flask, FastAPI, Django, Starlette, Sanic).

## Detect
`requirements.txt`, `pyproject.toml`, `Pipfile`, `*.py`. Declared manager:
`uv.lock` → uv · `poetry.lock` → poetry · `Pipfile.lock` → pipenv · plain `requirements.txt` → pip.

## Dependencies & install — prefer `uv`
- Create env: `uv venv`
- Install: `uv pip install -r requirements.txt` · or `uv sync` (with `pyproject.toml`/`uv.lock`)
- uv reads `requirements.txt` and PEP 621 `pyproject.toml`, so it works even if the project used
  pip or poetry.
- Fallback (no uv): `python -m venv .venv` then `python -m pip install -r requirements.txt`.
- Run tools as `uv run <tool>` / `python -m <tool>` — never `.venv/bin/<tool>`.

## Run / stop environment
- Flask: `uv run flask --app app run` or `uv run python app.py`
- FastAPI/Starlette: `uv run uvicorn main:app`
- Django: `uv run python manage.py runserver`
- **Config via env** set **inside** the script (`os.environ.setdefault(...)`), not as a CLI prefix.
- Prefer in-process verification (below) so there's no server to stop.

## Tests (when needed)
`uv run pytest` · `uv run python -m unittest` · Django `uv run python manage.py test`.

## Lint · format · types
- Lint: `uv run ruff check .` (or `uv run flake8`)
- Format: `uv run ruff format .` (or `uv run black .`)
- Types: `uv run mypy .`  (no build step for plain Python)

## Verify the route surface in-process
- Flask → `app.test_client()`
- FastAPI/Starlette → `from starlette.testclient import TestClient; TestClient(app)`
- Django → `django.test.Client()`

`verify_routes.py` imports the app, sets env internally, hits every Phase 1 route, asserts, and
exits non-zero on failure. Run as ONE command: `uv run python verify_routes.py`.
