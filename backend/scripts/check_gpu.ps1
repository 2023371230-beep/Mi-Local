# Watchdog de GPU para Ollama.
#
# Problema real (auditoria 2026-07-10): tras suspender/arrancar la laptop, la deteccion
# CUDA de Ollama a veces falla y cae a CPU EN SILENCIO (7 tok/s vs 98 tok/s en la RTX 3060).
# Este script genera 1 token, lee size_vram de /api/ps y si es 0 reinicia Ollama.
#
# Uso:  .\scripts\check_gpu.ps1            (solo diagnostica)
#       .\scripts\check_gpu.ps1 -Fix       (reinicia Ollama si esta en CPU)

param(
    [switch]$Fix,
    [string]$Model = "llama3.2:latest"
)

$ErrorActionPreference = "Stop"

function Test-OllamaGpu {
    param([string]$ModelName)
    $body = @{ model = $ModelName; prompt = "ok"; stream = $false; options = @{ num_predict = 1 } } | ConvertTo-Json
    Invoke-RestMethod "http://localhost:11434/api/generate" -Method Post -Body $body -TimeoutSec 300 | Out-Null
    $ps = Invoke-RestMethod "http://localhost:11434/api/ps" -TimeoutSec 10
    $loaded = $ps.models | Where-Object { $_.name -eq $ModelName } | Select-Object -First 1
    if ($null -eq $loaded) { return $null }
    return [long]$loaded.size_vram
}

$vram = Test-OllamaGpu -ModelName $Model
if ($null -eq $vram) {
    Write-Host "AVISO: no se pudo verificar el modelo $Model" -ForegroundColor Yellow
    exit 1
}

if ($vram -gt 0) {
    $gb = [math]::Round($vram / 1GB, 2)
    Write-Host "OK: Ollama esta usando la GPU ($Model con $gb GB en VRAM)" -ForegroundColor Green
    exit 0
}

Write-Host "PROBLEMA: Ollama esta corriendo en CPU (size_vram=0). Esto es 4-14x mas lento." -ForegroundColor Red
if (-not $Fix) {
    Write-Host "Corre:  .\scripts\check_gpu.ps1 -Fix   para reiniciar Ollama y reintentar."
    exit 2
}

Write-Host "Reiniciando Ollama..."
Stop-Process -Name 'ollama app' -Force -Confirm:$false -ErrorAction SilentlyContinue
Stop-Process -Name ollama -Force -Confirm:$false -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Start-Process -FilePath "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
Start-Sleep -Seconds 10

$vram = Test-OllamaGpu -ModelName $Model
if ($vram -gt 0) {
    $gb = [math]::Round($vram / 1GB, 2)
    Write-Host "OK: GPU recuperada ($gb GB en VRAM)" -ForegroundColor Green
    exit 0
}
Write-Host "SIGUE EN CPU tras reiniciar. Revisar: nvidia-smi ; driver NVIDIA ; %LOCALAPPDATA%\Ollama\server.log" -ForegroundColor Red
exit 2
