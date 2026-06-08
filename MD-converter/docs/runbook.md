# Runbook

## Local health checks

```bash
docker compose -f infra/docker-compose.yml config
uv --project apps/api run pytest
uv --project apps/workers run pytest
npm run typecheck
```

## Useful endpoints

- `GET /health`
- `POST /api/uploads`
- `POST /api/uploads/{file_id}/complete`
- `POST /api/conversions`
- `GET /api/conversions/{job_id}`
- `GET /api/conversions`

Cancel, retry, and download endpoints currently return explicit `501` responses until job persistence and queue integration exist.

