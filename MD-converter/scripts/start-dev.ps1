# Starts the API and web development servers in separate PowerShell windows.
# Use this for local UI work when both services should run together.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  (Join-Path $PSScriptRoot "start-api.ps1")
) -WorkingDirectory $repoRoot

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  (Join-Path $PSScriptRoot "start-web.ps1")
) -WorkingDirectory $repoRoot

Write-Host "API starting at http://127.0.0.1:8000"
Write-Host "Web starting at http://127.0.0.1:3000"

