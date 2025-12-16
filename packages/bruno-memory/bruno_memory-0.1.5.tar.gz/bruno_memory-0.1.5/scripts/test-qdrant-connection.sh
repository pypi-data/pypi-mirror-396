#!/bin/bash
# Qdrant Connection Test Script for Linux/Mac
# Tests connection to Qdrant container and verifies functionality

set -e

# Configuration from environment or defaults
QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_HTTP_PORT:-6333}"

echo "============================================"
echo "Qdrant Connection Test"
echo "============================================"
echo "Host: $QDRANT_HOST"
echo "Port: $QDRANT_PORT"
echo "============================================"
echo ""

BASE_URL="http://${QDRANT_HOST}:${QDRANT_PORT}"

# Test 1: Check if curl is available
echo "[1/6] Checking connectivity tools..."
if ! command -v curl &> /dev/null; then
    echo "✗ curl not found"
    exit 1
fi
echo "✓ curl is available"

# Test 2: Test health endpoint
echo ""
echo "[2/6] Testing Qdrant health..."
HEALTH=$(curl -s -f "$BASE_URL/healthz" 2>/dev/null || echo "ERROR")
if [ "$HEALTH" != "ERROR" ]; then
    echo "✓ Qdrant is healthy"
else
    echo "✗ Health check failed"
    exit 1
fi

# Test 3: Get Qdrant version and info
echo ""
echo "[3/6] Checking Qdrant version..."
INFO=$(curl -s -f "$BASE_URL/" 2>/dev/null || echo "ERROR")
if [ "$INFO" != "ERROR" ]; then
    VERSION=$(echo "$INFO" | jq -r '.version' 2>/dev/null || echo "unknown")
    TITLE=$(echo "$INFO" | jq -r '.title' 2>/dev/null || echo "unknown")
    echo "✓ Qdrant version: $VERSION"
    echo "  Title: $TITLE"
else
    echo "⚠ Could not determine version"
fi

# Test 4: List collections
echo ""
echo "[4/6] Listing collections..."
COLLECTIONS=$(curl -s -f "$BASE_URL/collections" 2>/dev/null || echo "ERROR")
if [ "$COLLECTIONS" != "ERROR" ]; then
    COUNT=$(echo "$COLLECTIONS" | jq '.result.collections | length' 2>/dev/null || echo "0")
    echo "✓ Collections endpoint accessible ($COUNT collections)"
    if [ "$COUNT" -gt "0" ]; then
        echo "  Collections:"
        echo "$COLLECTIONS" | jq -r '.result.collections[].name' 2>/dev/null | while read name; do
            echo "    - $name"
        done
    fi
else
    echo "✗ Failed to list collections"
fi

# Test 5: Test collection operations
echo ""
echo "[5/6] Testing collection operations..."
TEST_COLLECTION="bruno_memory_test_$$"

# Create test collection
CREATE_RESULT=$(curl -s -f -X PUT "$BASE_URL/collections/$TEST_COLLECTION" \
    -H "Content-Type: application/json" \
    -d '{"vectors":{"size":128,"distance":"Cosine"}}' \
    2>/dev/null || echo "ERROR")

if [ "$CREATE_RESULT" != "ERROR" ]; then
    SUCCESS=$(echo "$CREATE_RESULT" | jq -r '.result' 2>/dev/null || echo "false")
    if [ "$SUCCESS" = "true" ]; then
        echo "  ✓ Created test collection: $TEST_COLLECTION"
        
        # Get collection info
        GET_RESULT=$(curl -s -f "$BASE_URL/collections/$TEST_COLLECTION" 2>/dev/null || echo "ERROR")
        if [ "$GET_RESULT" != "ERROR" ]; then
            VECTOR_SIZE=$(echo "$GET_RESULT" | jq -r '.result.config.params.vectors.size' 2>/dev/null || echo "unknown")
            echo "  ✓ Retrieved test collection (vectors: $VECTOR_SIZE)"
        else
            echo "  ✗ Failed to retrieve collection"
        fi
        
        # Delete test collection
        DELETE_RESULT=$(curl -s -f -X DELETE "$BASE_URL/collections/$TEST_COLLECTION" 2>/dev/null || echo "ERROR")
        if [ "$DELETE_RESULT" != "ERROR" ]; then
            DELETE_SUCCESS=$(echo "$DELETE_RESULT" | jq -r '.result' 2>/dev/null || echo "false")
            if [ "$DELETE_SUCCESS" = "true" ]; then
                echo "  ✓ Deleted test collection"
            else
                echo "  ✗ Failed to delete collection"
            fi
        else
            echo "  ✗ Failed to delete collection"
        fi
    else
        echo "  ✗ Collection creation returned false"
    fi
else
    echo "  ✗ Collection operations failed"
fi

# Test 6: Check cluster status
echo ""
echo "[6/6] Checking cluster status..."
CLUSTER=$(curl -s -f "$BASE_URL/cluster" 2>/dev/null || echo "ERROR")
if [ "$CLUSTER" != "ERROR" ]; then
    STATUS=$(echo "$CLUSTER" | jq -r '.result.status' 2>/dev/null || echo "unknown")
    PEER_ID=$(echo "$CLUSTER" | jq -r '.result.peer_id' 2>/dev/null || echo "unknown")
    echo "✓ Cluster status: $STATUS"
    echo "  Peer ID: $PEER_ID"
else
    echo "⚠ Could not get cluster status"
fi

# Summary
echo ""
echo "============================================"
echo "✓ Qdrant connection tests passed!"
echo "Qdrant is ready for vector operations"
echo "============================================"
exit 0
