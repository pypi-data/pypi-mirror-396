#!/usr/bin/env pwsh
# Teardown test environment - stops and optionally removes Docker services

param(
    [ValidateSet("minimal", "full", "ci", "all")]
    [string]$Profile = "full",
    [switch]$Volumes,
    [switch]$Force
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Bruno-Memory Test Environment Teardown" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Profile: $Profile"
Write-Host "Remove volumes: $Volumes"
Write-Host "============================================`n" -ForegroundColor Cyan

# Determine compose files to stop
$composeFiles = @()
if ($Profile -eq "all") {
    $composeFiles = @("docker-compose.yml", "docker-compose.minimal.yml", "docker-compose.ci.yml")
    Write-Host "[1/2] Stopping all compose configurations..." -ForegroundColor Yellow
} else {
    $composeFile = switch ($Profile) {
        "minimal" { "docker-compose.minimal.yml" }
        "ci" { "docker-compose.ci.yml" }
        default { "docker-compose.yml" }
    }
    $composeFiles = @($composeFile)
    Write-Host "[1/2] Stopping $composeFile..." -ForegroundColor Yellow
}

# Build docker-compose command
$downArgs = @()
if ($Volumes) {
    $downArgs += "-v"
}

# Stop each compose configuration
$success = $true
foreach ($file in $composeFiles) {
    if (Test-Path $file) {
        Write-Host "  Stopping services from $file..." -ForegroundColor Gray
        
        $result = docker-compose -f $file down @downArgs 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ⚠ Warning: Some issues stopping $file" -ForegroundColor Yellow
            if (-not $Force) {
                $success = $false
            }
        } else {
            Write-Host "  ✓ Stopped $file" -ForegroundColor Green
        }
    } else {
        Write-Host "  ⚠ File not found: $file" -ForegroundColor Yellow
    }
}

# Show remaining containers
Write-Host "`n[2/2] Checking for remaining bruno-memory containers..." -ForegroundColor Yellow
$remainingContainers = docker ps -a --filter "name=bruno-memory" --format "{{.Names}}"

if ($remainingContainers) {
    Write-Host "  ⚠ Some containers still exist:" -ForegroundColor Yellow
    $remainingContainers | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }
    
    if ($Force) {
        Write-Host "`n  Force removing containers..." -ForegroundColor Yellow
        $remainingContainers | ForEach-Object {
            docker rm -f $_ 2>&1 | Out-Null
        }
        Write-Host "  ✓ Containers removed" -ForegroundColor Green
    }
} else {
    Write-Host "  ✓ No bruno-memory containers remaining" -ForegroundColor Green
}

# Show remaining volumes if not removed
if (-not $Volumes) {
    Write-Host "`n[Info] Checking for bruno-memory volumes..." -ForegroundColor Cyan
    $volumes = docker volume ls --filter "name=bruno-memory" --format "{{.Name}}"
    
    if ($volumes) {
        Write-Host "  Data volumes still exist (use -Volumes to remove):" -ForegroundColor Yellow
        $volumes | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }
    }
}

# Summary
Write-Host "`n============================================" -ForegroundColor Cyan
if ($success) {
    Write-Host "✓ Test environment teardown complete!" -ForegroundColor Green
    if ($Volumes) {
        Write-Host "  All data has been removed" -ForegroundColor Yellow
    } else {
        Write-Host "  Data volumes preserved (use -Volumes to remove)" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠ Teardown completed with warnings" -ForegroundColor Yellow
    Write-Host "  Use -Force to remove containers forcefully" -ForegroundColor Cyan
}
Write-Host "============================================" -ForegroundColor Cyan
exit 0
