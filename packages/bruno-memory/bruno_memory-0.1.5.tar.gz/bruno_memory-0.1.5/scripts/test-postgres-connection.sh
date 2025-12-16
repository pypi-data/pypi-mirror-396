#!/bin/bash
# PostgreSQL Connection Test Script for Linux/Mac
# Tests connection to PostgreSQL container and verifies schema

set -e

# Configuration from environment or defaults
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-testpass123}"
POSTGRES_DB="${POSTGRES_DB:-bruno_memory_test}"

echo "============================================"
echo "PostgreSQL Connection Test"
echo "============================================"
echo "Host:     $POSTGRES_HOST"
echo "Port:     $POSTGRES_PORT"
echo "Database: $POSTGRES_DB"
echo "User:     $POSTGRES_USER"
echo "============================================"
echo ""

# Export password for psql
export PGPASSWORD=$POSTGRES_PASSWORD

# Test 1: Check if psql is available
echo "[1/5] Checking psql availability..."
if ! command -v psql &> /dev/null; then
    echo "✗ psql not found. Install PostgreSQL client tools or use Docker exec"
    echo ""
    echo "Alternative: Use Docker exec to test connection:"
    echo "  docker exec bruno-memory-postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c '\\l'"
    exit 1
fi
echo "✓ psql found at: $(which psql)"

# Test 2: Test basic connection
echo ""
echo "[2/5] Testing basic connection..."
if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c '\q' 2>/dev/null; then
    echo "✓ PostgreSQL server is reachable"
else
    echo "✗ Cannot connect to PostgreSQL server"
    exit 1
fi

# Test 3: Check database existence
echo ""
echo "[3/5] Checking database existence..."
DB_EXISTS=$(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB'" 2>/dev/null || echo "0")
if [ "$DB_EXISTS" = "1" ]; then
    echo "✓ Database '$POSTGRES_DB' exists"
else
    echo "✗ Database '$POSTGRES_DB' not found"
    exit 1
fi

# Test 4: Check extensions
echo ""
echo "[4/5] Checking required extensions..."
UUID_EXT=$(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT 1 FROM pg_extension WHERE extname='uuid-ossp'" 2>/dev/null || echo "0")
VECTOR_EXT=$(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT 1 FROM pg_extension WHERE extname='vector'" 2>/dev/null || echo "0")

if [ "$UUID_EXT" = "1" ]; then
    echo "✓ uuid-ossp extension is installed"
else
    echo "✗ uuid-ossp extension not found"
fi

if [ "$VECTOR_EXT" = "1" ]; then
    echo "✓ vector (pgvector) extension is installed"
else
    echo "⚠ vector (pgvector) extension not found"
fi

# Test 5: Check schema tables
echo ""
echo "[5/5] Checking schema tables..."
TABLES=("messages" "memory_entries" "session_contexts" "user_contexts" "conversation_contexts" "schema_migrations")
ALL_TABLES_EXIST=true

for table in "${TABLES[@]}"; do
    TABLE_EXISTS=$(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='$table'" 2>/dev/null || echo "0")
    if [ "$TABLE_EXISTS" = "1" ]; then
        echo "  ✓ Table '$table' exists"
    else
        echo "  ✗ Table '$table' not found"
        ALL_TABLES_EXIST=false
    fi
done

# Show schema version
echo ""
echo "Schema Information:"
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version, applied_at, description FROM schema_migrations ORDER BY applied_at DESC LIMIT 1" 2>/dev/null || echo "No schema version found"

# Summary
echo ""
echo "============================================"
if [ "$ALL_TABLES_EXIST" = true ]; then
    echo "✓ All connection tests passed!"
    echo "PostgreSQL is ready for testing"
    exit 0
else
    echo "⚠ Some tests failed"
    echo "Run schema initialization if needed"
    exit 1
fi
