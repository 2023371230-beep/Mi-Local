param(
    [string]$Name = "vane",
    [int]$Tail = 100
)

docker logs $Name --tail $Tail
