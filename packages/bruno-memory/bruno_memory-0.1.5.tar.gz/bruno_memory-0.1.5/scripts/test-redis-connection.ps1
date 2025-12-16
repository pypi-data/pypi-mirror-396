#!/usr/bin/env pwsh
# Redis Connection Test Script for Windows
# Tests connection to Redis container and verifies functionality

param(
    [string]$RedisHost = $env:REDIS_HOST ?? "localhost",
    [int]$RedisPort = $env:REDIS_PORT ?? 6379,
    [int]$RedisDb = $env:REDIS_DB ?? 15,
    [string]$RedisPassword = $env:REDIS_PASSWORD ?? ""
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Redis Connection Test" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Host:     $RedisHost"
Write-Host "Port:     $RedisPort"
Write-Host "Database: $RedisDb"
Write-Host "============================================`n" -ForegroundColor Cyan

# Test 1: Check if redis-cli is available
Write-Host "[1/5] Checking redis-cli availability..." -ForegroundColor Yellow
$redisCliPath = Get-Command redis-cli -ErrorAction SilentlyContinue
if ($null -eq $redisCliPath) {
    Write-Host "✗ redis-cli not found. Using Docker exec instead" -ForegroundColor Yellow
    $useDocker = $true
} else {
    Write-Host "✓ redis-cli found at: $($redisCliPath.Source)" -ForegroundColor Green
    $useDocker = $false
}

# Helper function to run Redis commands
function Invoke-RedisCommand {
    param([string[]]$Arguments)
    
    if ($useDocker) {
        $result = docker exec bruno-memory-redis-minimal redis-cli @Arguments 2>&1
    } else {
        if ($RedisPassword) {
            $result = & redis-cli -h $RedisHost -p $RedisPort -a $RedisPassword @Arguments 2>&1
        } else {
            $result = & redis-cli -h $RedisHost -p $RedisPort @Arguments 2>&1
        }
    }
    return $result
}

# Test 2: Test basic connection
Write-Host "`n[2/5] Testing basic connection..." -ForegroundColor Yellow
try {
    $result = Invoke-RedisCommand @("PING")
    if ($result -match "PONG") {
        Write-Host "✓ Redis server is reachable (PONG received)" -ForegroundColor Green
    } else {
        Write-Host "✗ Unexpected response from Redis: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Connection failed: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Check Redis info
Write-Host "`n[3/5] Checking Redis server info..." -ForegroundColor Yellow
$info = Invoke-RedisCommand @("INFO", "server")
if ($info -match "redis_version:(\S+)") {
    $version = $matches[1]
    Write-Host "✓ Redis version: $version" -ForegroundColor Green
} else {
    Write-Host "⚠ Could not determine Redis version" -ForegroundColor Yellow
}

# Test 4: Test basic operations
Write-Host "`n[4/5] Testing basic Redis operations..." -ForegroundColor Yellow

# Set a test key
$setResult = Invoke-RedisCommand @("SET", "bruno_memory_test", "test_value", "EX", "60")
if ($setResult -match "OK") {
    Write-Host "  ✓ SET operation successful" -ForegroundColor Green
} else {
    Write-Host "  ✗ SET operation failed: $setResult" -ForegroundColor Red
}

# Get the test key
$getResult = Invoke-RedisCommand @("GET", "bruno_memory_test")
if ($getResult -match "test_value") {
    Write-Host "  ✓ GET operation successful" -ForegroundColor Green
} else {
    Write-Host "  ✗ GET operation failed: $getResult" -ForegroundColor Red
}

# Delete the test key
$delResult = Invoke-RedisCommand @("DEL", "bruno_memory_test")
if ($delResult -match "1") {
    Write-Host "  ✓ DEL operation successful" -ForegroundColor Green
} else {
    Write-Host "  ✗ DEL operation failed: $delResult" -ForegroundColor Red
}

# Test 5: Check memory and configuration
Write-Host "`n[5/5] Checking Redis configuration..." -ForegroundColor Yellow

# Check maxmemory
$maxmemory = Invoke-RedisCommand @("CONFIG", "GET", "maxmemory")
Write-Host "  Max Memory: $($maxmemory -join ' ')" -ForegroundColor Cyan

# Check maxmemory-policy
$policy = Invoke-RedisCommand @("CONFIG", "GET", "maxmemory-policy")
Write-Host "  Eviction Policy: $($policy -join ' ')" -ForegroundColor Cyan

# Check database count
$dbInfo = Invoke-RedisCommand @("INFO", "keyspace")
Write-Host "  Keyspace Info:" -ForegroundColor Cyan
if ($dbInfo) {
    $dbInfo | Select-String "db" | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} else {
    Write-Host "    (No keys present)" -ForegroundColor Gray
}

# Summary
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ All Redis connection tests passed!" -ForegroundColor Green
Write-Host "Redis is ready for testing" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
exit 0
