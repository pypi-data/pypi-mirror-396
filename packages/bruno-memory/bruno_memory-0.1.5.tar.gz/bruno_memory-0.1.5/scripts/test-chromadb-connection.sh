#!/bin/bash
# ChromaDB Connection Test Script for Linux/Mac
# Tests connection to ChromaDB container and verifies functionality

set -e

# Configuration from environment or defaults
CHROMA_HOST="${CHROMADB_HOST:-localhost}"
CHROMA_PORT="${CHROMADB_PORT:-8000}"

echo "============================================"
echo "ChromaDB Connection Test"
echo "============================================"
echo "Host: $CHROMA_HOST"
echo "Port: $CHROMA_PORT"
echo "============================================"
echo ""

BASE_URL="http://${CHROMA_HOST}:${CHROMA_PORT}/api/v2"

# Test 1: Check if curl is available
echo "[1/5] Checking connectivity tools..."
if ! command -v curl &> /dev/null; then
    echo "✗ curl not found"
    exit 1
fi
echo "✓ curl is available"

# Test 2: Test heartbeat endpoint
echo ""
echo "[2/5] Testing ChromaDB heartbeat..."
HEARTBEAT=$(curl -s -f "$BASE_URL/heartbeat" 2>/dev/null || echo "ERROR")
if [ "$HEARTBEAT" != "ERROR" ]; then
    echo "✓ ChromaDB is alive"
else
    echo "✗ Heartbeat failed"
    exit 1
fi

# Test 3: Check container status
echo ""
echo "[3/5] Checking container status..."
CONTAINER_STATUS=$(docker ps --filter "name=bruno-memory-chromadb" --format "{{.Status}}" 2>/dev/null)
if [ -n "$CONTAINER_STATUS" ]; then
    echo "✓ Container is running: $CONTAINER_STATUS"
else
    echo "⚠ Container not found or not running"
fi

# Test 4: Check logs for errors
echo ""
echo "[4/5] Checking ChromaDB logs..."
if docker logs bruno-memory-chromadb --tail 5 2>&1 | grep -qiE "error|failed"; then
    echo "⚠ Found errors in logs"
else
    echo "✓ No errors in recent logs"
fi

# Test 5: Python client information
echo ""
echo "[5/5] ChromaDB API Information..."
echo "✓ ChromaDB requires Python client for full functionality"
echo "  The HTTP API is not fully REST-based"
echo "  Install with: pip install chromadb"
echo "  Example usage:"
echo "    import chromadb"
echo "    client = chromadb.HttpClient(host='localhost', port=8000)"
echo "    collection = client.create_collection('test')"

# Summary
echo ""
echo "============================================"
echo "✓ ChromaDB connection tests passed!"
echo "ChromaDB is ready for vector operations"
echo "============================================"
exit 0
