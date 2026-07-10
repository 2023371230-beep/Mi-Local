param(
    [string]$Name = "vane"
)

$existing = docker ps -a --filter "name=^/$Name$" --format "{{.Names}}"
if ($existing -ne $Name) {
    Write-Host "Vane container '$Name' does not exist."
    exit 0
}

docker stop $Name
