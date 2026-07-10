$ports = @(8000, 8010, 3000, 3001, 11434)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        $connections |
            Select-Object LocalAddress, LocalPort, State, OwningProcess |
            Format-Table -AutoSize
    }
    else {
        Write-Host "Port ${port}: free"
    }
}
