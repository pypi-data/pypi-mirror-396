#!/usr/bin/env pwsh
# Run tests with Docker services
# Manages Docker environment and executes pytest with proper configuration

param(
    [ValidateSet("minimal", "full", "ci")]
    [string]$Profile = "full",
    [string[]]$Markers = @(),
    [string]$TestPath = "tests/",
    [switch]$NoCoverage,
    [switch]$Verbose,
    [switch]$KeepEnv,
    [switch]$SetupOnly,
    [string[]]$PytestArgs = @()
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Bruno-Memory Docker Test Runner" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Profile: $Profile"
Write-Host "Test path: $TestPath"
if ($Markers.Count -gt 0) {
    Write-Host "Markers: $($Markers -join ', ')"
}
Write-Host "============================================`n" -ForegroundColor Cyan

# Step 1: Setup test environment
Write-Host "[1/4] Setting up test environment..." -ForegroundColor Yellow
$setupScript = Join-Path $PSScriptRoot "setup-test-env.ps1"
& $setupScript -Profile $Profile

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Failed to setup test environment" -ForegroundColor Red
    exit 1
}

if ($SetupOnly) {
    Write-Host "`n✓ Setup complete (SetupOnly mode)" -ForegroundColor Green
    exit 0
}

# Step 2: Verify services are ready
Write-Host "`n[2/4] Verifying services..." -ForegroundColor Yellow
$waitScript = Join-Path $PSScriptRoot "wait-for-services.ps1"
$servicesToWait = switch ($Profile) {
    "minimal" { @("postgresql", "redis") }
    default { @("postgresql", "redis", "chromadb", "qdrant") }
}
& $waitScript -Services $servicesToWait -TimeoutSeconds 60

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ Services not ready" -ForegroundColor Red
    exit 1
}

# Step 3: Build pytest command
Write-Host "`n[3/4] Running tests..." -ForegroundColor Yellow

$pytestCommand = @("pytest", $TestPath)

# Add markers
if ($Markers.Count -gt 0) {
    $markerExpression = $Markers -join " or "
    $pytestCommand += @("-m", $markerExpression)
}

# Add coverage
if (-not $NoCoverage) {
    $pytestCommand += @(
        "--cov=bruno_memory",
        "--cov-report=html",
        "--cov-report=term-missing"
    )
}

# Add verbosity
if ($Verbose) {
    $pytestCommand += "-vv"
} else {
    $pytestCommand += "-v"
}

# Add additional pytest args
if ($PytestArgs.Count -gt 0) {
    $pytestCommand += $PytestArgs
}

Write-Host "  Command: $($pytestCommand -join ' ')" -ForegroundColor Gray

# Run pytest
$testResult = $null
try {
    & $pytestCommand[0] $pytestCommand[1..($pytestCommand.Length - 1)]
    $testResult = $LASTEXITCODE
} catch {
    Write-Host "`n✗ Error running tests: $($_.Exception.Message)" -ForegroundColor Red
    $testResult = 1
}

# Step 4: Cleanup (if not keeping environment)
if (-not $KeepEnv) {
    Write-Host "`n[4/4] Cleaning up test environment..." -ForegroundColor Yellow
    $teardownScript = Join-Path $PSScriptRoot "teardown-test-env.ps1"
    & $teardownScript -Profile $Profile
} else {
    Write-Host "`n[4/4] Keeping test environment (use -KeepEnv to preserve)" -ForegroundColor Yellow
    Write-Host "  To cleanup manually: .\scripts\teardown-test-env.ps1" -ForegroundColor Gray
}

# Summary
Write-Host "`n============================================" -ForegroundColor Cyan
if ($testResult -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
}
Write-Host "============================================" -ForegroundColor Cyan

exit $testResult
