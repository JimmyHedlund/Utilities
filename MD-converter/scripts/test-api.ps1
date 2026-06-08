# Runs the FastAPI test suite with the API pytest configuration.
# The explicit config and test path prevent pytest from collecting unrelated tests outside this repo.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiPath = Join-Path $repoRoot "apps/api"

uv --project $apiPath --system-certs run pytest -c (Join-Path $apiPath "pyproject.toml") (Join-Path $apiPath "tests")

