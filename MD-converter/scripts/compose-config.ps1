# Validates the Docker Compose configuration without starting containers.
# Use this after changing infra/docker-compose.yml or Docker build settings.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

docker compose -f (Join-Path $repoRoot "infra/docker-compose.yml") config

