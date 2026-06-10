# Starts the Next.js development server on http://localhost:3000.
# Runs through the web workspace so app-specific Next.js settings are used.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

npm --prefix $repoRoot --workspace "@md-converter/web" run dev
