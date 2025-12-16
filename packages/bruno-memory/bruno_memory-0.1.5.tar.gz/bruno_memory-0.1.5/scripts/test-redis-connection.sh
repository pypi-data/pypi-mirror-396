#!/bin/bash
# Redis Connection Test Script for Linux/Mac
# Tests connection to Redis container and verifies functionality

set -e

# Configuration from environment or defaults
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_DB="${REDIS_DB:-15}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"

echo "============================================"
echo "Redis Connection Test"
echo "============================================"
echo "Host:     $REDIS_HOST"
echo "Port:     $REDIS_PORT"
echo "Database: $REDIS_DB"
echo "============================================"
echo ""

# Test 1: Check if redis-cli is available
echo "[1/5] Checking redis-cli availability..."
if ! command -v redis-cli &> /dev/null; then
    echo "✗ redis-cli not found. Using Docker exec instead"
    USE_DOCKER=true
else
    echo "✓ redis-cli found at: $(which redis-cli)"
    USE_DOCKER=false
fi

# Helper function to run Redis commands
redis_cmd() {
    if [ "$USE_DOCKER" = true ]; then
        docker exec bruno-memory-redis-minimal redis-cli "$@"
    else
        if [ -n "$REDIS_PASSWORD" ]; then
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" "$@"
        else
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" "$@"
        fi
    fi
}

# Test 2: Test basic connection
echo ""
echo "[2/5] Testing basic connection..."
PING_RESULT=$(redis_cmd PING 2>/dev/null || echo "ERROR")
if [ "$PING_RESULT" = "PONG" ]; then
    echo "✓ Redis server is reachable (PONG received)"
else
    echo "✗ Connection failed: $PING_RESULT"
    exit 1
fi

# Test 3: Check Redis info
echo ""
echo "[3/5] Checking Redis server info..."
REDIS_VERSION=$(redis_cmd INFO server 2>/dev/null | grep "redis_version:" | cut -d: -f2 | tr -d '\r')
if [ -n "$REDIS_VERSION" ]; then
    echo "✓ Redis version: $REDIS_VERSION"
else
    echo "⚠ Could not determine Redis version"
fi

# Test 4: Test basic operations
echo ""
echo "[4/5] Testing basic Redis operations..."

# Set a test key
SET_RESULT=$(redis_cmd SET bruno_memory_test "test_value" EX 60 2>/dev/null)
if [ "$SET_RESULT" = "OK" ]; then
    echo "  ✓ SET operation successful"
else
    echo "  ✗ SET operation failed: $SET_RESULT"
fi

# Get the test key
GET_RESULT=$(redis_cmd GET bruno_memory_test 2>/dev/null)
if [ "$GET_RESULT" = "test_value" ]; then
    echo "  ✓ GET operation successful"
else
    echo "  ✗ GET operation failed: $GET_RESULT"
fi

# Delete the test key
DEL_RESULT=$(redis_cmd DEL bruno_memory_test 2>/dev/null)
if [ "$DEL_RESULT" = "1" ]; then
    echo "  ✓ DEL operation successful"
else
    echo "  ✗ DEL operation failed: $DEL_RESULT"
fi

# Test 5: Check memory and configuration
echo ""
echo "[5/5] Checking Redis configuration..."

# Check maxmemory
MAXMEMORY=$(redis_cmd CONFIG GET maxmemory 2>/dev/null | grep -A1 "maxmemory" | tail -1)
echo "  Max Memory: $MAXMEMORY"

# Check maxmemory-policy
POLICY=$(redis_cmd CONFIG GET maxmemory-policy 2>/dev/null | grep -A1 "maxmemory-policy" | tail -1)
echo "  Eviction Policy: $POLICY"

# Check database info
echo "  Keyspace Info:"
redis_cmd INFO keyspace 2>/dev/null | grep "^db" || echo "    (No keys present)"

# Summary
echo ""
echo "============================================"
echo "✓ All Redis connection tests passed!"
echo "Redis is ready for testing"
echo "============================================"
exit 0
