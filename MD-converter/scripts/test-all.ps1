# Runs the local scaffold verification suite.
# This checks API tests, worker tests, and frontend/shared TypeScript types.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

& (Join-Path $PSScriptRoot "test-api.ps1")
& (Join-Path $PSScriptRoot "test-workers.ps1")
npm --prefix $repoRoot run typecheck

