#!/usr/bin/env pwsh
# Wait for Docker services to be ready
# Tests each service's health and readiness before proceeding

param(
    [string[]]$Services = @("postgresql", "redis", "chromadb", "qdrant"),
    [int]$TimeoutSeconds = 120,
    [int]$CheckInterval = 2
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Waiting for Docker Services" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Services to check: $($Services -join ', ')"
Write-Host "Timeout: $TimeoutSeconds seconds"
Write-Host "============================================`n" -ForegroundColor Cyan

$startTime = Get-Date
$allReady = $false

# Service check configurations
$serviceChecks = @{
    postgresql = @{
        containers = @("bruno-memory-postgres", "bruno-memory-postgres-minimal")
        check = {
            param($container)
            try {
                $result = docker exec $container pg_isready -U postgres 2>&1
                return $result -match "accepting connections"
            } catch {
                return $false
            }
        }
        port = 5432
    }
    redis = @{
        containers = @("bruno-memory-redis", "bruno-memory-redis-minimal")
        check = {
            param($container)
            try {
                $result = docker exec $container redis-cli ping 2>&1
                return $result -match "PONG"
            } catch {
                return $false
            }
        }
        port = 6379
    }
    chromadb = @{
        container = "bruno-memory-chromadb"
        check = {
            try {
                $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v2/heartbeat" -Method Get -TimeoutSec 5 -ErrorAction Stop
                return $true
            } catch {
                return $false
            }
        }
        port = 8000
    }
    qdrant = @{
        container = "bruno-memory-qdrant"
        check = {
            try {
                $response = Invoke-RestMethod -Uri "http://localhost:6333/healthz" -Method Get -TimeoutSec 5 -ErrorAction Stop
                return $true
            } catch {
                return $false
            }
        }
        port = 6333
    }
}

# Check if containers are running
Write-Host "[1/3] Checking if containers are running..." -ForegroundColor Yellow
$allContainersRunning = $true
$runningContainers = @{}

foreach ($service in $Services) {
    $config = $serviceChecks[$service]
    $containerNames = $config.containers
    
    $foundContainer = $null
    foreach ($containerName in $containerNames) {
        $running = docker ps --filter "name=$containerName" --format "{{.Names}}" 2>$null
        if ($running) {
            $foundContainer = $running
            break
        }
    }
    
    if ($foundContainer) {
        Write-Host "  ✓ $service container is running ($foundContainer)" -ForegroundColor Green
        $runningContainers[$service] = $foundContainer
    } else {
        Write-Host "  ✗ $service container is not running" -ForegroundColor Red
        $allContainersRunning = $false
    }
}

if (-not $allContainersRunning) {
    Write-Host "`n✗ Some containers are not running. Please start them first." -ForegroundColor Red
    Write-Host "  Run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Wait for services to be ready
Write-Host "`n[2/3] Waiting for services to be ready..." -ForegroundColor Yellow
$readyServices = @{}

while (-not $allReady) {
    $elapsed = (Get-Date) - $startTime
    
    if ($elapsed.TotalSeconds -gt $TimeoutSeconds) {
        Write-Host "`n✗ Timeout waiting for services to be ready" -ForegroundColor Red
        Write-Host "  Not ready: $($Services | Where-Object { -not $readyServices[$_] } | ForEach-Object { $_ })" -ForegroundColor Yellow
        exit 1
    }
    
    $allReady = $true
    foreach ($service in $Services) {
        if (-not $readyServices[$service]) {
            $config = $serviceChecks[$service]
            $container = $runningContainers[$service]
            $isReady = & $config.check $container
            
            if ($isReady) {
                $readyServices[$service] = $true
                Write-Host "  ✓ $service is ready (port $($config.port))" -ForegroundColor Green
            } else {
                $allReady = $false
            }
        }
    }
    
    if (-not $allReady) {
        Start-Sleep -Seconds $CheckInterval
    }
}

# Final verification
Write-Host "`n[3/3] Final verification..." -ForegroundColor Yellow
$allHealthy = $true
foreach ($service in $Services) {
    $config = $serviceChecks[$service]
    $container = $runningContainers[$service]
    $isReady = & $config.check $container
    
    if ($isReady) {
        Write-Host "  ✓ $service verified" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $service verification failed" -ForegroundColor Red
        $allHealthy = $false
    }
}

if ($allHealthy) {
    $elapsed = (Get-Date) - $startTime
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "✓ All services are ready!" -ForegroundColor Green
    Write-Host "Time elapsed: $([math]::Round($elapsed.TotalSeconds, 1)) seconds" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "`n✗ Some services failed final verification" -ForegroundColor Red
    exit 1
}
