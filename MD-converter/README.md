# PDF and PowerPoint to Markdown Converter

## What it Does
This project is a web app for converting PDF and PowerPoint files into Markdown files. The goal is to reduce token usage when adding files to AI agents and make document content easier to process.

## Features
Batchprocessing when the documents contains more then 10 pages.
What it can do. /ToDo

## How to run it
Setup and startup steps. /ToDo

## Current Local Status

Phase 2 is implemented for local development:

- Upload `.pdf` and `.pptx` files through presigned MinIO URLs.
- Persist files, conversion jobs, batches, outputs, and events in PostgreSQL.
- Queue Celery preflight, split, batch conversion, merge, retry, and cancel state transitions.
- Produce deterministic placeholder Markdown through the Phase 2 batch pipeline.
- Poll job status from the web app and download final Markdown after success.

Useful commands:

```bash
npm run stack:up
npm test
npm run build:web
```

If `npm run stack:up` says the container engine is not reachable on Windows, start Rancher Desktop and wait for its engine to finish starting. This repo uses `docker compose`, so Rancher Desktop should be configured for dockerd/Moby or your Docker CLI context should point at Rancher Desktop.

## Usage
How to use the app. /ToDo

## Tech stack
Frameworks and tools. /ToDo

## Notes
Anything important about limits, file types, or behavior. /ToDo
