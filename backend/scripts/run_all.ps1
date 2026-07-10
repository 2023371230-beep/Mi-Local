param(
    [int]$BackendPort = 8000,
    [int]$VanePort = 3000,
    [int]$SearxngPort = 4000
)

$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

docker info | Out-Null
Invoke-RestMethod "http://localhost:11434/api/tags" -TimeoutSec 10 | Out-Null

& "..\perplexica\scripts\run_vane.ps1" -Port $VanePort -SearxngPort $SearxngPort

$listener = Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    Write-Host "Backend already listening on port $BackendPort."
    exit 0
}

Start-Process -FilePath ".\.venv\Scripts\python.exe" `
    -ArgumentList "-m","uvicorn","app.presentation.main:app","--host","127.0.0.1","--port","$BackendPort" `
    -WorkingDirectory (Get-Location) `
    -WindowStyle Hidden

Start-Sleep -Seconds 5
Invoke-RestMethod "http://127.0.0.1:$BackendPort/health" -TimeoutSec 20 | ConvertTo-Json -Depth 10
