param(
    [string]$Url = "http://localhost:3000"
)

$ErrorActionPreference = "Stop"

docker ps --filter "name=^/vane$" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

try {
    $providers = Invoke-RestMethod "$Url/api/providers" -TimeoutSec 10
    $providers | ConvertTo-Json -Depth 10
}
catch {
    Write-Error "Vane providers endpoint failed at $Url/api/providers: $($_.Exception.Message)"
}
