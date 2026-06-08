# Runs the Celery worker test suite with the worker pytest configuration.
# This currently verifies that the scaffold task names are registered.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$workersPath = Join-Path $repoRoot "apps/workers"

uv --project $workersPath --system-certs run pytest -c (Join-Path $workersPath "pyproject.toml") (Join-Path $workersPath "tests")

