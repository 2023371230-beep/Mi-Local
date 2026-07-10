param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    $pids = ($existing | Select-Object -ExpandProperty OwningProcess -Unique) -join ", "
    Write-Error "Port $Port is already in use by PID(s): $pids. Run scripts\check_ports.ps1 or use -Port 8010."
}

$args = @("-m", "uvicorn", "app.presentation.main:app", "--host", $HostAddress, "--port", "$Port")
if (-not $NoReload) {
    $args += "--reload"
}

.\.venv\Scripts\python.exe @args
