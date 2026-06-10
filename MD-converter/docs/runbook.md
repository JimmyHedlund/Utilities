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

Cancel and retry endpoints use persisted job and batch state. Download returns a Markdown URL after a job reaches `succeeded`.

## Local Phase 2 flow

1. Start the stack:

```bash
npm run stack:up
```

2. Open the web app at `http://localhost:3000`.
3. Upload a `.pdf` or `.pptx`.
4. Wait for the job detail page to show `succeeded`.
5. Use the download action to fetch the generated Phase 2 Markdown.
6. Use retry after a failed batch, or cancel while a job is queued, preflighting, splitting, running, or retrying.

## Docker troubleshooting

If Docker reports that `//./pipe/docker_engine` cannot be found, Rancher Desktop is not running, the engine has not finished starting, or the Docker CLI is not pointed at Rancher Desktop.

Fix:

1. Start Rancher Desktop.
2. Wait until Rancher Desktop reports that the engine is running.
3. Use dockerd/Moby in Rancher Desktop if you want `docker compose`.
4. Confirm your Docker CLI context points at Rancher Desktop.
5. Retry `npm run stack:up`.
6. If your local setup requires elevated access, run PowerShell as Administrator.

If `uv sync` fails inside Docker with `invalid peer certificate: UnknownIssuer`, the local Compose build passes explicit `uv` TLS flags for PyPI through `UV_TLS_ARGS`. For a stricter setup, install your organization or proxy CA certificate into the Rancher Desktop/WSL build environment and remove the `--allow-insecure-host` flags from `infra/docker-compose.yml`.

If the frontend image fails during `npm install` with npm's `Exit handler never called!` message, it can be the same TLS interception problem surfaced poorly by npm. The local Compose build sets `NPM_STRICT_SSL=false` for the frontend build. For a stricter setup, install your CA certificate into Rancher Desktop/WSL and set `NPM_STRICT_SSL` to `true` in `infra/docker-compose.yml`.
