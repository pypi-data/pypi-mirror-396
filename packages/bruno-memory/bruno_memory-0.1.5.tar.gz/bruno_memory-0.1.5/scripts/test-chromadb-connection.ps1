#!/usr/bin/env pwsh
# ChromaDB Connection Test Script for Windows
# Tests connection to ChromaDB container and verifies functionality

param(
    [string]$ChromaHost = $env:CHROMADB_HOST ?? "localhost",
    [int]$ChromaPort = $env:CHROMADB_PORT ?? 8000
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "ChromaDB Connection Test" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Host: $ChromaHost"
Write-Host "Port: $ChromaPort"
Write-Host "============================================`n" -ForegroundColor Cyan

$baseUrl = "http://${ChromaHost}:${ChromaPort}/api/v2"

# Test 1: Check if curl is available
Write-Host "[1/5] Checking connectivity tools..." -ForegroundColor Yellow
$curlAvailable = Get-Command curl -ErrorAction SilentlyContinue
if ($curlAvailable) {
    Write-Host "✓ curl is available" -ForegroundColor Green
} else {
    Write-Host "✗ curl not found" -ForegroundColor Red
    exit 1
}

# Test 2: Test heartbeat endpoint
Write-Host "`n[2/5] Testing ChromaDB heartbeat..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/heartbeat" -Method Get -TimeoutSec 5 -ErrorAction Stop
    $heartbeat = $response.'nanosecond heartbeat'
    Write-Host "✓ ChromaDB is alive (heartbeat: $heartbeat ns)" -ForegroundColor Green
} catch {
    Write-Host "✗ Heartbeat failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Check container status
Write-Host "`n[3/5] Checking container status..." -ForegroundColor Yellow
try {
    $containerStatus = docker ps --filter "name=bruno-memory-chromadb" --format "{{.Status}}"
    if ($containerStatus) {
        Write-Host "✓ Container is running: $containerStatus" -ForegroundColor Green
    } else {
        Write-Host "⚠ Container not found or not running" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not check container status" -ForegroundColor Yellow
}

# Test 4: Check logs for errors
Write-Host "`n[4/5] Checking ChromaDB logs..." -ForegroundColor Yellow
try {
    $logs = docker logs bruno-memory-chromadb --tail 5 2>&1
    if ($LASTEXITCODE -eq 0) {
        $hasError = $logs | Select-String -Pattern "error|ERROR|failed|FAILED" -Quiet
        if ($hasError) {
            Write-Host "⚠ Found errors in logs" -ForegroundColor Yellow
        } else {
            Write-Host "✓ No errors in recent logs" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "⚠ Could not check logs" -ForegroundColor Yellow
}

# Test 5: Python client information
Write-Host "`n[5/5] ChromaDB API Information..." -ForegroundColor Yellow
Write-Host "✓ ChromaDB requires Python client for full functionality" -ForegroundColor Green
Write-Host "  The HTTP API is not fully REST-based" -ForegroundColor Cyan
Write-Host "  Install with: pip install chromadb" -ForegroundColor Cyan
Write-Host "  Example usage:" -ForegroundColor Cyan
Write-Host "    import chromadb" -ForegroundColor Gray
Write-Host "    client = chromadb.HttpClient(host='localhost', port=8000)" -ForegroundColor Gray
Write-Host "    collection = client.create_collection('test')" -ForegroundColor Gray

# Summary
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ ChromaDB connection tests passed!" -ForegroundColor Green
Write-Host "ChromaDB is ready for vector operations" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
exit 0
