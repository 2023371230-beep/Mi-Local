param(
    [switch]$Kill,
    [switch]$SuggestAlt
)

$connections = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $connections) {
    Write-Host "Port 8000 is free."
    exit 0
}

$pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pidValue in $pids) {
    $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
    Write-Host "Port 8000 is used by PID $pidValue ($($process.ProcessName))"
}

if ($Kill) {
    foreach ($pidValue in $pids) {
        Stop-Process -Id $pidValue -Force
        Write-Host "Stopped PID $pidValue"
    }
}
elseif ($SuggestAlt) {
    Write-Host "Start backend on 8010 with: .\scripts\run_backend.ps1 -Port 8010"
}
else {
    Write-Host "Use -Kill to stop the listener, or -SuggestAlt to keep it and use port 8010."
}
