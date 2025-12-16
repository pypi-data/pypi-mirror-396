#!/usr/bin/env pwsh
# PostgreSQL Connection Test Script for Windows
# Tests connection to PostgreSQL container and verifies schema

param(
    [string]$PgHost = $env:POSTGRES_HOST ?? "localhost",
    [int]$PgPort = $env:POSTGRES_PORT ?? 5432,
    [string]$PgUser = $env:POSTGRES_USER ?? "postgres",
    [string]$PgPassword = $env:POSTGRES_PASSWORD ?? "testpass123",
    [string]$PgDatabase = $env:POSTGRES_DB ?? "bruno_memory_test"
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Connection Test" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Host:     $PgHost"
Write-Host "Port:     $PgPort"
Write-Host "Database: $PgDatabase"
Write-Host "User:     $PgUser"
Write-Host "============================================`n" -ForegroundColor Cyan

# Set environment variable for password
$env:PGPASSWORD = $PgPassword

# Test 1: Check if psql is available
Write-Host "[1/5] Checking psql availability..." -ForegroundColor Yellow
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if ($null -eq $psqlPath) {
    Write-Host "✗ psql not found. Install PostgreSQL client tools or use Docker exec" -ForegroundColor Red
    Write-Host "`nAlternative: Use Docker exec to test connection:" -ForegroundColor Yellow
    Write-Host "  docker exec bruno-memory-postgres psql -U $PgUser -d $PgDatabase -c '\l'" -ForegroundColor Gray
    exit 1
}
Write-Host "✓ psql found at: $($psqlPath.Source)" -ForegroundColor Green

# Test 2: Test basic connection
Write-Host "`n[2/5] Testing basic connection..." -ForegroundColor Yellow
try {
    $result = & psql -h $PgHost -p $PgPort -U $PgUser -d postgres -c '\q' 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL server is reachable" -ForegroundColor Green
    } else {
        Write-Host "✗ Cannot connect to PostgreSQL server" -ForegroundColor Red
        Write-Host "Error: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Connection failed: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Check database existence
Write-Host "`n[3/5] Checking database existence..." -ForegroundColor Yellow
$dbCheck = & psql -h $PgHost -p $PgPort -U $PgUser -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$PgDatabase'" 2>&1
if ($LASTEXITCODE -eq 0 -and $dbCheck -eq "1") {
    Write-Host "✓ Database '$PgDatabase' exists" -ForegroundColor Green
} else {
    Write-Host "✗ Database '$PgDatabase' not found" -ForegroundColor Red
    exit 1
}

# Test 4: Check extensions
Write-Host "`n[4/5] Checking required extensions..." -ForegroundColor Yellow
$extensions = & psql -h $PgHost -p $PgPort -U $PgUser -d $PgDatabase -tAc "SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector')" 2>&1
if ($LASTEXITCODE -eq 0) {
    if ($extensions -match "uuid-ossp") {
        Write-Host "✓ uuid-ossp extension is installed" -ForegroundColor Green
    } else {
        Write-Host "✗ uuid-ossp extension not found" -ForegroundColor Red
    }
    
    if ($extensions -match "vector") {
        Write-Host "✓ vector (pgvector) extension is installed" -ForegroundColor Green
    } else {
        Write-Host "⚠ vector (pgvector) extension not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ Failed to check extensions" -ForegroundColor Red
}

# Test 5: Check schema tables
Write-Host "`n[5/5] Checking schema tables..." -ForegroundColor Yellow
$tables = @(
    "messages",
    "memory_entries",
    "session_contexts",
    "user_contexts",
    "conversation_contexts",
    "schema_migrations"
)

$allTablesExist = $true
foreach ($table in $tables) {
    $tableCheck = & psql -h $PgHost -p $PgPort -U $PgUser -d $PgDatabase -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='$table'" 2>&1
    if ($LASTEXITCODE -eq 0 -and $tableCheck -eq "1") {
        Write-Host "  ✓ Table '$table' exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Table '$table' not found" -ForegroundColor Red
        $allTablesExist = $false
    }
}

# Show schema version
Write-Host "`n" -NoNewline
Write-Host "Schema Information:" -ForegroundColor Cyan
& psql -h $PgHost -p $PgPort -U $PgUser -d $PgDatabase -c "SELECT version, applied_at, description FROM schema_migrations ORDER BY applied_at DESC LIMIT 1" 2>&1 | Out-Host

# Summary
Write-Host "`n============================================" -ForegroundColor Cyan
if ($allTablesExist) {
    Write-Host "✓ All connection tests passed!" -ForegroundColor Green
    Write-Host "PostgreSQL is ready for testing" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠ Some tests failed" -ForegroundColor Yellow
    Write-Host "Run schema initialization if needed" -ForegroundColor Yellow
    exit 1
}
