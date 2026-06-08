# MD Converter

Runnable monorepo scaffold for the PDF and PowerPoint to Markdown web app described in `pdf_pptx_to_markdown_web_app_spec.md`.

The first pass is deliberately a scaffold: health checks, typed API contracts, UI routes, Celery task names, Docker infrastructure, and tests are in place. Real object storage, database persistence, queue fan-out, and document conversion are left as explicit integrations.

## Layout

```text
apps/
  web/       Next.js 16 TypeScript frontend
  api/       FastAPI API service
  workers/   Celery worker service
packages/
  shared-types/
infra/       Docker Compose and service Dockerfiles
migrations/  Alembic migration scaffold
docs/        Architecture, runbook, and test corpus notes
```

## Local Setup

Copy the example environment file before running services:

```bash
cp .env.example .env
```

Install frontend dependencies:

```bash
npm install
```

Run the web app:

```bash
npm run dev:web
```

Run API tests:

```bash
uv --project apps/api run pytest
```

Run worker tests:

```bash
uv --project apps/workers run pytest
```

Validate local infrastructure:

```bash
docker compose -f infra/docker-compose.yml config
```

Start the local stack:

```bash
docker compose -f infra/docker-compose.yml up --build
```

## Scaffold Behavior

- `GET /health` returns a working health response.
- Upload and conversion creation endpoints return typed placeholder IDs and statuses.
- Cancel, retry, and download endpoints return explicit `501` responses until persistence, storage, and queueing are implemented.
- Worker task names are registered, but conversion functions are stubs.
