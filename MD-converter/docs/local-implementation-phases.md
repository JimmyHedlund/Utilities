# Local Implementation Phases

This document turns `pdf_pptx_to_markdown_web_app_spec.md` into local, buildable phases. Each phase should leave the repo in a working state with clear verification commands and commit-ready acceptance criteria.

Related docs:

- `docs/pdf_pptx_to_markdown_web_app_spec.md`
- `docs/architecture.md`
- `docs/runbook.md`
- `docs/test-corpus.md`

## Phase 0: Scaffold Baseline

Status: completed by the initial scaffold.

Goal: keep the repo bootable while the real implementation is added behind stable interfaces.

Implementation tasks:

- Maintain the monorepo layout: `apps/web`, `apps/api`, `apps/workers`, `packages/shared-types`, `infra`, `migrations`, and `docs`.
- Keep `GET /health` working in the FastAPI app.
- Keep upload and conversion routes typed, even while storage, database, and queue behavior are placeholder-backed.
- Keep Celery task names registered for preflight, split, convert, merge, cleanup, cancel, and retry.
- Keep Docker Compose validating with Postgres, Redis, MinIO, API, workers, and frontend services.

Local verification:

```bash
npm run typecheck
npm run build:web
uv --project apps/api --system-certs run pytest -c apps/api/pyproject.toml apps/api/tests
uv --project apps/workers --system-certs run pytest -c apps/workers/pyproject.toml apps/workers/tests
docker compose -f infra/docker-compose.yml config
```

Done when:

- The scaffold builds and tests locally.
- The web app loads at `http://localhost:3000`.
- The API health check responds at `http://localhost:8000/health`.
- Placeholder endpoints return explicit scaffold behavior rather than silent failures.

## Phase 1: MVP Upload And Small-File Conversion

Goal: support one complete local happy path for small PDF/PPTX files without batching.

Implementation tasks:

- Add S3-compatible storage service code for MinIO-backed upload and output buckets.
- Implement upload session creation, upload completion verification, content-type checks, size checks, and normalized storage keys.
- Add initial PostgreSQL models and Alembic migration for files, conversion jobs, conversion outputs, and job events.
- Wire `POST /api/conversions` to create a queued job and enqueue one worker task.
- Implement a small-file worker conversion path that downloads the original file, calls a stubbed converter adapter, writes final Markdown to object storage, and updates job status.
- Update the frontend upload page to call real upload and conversion endpoints, then navigate to the job detail page.
- Keep real converter dependencies optional in this phase; a deterministic text fixture converter is acceptable for local flow validation.

Local verification:

```bash
docker compose -f infra/docker-compose.yml up --build
uv --project apps/api --system-certs run pytest -c apps/api/pyproject.toml apps/api/tests
uv --project apps/workers --system-certs run pytest -c apps/workers/pyproject.toml apps/workers/tests
npm run typecheck
```

Done when:

- A local file can be uploaded to MinIO.
- A conversion job is created in Postgres.
- A worker produces a final `.md` object in output storage.
- The job detail page shows progress and final success.
- The download endpoint returns a signed or local development URL for the final Markdown.

## Phase 2: Persistence, Preflight, Batching, And Retry

Status: implemented with deterministic preflight and batch conversion.

Goal: make large-document processing reliable by using persisted job state, preflight inspection, batch records, Celery fan-out, deterministic merge, and retry.

Implementation tasks:

- Complete database tables from the spec: files, conversion jobs, conversion batches, conversion outputs, and job events.
- Implement repository/service layers for job state transitions and batch state transitions.
- Add preflight logic for MIME sniffing, PDF page counts, PPTX slide counts, basic encrypted/corrupt-file detection, and route selection metadata.
- Split PDFs by page ranges and PPTX files by slide ranges using configurable batch sizes.
- Enqueue batch conversion tasks with payloads containing only IDs.
- Implement merge task behavior that sorts by `batch_index`, joins Markdown, rewrites asset paths, adds YAML front matter, and writes final output.
- Implement retry for failed batches and job-level retry when safe.
- Update frontend job detail polling to show batch counts, current stage, errors, cancel, retry, and download states.
- Add output folder for the markdown file in the ui.

Local verification:

```bash
docker compose -f infra/docker-compose.yml up --build
uv --project apps/api --system-certs run pytest -c apps/api/pyproject.toml apps/api/tests
uv --project apps/workers --system-certs run pytest -c apps/workers/pyproject.toml apps/workers/tests
npm run typecheck
```

Manual scenarios:

- Convert a small PDF as one batch.
- Convert a larger PDF split into multiple batches.
- Force one batch failure, retry it, and confirm final merge order is stable.
- Cancel a queued or running job and confirm terminal state is persisted.

Done when:

- Postgres is the source of truth for all job, batch, and output state.
- Workers can crash or restart without losing visible job state.
- Batch outputs merge in deterministic order.
- Failed batches can be retried without reprocessing successful batches.
- The UI accurately reflects queued, preflighting, splitting, running, merging, succeeded, failed, cancelling, cancelled, and retrying states.

## Phase 3: Converter Quality, OCR, Fallbacks, And Assets

