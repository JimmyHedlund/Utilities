# Builds and starts the local Docker Compose stack.
# Checks that a Docker-compatible engine is reachable first, so Windows pipe/daemon errors are easier to understand.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra/docker-compose.yml"
$script:dockerContext = $null

function Test-DockerEngine {
  param([string]$ContextName)

  $dockerArgs = @()
  if ($ContextName) {
    $dockerArgs += @("--context", $ContextName)
  }
  $dockerArgs += "info"

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

    $output = & docker @dockerArgs 2>&1 | ForEach-Object { $_.ToString() }
    $exitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousErrorActionPreference
    if ($hadNativeErrorPreference) {
      $PSNativeCommandUseErrorActionPreference = $previousNativeErrorPreference
    }
  }

  return [pscustomobject]@{
    Ok = ($exitCode -eq 0)
    Context = $ContextName
    Output = ($output -join [Environment]::NewLine)
  }
}

function Invoke-Docker {
  param([Parameter(ValueFromRemainingArguments = $true)][string[]]$DockerArgs)

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

    if ($script:dockerContext) {
      & docker --context $script:dockerContext @DockerArgs
    } else {
      & docker @DockerArgs
    }

    $exitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousErrorActionPreference
    if ($hadNativeErrorPreference) {
      $PSNativeCommandUseErrorActionPreference = $previousNativeErrorPreference
    }
  }

  if ($exitCode -ne 0) {
    exit $exitCode
  }
}

$dockerCommand = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCommand) {
  Write-Host ""
  Write-Host "Docker CLI is not available in this PowerShell session." -ForegroundColor Red
  Write-Host ""
  Write-Host "With Rancher Desktop on Windows, restart PowerShell after enabling Docker CLI integration,"
  Write-Host "or add Rancher Desktop's docker.exe location to PATH."
  Write-Host ""
  exit 1
}

$activeContext = (& docker context show 2>$null)
$availableContexts = @(& docker context ls --format '{{.Name}}' 2>$null)
$engineCheck = Test-DockerEngine -ContextName $null

if (-not $engineCheck.Ok -and $availableContexts -contains "rancher-desktop") {
  $rancherCheck = Test-DockerEngine -ContextName "rancher-desktop"
  if ($rancherCheck.Ok) {
    $script:dockerContext = "rancher-desktop"
    $engineCheck = $rancherCheck
    Write-Host "Using Docker context: rancher-desktop"
  }
}

if (-not $engineCheck.Ok) {
  Write-Host ""
  Write-Host "Docker-compatible container engine is not reachable." -ForegroundColor Red
  Write-Host ""
  Write-Host "Docker CLI:" $dockerCommand.Source
  if ($activeContext) {
    Write-Host "Active Docker context:" $activeContext
  }
  if ($availableContexts.Count -gt 0) {
    Write-Host "Available Docker contexts:" ($availableContexts -join ", ")
  }
  $dockerEnvVars = @(Get-ChildItem Env:DOCKER* -ErrorAction SilentlyContinue)
  if ($dockerEnvVars.Count -gt 0) {
    Write-Host "Docker environment variables:"
    foreach ($item in $dockerEnvVars) {
      Write-Host ("  {0}={1}" -f $item.Name, $item.Value)
    }
  }
  Write-Host ""
  Write-Host "Rancher Desktop checks:"
  Write-Host "1. Container engine is dockerd/Moby."
  Write-Host "2. Rancher Desktop says the engine is running."
  Write-Host "3. Docker context is 'rancher-desktop' or another context that points at Rancher."
  Write-Host "4. No stale DOCKER_HOST environment variable points at Docker Desktop's pipe."
  Write-Host ""
  Write-Host "Useful commands:"
  Write-Host "docker context ls"
  Write-Host "docker context use rancher-desktop"
  Write-Host "docker info"
  Write-Host "Get-ChildItem Env:DOCKER*"
  Write-Host ""
  Write-Host "Original docker info output:"
  Write-Host $engineCheck.Output
  Write-Host ""
  exit 1
}

# Build images one at a time. Rancher Desktop/buildx can be flaky when several
# services build the same Dockerfile concurrently.
Invoke-Docker compose -f $composeFile build api
Invoke-Docker compose -f $composeFile build frontend
Invoke-Docker compose -f $composeFile build worker-preflight
Invoke-Docker compose -f $composeFile up
