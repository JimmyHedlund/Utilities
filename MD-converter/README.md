# PDF and PowerPoint to Markdown Converter

## What it Does
This project is a web app for converting PDF and PowerPoint files into Markdown files. The goal is to reduce token usage when adding files to AI agents and make document content easier to process.

## Features
Batchprocessing when the documents contains more then 10 pages.
What it can do. /ToDo

## How to run it
Setup and startup steps. /ToDo

## Current Local Status

Phase 1 is implemented for local development:

- Upload `.pdf` and `.pptx` files through presigned MinIO URLs.
- Persist files, conversion jobs, outputs, and events in PostgreSQL.
- Queue a Celery worker task for small-file conversion.
- Produce deterministic placeholder Markdown for the Phase 1 happy path.
- Poll job status from the web app and download final Markdown after success.

Useful commands:

```bash
npm run stack:up
npm test
npm run build:web
```

## Usage
How to use the app. /ToDo

## Tech stack
Frameworks and tools. /ToDo

## Notes
Anything important about limits, file types, or behavior. /ToDo
