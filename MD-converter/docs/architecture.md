# Architecture

This scaffold follows the specification's service split:

- Next.js frontend for upload, job history, progress, settings, and downloads.
- FastAPI API for upload sessions, conversion job orchestration, status, and signed result URLs.
- Celery workers for preflight, splitting, batch conversion, merging, cleanup, cancellation, and retry.
- PostgreSQL as the source of truth.
- Redis as the MVP broker.
- S3-compatible object storage for originals, intermediate batch outputs, final Markdown, and assets.

The current implementation supports the Phase 2 local flow: presigned MinIO uploads, PostgreSQL-backed files/jobs/batches/outputs, Celery preflight and batch fan-out, deterministic batch conversion, merge into final Markdown, status polling, retry, cancellation, SSE status snapshots, and final Markdown download URLs.

Real document parsing, OCR, fallback converter routing, asset extraction, and production hardening remain later phases.
