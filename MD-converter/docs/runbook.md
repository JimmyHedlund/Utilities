# Runbook

## Local health checks

```bash
npm run stack:config
npm test
```

## Useful endpoints

- `GET /health`
- `POST /api/uploads`
- `POST /api/uploads/{file_id}/complete`
- `POST /api/conversions`
- `GET /api/conversions/{job_id}`
- `GET /api/conversions`

Cancel, retry, and download endpoints currently return explicit `501` responses until job persistence and queue integration exist.
Cancel and retry endpoints currently return explicit `501` responses until Phase 2 adds batch-aware state transitions. Download returns a Markdown URL after a job reaches `succeeded`.

## Local Phase 1 flow

1. Start the stack:

```bash
npm run stack:up
```

2. Open the web app at `http://127.0.0.1:3000`.
3. Upload a `.pdf` or `.pptx`.
4. Wait for the job detail page to show `succeeded`.
5. Use the download action to fetch the generated Phase 1 Markdown.
