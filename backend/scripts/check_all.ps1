param(
    [int]$BackendPort = 8000
)

$ErrorActionPreference = "Continue"
Set-Location "$PSScriptRoot\.."

Write-Host "== Ports =="
.\scripts\check_ports.ps1

Write-Host "== Docker =="
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

Write-Host "== Ollama =="
Invoke-RestMethod "http://localhost:11434/api/tags" -TimeoutSec 10 | ConvertTo-Json -Depth 4

Write-Host "== Ollama GPU (critico: en CPU todo es 4-14x mas lento) =="
.\scripts\check_gpu.ps1

Write-Host "== Backend health =="
Invoke-RestMethod "http://127.0.0.1:$BackendPort/health" -TimeoutSec 20 | ConvertTo-Json -Depth 10

Write-Host "== Vane providers =="
Invoke-RestMethod "http://localhost:3000/api/providers" -TimeoutSec 20 | ConvertTo-Json -Depth 8

Write-Host "== Web search =="
$body = @{ query = "What is OWASP Top 10?"; sources = @("web"); optimization_mode = "speed"; top_k = 2 } | ConvertTo-Json
Invoke-RestMethod "http://127.0.0.1:$BackendPort/web/search" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 180 | ConvertTo-Json -Depth 8

Write-Host "== Logs =="
Invoke-RestMethod "http://127.0.0.1:$BackendPort/logs?lines=5" -TimeoutSec 20 | ConvertTo-Json -Depth 4
