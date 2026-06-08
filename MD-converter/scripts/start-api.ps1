# Starts the FastAPI development server on http://127.0.0.1:8000.
# Uses uv with system TLS certificates because this local environment needs them for dependency resolution.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiPath = Join-Path $repoRoot "apps/api"

uv --project $apiPath --system-certs run uvicorn app.main:app --host 127.0.0.1 --port 8000

