param(
    [int]$BackendPort = 8000,
    [switch]$StopVane
)

$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

.\scripts\stop_backend.ps1 -Port $BackendPort

if ($StopVane) {
    & "..\perplexica\scripts\stop_vane.ps1"
}
else {
    Write-Host "Vane left running. Use -StopVane to stop it too."
}
