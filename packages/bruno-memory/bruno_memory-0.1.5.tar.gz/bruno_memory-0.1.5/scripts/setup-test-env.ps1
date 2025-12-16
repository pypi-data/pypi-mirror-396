#!/usr/bin/env pwsh
# Setup test environment - starts Docker services and waits for readiness

param(
    [ValidateSet("minimal", "full", "ci")]
    [string]$Profile = "full",
    [switch]$Pull,
    [switch]$Build,
    [switch]$Clean
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Bruno-Memory Test Environment Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Profile: $Profile"
Write-Host "============================================`n" -ForegroundColor Cyan

# Determine compose file
$composeFile = switch ($Profile) {
    "minimal" { "docker-compose.minimal.yml" }
    "ci" { "docker-compose.ci.yml" }
    default { "docker-compose.yml" }
}

Write-Host "[1/5] Using compose file: $composeFile" -ForegroundColor Yellow

# Clean up if requested
if ($Clean) {
    Write-Host "`n[2/5] Cleaning up existing containers..." -ForegroundColor Yellow
    docker-compose -f $composeFile down -v 2>&1 | Out-Null
    Write-Host "  ✓ Cleaned up" -ForegroundColor Green
} else {
    Write-Host "`n[2/5] Skipping cleanup (use -Clean to remove existing containers)" -ForegroundColor Yellow
}

# Pull images if requested
if ($Pull) {
    Write-Host "`n[3/5] Pulling latest images..." -ForegroundColor Yellow
    docker-compose -f $composeFile pull
    Write-Host "  ✓ Images pulled" -ForegroundColor Green
} else {
    Write-Host "`n[3/5] Skipping image pull (use -Pull to update images)" -ForegroundColor Yellow
}

# Build custom images if requested
if ($Build) {
    Write-Host "`n[4/5] Building custom images..." -ForegroundColor Yellow
    docker-compose -f $composeFile build
    Write-Host "  ✓ Images built" -ForegroundColor Green
} else {
    Write-Host "`n[4/5] Skipping build (use -Build to rebuild images)" -ForegroundColor Yellow
}

# Start services
Write-Host "`n[5/5] Starting Docker services..." -ForegroundColor Yellow
$startResult = docker-compose -f $composeFile up -d 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to start services" -ForegroundColor Red
    Write-Host $startResult
    exit 1
}
Write-Host "  ✓ Services started" -ForegroundColor Green

# Determine which services to wait for based on profile
$servicesToWait = switch ($Profile) {
    "minimal" { @("postgresql", "redis") }
    default { @("postgresql", "redis", "chromadb", "qdrant") }
}

# Wait for services to be ready
Write-Host "`n[6/6] Waiting for services to be ready..." -ForegroundColor Yellow
$waitScript = Join-Path $PSScriptRoot "wait-for-services.ps1"
& $waitScript -Services $servicesToWait

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "✓ Test environment is ready!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "`nRunning containers:" -ForegroundColor Cyan
    docker ps --filter "name=bruno-memory" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    Write-Host "`nTo run tests: pytest tests/" -ForegroundColor Yellow
    Write-Host "To stop: docker-compose -f $composeFile down" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n✗ Failed to setup test environment" -ForegroundColor Red
    exit 1
}