Goal: replace scaffold conversion with real local converter routing for PDFs and PowerPoint files.

Implementation tasks:

- Add converter adapters for Docling, PyMuPDF4LLM, MarkItDown, and LibreOffice utility conversion.
- Route clean digital PDFs to PyMuPDF4LLM where licensing and deployment constraints allow.
- Route default PDF/PPTX conversion through Docling.
- Use MarkItDown as a simple fallback for PDFs/PPTX where high fidelity is not required.
- Add OCR route configuration using Tesseract as the baseline local OCR engine.
- Extract images and table assets into batch-specific prefixes, then merge them into final `assets/` output.
- Preserve page and slide separators using the Markdown output contract in the specification.
- Add clear structured errors for unsupported, encrypted, corrupt, oversized, timed-out, and partially converted files.
- Expand the test corpus in `docs/test-corpus.md` with local fixture naming and expected outcomes.

Local verification:

```bash
docker compose -f infra/docker-compose.yml up --build
uv --project apps/api --system-certs run pytest -c apps/api/pyproject.toml apps/api/tests
uv --project apps/workers --system-certs run pytest -c apps/workers/pyproject.toml apps/workers/tests
npm run typecheck
```

Manual scenarios:

- Simple text PDF.
- Multi-column PDF.
- PDF with tables.
- Scanned PDF requiring OCR.
- Simple PPTX.
- PPTX with charts or screenshots.
- Corrupt PDF.
- Password-protected PDF.
- Unsupported file renamed as `.pdf`.

Done when:

- Real converter routes produce useful Markdown locally.
- OCR-heavy documents run through low-concurrency OCR processing.
- Extracted assets use safe relative paths in final Markdown.
- Fallback routes produce either a successful result or a clear user-facing error.
- The test corpus has documented expected behavior for each fixture type.

## Phase 4: Hardening, Observability, Cleanup, And Load Testing

Goal: make the local stack behave like a production-shaped system under failure, load, and untrusted file input.

Implementation tasks:

- Enforce MVP limits for file size, PDF pages, PPTX slides, batch runtime, full job runtime, retries, extracted image count, and output size.
- Add worker timeouts, memory-aware queue routing, smaller-batch retry behavior, and cleanup of temporary files.
- Add safe filename normalization, path traversal protection, content sniffing, and stricter validation around extracted assets.
- Add structured application logs for uploads, job transitions, batch transitions, retries, and merge completion.
- Add metrics hooks for job counts, durations, retries, queue depth, upload size, output size, CPU, and memory where locally practical.
- Add cleanup/retention task behavior for temporary files and old job artifacts.
- Add load-test scripts or documented commands for concurrent small, medium, OCR-heavy, and large-batch jobs.
- Update `docs/runbook.md` with operational commands for local debugging.

Local verification:

```bash
docker compose -f infra/docker-compose.yml up --build
docker compose -f infra/docker-compose.yml logs
uv --project apps/api --system-certs run pytest -c apps/api/pyproject.toml apps/api/tests
uv --project apps/workers --system-certs run pytest -c apps/workers/pyproject.toml apps/workers/tests
npm run typecheck
```

Manual scenarios:

- Worker crash during conversion.
- Redis restart while jobs are queued.
- Postgres restart while idle.
- Object storage transient failure.
- Many polling clients on one running job.
- OCR-heavy files running at constrained concurrency.

Done when:

- Limits are enforced before expensive conversion work begins.
- Failures produce structured logs, persisted errors, and actionable UI messages.
- Cleanup tasks remove temporary artifacts without deleting final outputs before retention.
- Load scenarios do not block API health checks or status polling.

## Phase 5: Production Deployment Preparation

Goal: prepare the local implementation for managed infrastructure without changing core application behavior.

Implementation tasks:

- Review environment variable names and defaults against `.env.example`.
- Separate local-only settings from production-required settings.
- Add deployment notes for frontend hosting, API hosting, worker hosting, managed Postgres, managed Redis/RabbitMQ, and S3-compatible object storage.
- Add least-privilege storage credential guidance for uploads, outputs, and worker access.
- Add migration and rollback instructions for database schema changes.
- Add monitoring guidance for Sentry, OpenTelemetry, Prometheus/Grafana, and Celery queue visibility.
- Document production readiness gaps that remain, such as auth, billing, tenant isolation, virus scanning, and external cloud fallback privacy review.

Local verification:

```bash
docker compose -f infra/docker-compose.yml config
npm run typecheck
uv --project apps/api --system-certs run pytest -c apps/api/pyproject.toml apps/api/tests
uv --project apps/workers --system-certs run pytest -c apps/workers/pyproject.toml apps/workers/tests
```

Done when:

- The app can still run locally with Docker Compose.
- Production environment requirements are documented.
- Secrets and deployment-specific settings are not hard-coded.
- Operators have a clear checklist for migrating from local services to managed services.

## Commit Rhythm

Use small, phase-aligned commits:

- One commit for schema or interface changes.
- One commit for API behavior.
- One commit for worker behavior.
- One commit for frontend workflow.
- One commit for tests and docs when they are substantial.

Each phase should end with a commit that passes the local verification commands listed for that phase.
