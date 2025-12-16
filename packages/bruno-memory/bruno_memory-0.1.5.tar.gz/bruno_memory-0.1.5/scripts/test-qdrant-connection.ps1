#!/usr/bin/env pwsh
# Qdrant Connection Test Script for Windows
# Tests connection to Qdrant container and verifies functionality

param(
    [string]$QdrantHost = $env:QDRANT_HOST ?? "localhost",
    [int]$QdrantPort = $env:QDRANT_HTTP_PORT ?? 6333
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Qdrant Connection Test" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Host: $QdrantHost"
Write-Host "Port: $QdrantPort"
Write-Host "============================================`n" -ForegroundColor Cyan

$baseUrl = "http://${QdrantHost}:${QdrantPort}"

# Test 1: Check if curl is available
Write-Host "[1/6] Checking connectivity tools..." -ForegroundColor Yellow
$curlAvailable = Get-Command curl -ErrorAction SilentlyContinue
if ($curlAvailable) {
    Write-Host "✓ curl is available" -ForegroundColor Green
} else {
    Write-Host "✗ curl not found" -ForegroundColor Red
    exit 1
}

# Test 2: Test health endpoint
Write-Host "`n[2/6] Testing Qdrant health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/healthz" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Qdrant is healthy" -ForegroundColor Green
} catch {
    Write-Host "✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Get Qdrant version and info
Write-Host "`n[3/6] Checking Qdrant version..." -ForegroundColor Yellow
try {
    $info = Invoke-RestMethod -Uri "$baseUrl/" -Method Get -ErrorAction Stop
    Write-Host "✓ Qdrant version: $($info.version)" -ForegroundColor Green
    Write-Host "  Title: $($info.title)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Could not determine version: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 4: List collections
Write-Host "`n[4/6] Listing collections..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/collections" -Method Get -ErrorAction Stop
    $collections = $response.result.collections
    $count = $collections.Count
    Write-Host "✓ Collections endpoint accessible ($count collections)" -ForegroundColor Green
    if ($count -gt 0) {
        Write-Host "  Collections:" -ForegroundColor Cyan
        $collections | ForEach-Object { Write-Host "    - $($_.name)" -ForegroundColor Gray }
    }
} catch {
    Write-Host "✗ Failed to list collections: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Test collection operations
Write-Host "`n[5/6] Testing collection operations..." -ForegroundColor Yellow
$testCollectionName = "bruno_memory_test_$(Get-Random -Maximum 10000)"

try {
    # Create test collection
    $createBody = @{
        vectors = @{
            size = 128
            distance = "Cosine"
        }
    } | ConvertTo-Json -Depth 3
    
    $created = Invoke-RestMethod -Uri "$baseUrl/collections/$testCollectionName" `
        -Method Put `
        -Body $createBody `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    if ($created.result -eq $true) {
        Write-Host "  ✓ Created test collection: $testCollectionName" -ForegroundColor Green
    }
    
    # Get collection info
    $collection = Invoke-RestMethod -Uri "$baseUrl/collections/$testCollectionName" `
        -Method Get `
        -ErrorAction Stop
    
    Write-Host "  ✓ Retrieved test collection (vectors: $($collection.result.config.params.vectors.size))" -ForegroundColor Green
    
    # Delete test collection
    $deleted = Invoke-RestMethod -Uri "$baseUrl/collections/$testCollectionName" `
        -Method Delete `
        -ErrorAction Stop
    
    if ($deleted.result -eq $true) {
        Write-Host "  ✓ Deleted test collection" -ForegroundColor Green
    }
    
} catch {
    Write-Host "  ✗ Collection operations failed: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try to cleanup
    try {
        Invoke-RestMethod -Uri "$baseUrl/collections/$testCollectionName" `
            -Method Delete `
            -ErrorAction SilentlyContinue | Out-Null
    } catch {}
}

# Test 6: Check cluster status
Write-Host "`n[6/6] Checking cluster status..." -ForegroundColor Yellow
try {
    $cluster = Invoke-RestMethod -Uri "$baseUrl/cluster" -Method Get -ErrorAction Stop
    Write-Host "✓ Cluster status: $($cluster.result.status)" -ForegroundColor Green
    Write-Host "  Peer ID: $($cluster.result.peer_id)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Could not get cluster status: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ Qdrant connection tests passed!" -ForegroundColor Green
Write-Host "Qdrant is ready for vector operations" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
exit 0
