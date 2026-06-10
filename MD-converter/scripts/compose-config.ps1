# Validates the Docker Compose configuration without starting containers.
# Use this after changing infra/docker-compose.yml or Docker build settings.
# This only needs the Docker CLI + Compose plugin; the container engine does not
# need to be running for config validation.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra/docker-compose.yml"

$previousErrorActionPreference = $ErrorActionPreference
$hadNativeErrorPreference = Test-Path Variable:\PSNativeCommandUseErrorActionPreference
if ($hadNativeErrorPreference) {
  $previousNativeErrorPreference = $PSNativeCommandUseErrorActionPreference
}

try {
  $ErrorActionPreference = "Continue"
  if ($hadNativeErrorPreference) {
    $PSNativeCommandUseErrorActionPreference = $false
  }

  & docker compose version 1>$null 2>$null
  $composeVersionExitCode = $LASTEXITCODE
} finally {
  $ErrorActionPreference = $previousErrorActionPreference
  if ($hadNativeErrorPreference) {
    $PSNativeCommandUseErrorActionPreference = $previousNativeErrorPreference
  }
}

if ($composeVersionExitCode -ne 0) {
  Write-Host ""
  Write-Host "Docker Compose is not available in this PowerShell session." -ForegroundColor Red
  Write-Host ""
  Write-Host "With Rancher Desktop on Windows, check that:"
  Write-Host "1. The Docker CLI is on PATH."
  Write-Host "2. Rancher Desktop is configured for dockerd/Moby."
  Write-Host "3. The Docker Compose plugin is installed and visible to docker."
  Write-Host "4. This terminal was restarted after changing Rancher Desktop settings."
  Write-Host ""
  Write-Host "Useful checks:"
  Write-Host "docker --version"
  Write-Host "docker compose version"
  Write-Host ""
  exit 1
}

try {
  $ErrorActionPreference = "Continue"
  if ($hadNativeErrorPreference) {
    $PSNativeCommandUseErrorActionPreference = $false
  }

  docker compose -f $composeFile config
  $composeConfigExitCode = $LASTEXITCODE
} finally {
  $ErrorActionPreference = $previousErrorActionPreference
  if ($hadNativeErrorPreference) {
    $PSNativeCommandUseErrorActionPreference = $previousNativeErrorPreference
  }
}

if ($composeConfigExitCode -ne 0) {
  exit $composeConfigExitCode
}
