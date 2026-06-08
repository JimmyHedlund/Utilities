# Architecture

This scaffold follows the specification's service split:

- Next.js frontend for upload, job history, progress, settings, and downloads.
- FastAPI API for upload sessions, conversion job orchestration, status, and signed result URLs.
- Celery workers for preflight, splitting, batch conversion, merging, cleanup, cancellation, and retry.
- PostgreSQL as the source of truth.
- Redis as the MVP broker.
- S3-compatible object storage for originals, intermediate batch outputs, final Markdown, and assets.

The current implementation is intentionally shallow. It preserves public interfaces and task names while leaving persistence, queueing, storage, and converter calls for the next milestone.

