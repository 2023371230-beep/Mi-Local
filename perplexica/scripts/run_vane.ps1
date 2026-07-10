param(
    [int]$Port = 3000,
    [int]$SearxngPort = 4000,
    [string]$Name = "vane",
    [string]$Image = "itzcrazykns1337/vane:latest"
)

$ErrorActionPreference = "Stop"

docker info | Out-Null

$existing = docker ps -a --filter "name=^/$Name$" --format "{{.Names}}"
if ($existing -eq $Name) {
    $running = docker ps --filter "name=^/$Name$" --filter "status=running" --format "{{.Names}}"
    if ($running -eq $Name) {
        Write-Host "Vane container '$Name' is already running."
        exit 0
    }
    Write-Host "Starting existing Vane container '$Name'."
    docker start $Name | Out-Null
    exit 0
}

$portInUse = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($portInUse) {
    $pids = ($portInUse | Select-Object -ExpandProperty OwningProcess -Unique) -join ", "
    Write-Error "Port $Port is already in use by PID(s): $pids. Re-run with -Port 3001."
}

$searxngPortInUse = Get-NetTCPConnection -LocalPort $SearxngPort -State Listen -ErrorAction SilentlyContinue
if ($searxngPortInUse) {
    $pids = ($searxngPortInUse | Select-Object -ExpandProperty OwningProcess -Unique) -join ", "
    Write-Error "Port $SearxngPort is already in use by PID(s): $pids. Re-run with -SearxngPort 4001."
}

docker pull $Image
docker run -d -p "${Port}:3000" -p "${SearxngPort}:8080" -v vane-data:/home/vane/data --name $Name $Image
