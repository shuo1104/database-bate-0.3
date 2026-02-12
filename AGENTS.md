# Repo Agent Guide

This repository contains:
- `backend_fastapi/`: FastAPI + SQLAlchemy (async) + PostgreSQL backend.
- `frontend_vue3/`: Vue 3 + TypeScript + Vite frontend.
- `database/`: small Python package (psycopg2 utilities).
- `backend_fastapi/app/agent/`: Agent system (LangChain + Deepseek + MinerU) docs/plans.

Editor rules: no `.cursorrules`/`.cursor/rules/`; no `.github/copilot-instructions.md`.

## Commands

### Backend (FastAPI)
Install deps:
```bash
cd backend_fastapi
python -m venv env
pip install -r requirements.txt
```

Configure env:
- Shared env is loaded from repo root `.env` (if present).
- Backend env is loaded from `backend_fastapi/env/.env.{env}` (for `ENVIRONMENT=dev|prod|test`).
- Example: `backend_fastapi/env/.env.dev`.

Run server (preferred; uses Typer wrapper):
```bash
cd backend_fastapi
python main.py run --env=dev
```

Initialize DB tables:
```bash
cd backend_fastapi
python scripts/create_tables.py
```

Smoke test:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

Lint/format (Python):
- No pinned linter/formatter config in this repo.

Tests (Python):
- No test runner is currently wired (no `pytest` config/dependency found). If you add it:
```bash
cd backend_fastapi
pytest path/to/test_file.py::test_name
pytest -k "keyword" -q
```

### Frontend (Vue 3)
Install deps and run dev server:
```bash
cd frontend_vue3
pnpm install
pnpm dev
```

Build / preview:
```bash
cd frontend_vue3
pnpm build
pnpm preview
```

Type-check:
```bash
cd frontend_vue3
pnpm type-check
```

Lint:
- `package.json` defines `lint`, but ESLint is not pinned in `devDependencies`.
- If `pnpm lint` fails due to missing eslint, do not guess plugins; ask or pin them explicitly.

### `database/` (aux)

- `database/` currently contains a minimal Python package scaffold and is not used by the FastAPI app.
- Prefer making backend changes in `backend_fastapi/` unless you intentionally split shared DB utilities.

## Backend Code Style (FastAPI)

### Architecture and file placement
- Follow the module layering documented in `backend_fastapi/README.md`:
  - `model.py`: SQLAlchemy ORM models
  - `schema.py`: Pydantic request/response models
  - `crud.py`: DB queries only (no HTTP, minimal business logic)
  - `service.py`: business logic + transaction boundaries
  - `controller.py`: FastAPI routes; thin orchestration
- Register routes through `backend_fastapi/app/api/v1/__init__.py`.
- App initialization is centralized in `backend_fastapi/app/plugin/init_app.py`.

### Imports
- Group imports in this order, separated by blank lines:
  1) stdlib
  2) third-party
  3) local `app.*`
- Prefer explicit imports over `import *`.

### Typing and Pydantic
- Use type hints on public functions and service/crud entrypoints.
- Pydantic is v2; use `model_validate(...)` and `model_dump(mode="json")`.
- Request schemas use snake_case; response schemas often mirror DB column names via `alias=`.
- If adding new response models, keep the aliasing strategy consistent with existing modules.
- ORM models map to existing DB columns (often `ProjectID`/`TypeName` style); do not rename DB columns in code unless you are also migrating the database.

### Database and transactions
- Use `AsyncSession` injected via `Depends(get_db)` (`app.core.database.get_db`).
- CRUD functions should NOT call `commit()`; they should return objects/results.
- Service functions own transaction boundaries:
  - `await db.commit()` on success
  - `await db.rollback()` on handled failures
  - `await db.refresh(obj)` when returning newly created/updated ORM objects

### Error handling
- Prefer raising `app.core.custom_exceptions.BaseAPIException` subclasses from services.
- Let global handlers in `app.core.exceptions.register_exception_handlers` shape responses.
- Do not leak sensitive internals in error messages returned to clients.
- When catching broad exceptions in services:
  - always `await db.rollback()`
  - log with `exc_info=True` for unexpected errors
  - raise a safe `DatabaseException`/`ExternalServiceException` with a generic message

### Responses
- Use `SuccessResponse` / `ErrorResponse` from `app.common.response` for consistent JSON shape.
- Avoid returning raw ORM objects; convert via Pydantic models or `model_dump(mode="json")`.

### Logging
- Use `app.core.logger.logger`.
- Prefer structured context via `extra={...}` for request/path identifiers where practical.

## Frontend Code Style (Vue 3 + TS)
- TypeScript is `strict` (`frontend_vue3/tsconfig.json`): do not silence type errors.
- Prefer Composition API; put reusable logic in `src/composables/useX.ts`.
- API wrappers live in `src/api/*.ts`; keep them small and typed.
- Use `@/` alias for imports (configured in `vite.config.ts` and `tsconfig.json`).
- Prefer `type` imports for types in TS where it improves clarity.

## Agent System Notes
- Agent work belongs under `backend_fastapi/app/agent/`.
- Planning docs live in `backend_fastapi/app/agent/doc/`.
- Keep the Agent integration consistent with existing backend patterns (Controller/Service, JWT auth, logging, async tasks).
