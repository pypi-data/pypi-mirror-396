#!/bin/bash
# Wait for Docker services to be ready
# Tests each service's health and readiness before proceeding

set -e

# Default configuration
SERVICES=("postgresql" "redis" "chromadb" "qdrant")
TIMEOUT=120
CHECK_INTERVAL=2

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --services)
            IFS=',' read -ra SERVICES <<< "$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT=$2
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

echo "============================================"
echo "Waiting for Docker Services"
echo "============================================"
echo "Services to check: ${SERVICES[*]}"
echo "Timeout: $TIMEOUT seconds"
echo "============================================"
echo ""

START_TIME=$(date +%s)

# Service check functions
check_postgresql() {
    docker exec bruno-memory-postgres pg_isready -U postgres 2>&1 | grep -q "accepting connections"
}

check_redis() {
    docker exec bruno-memory-redis redis-cli ping 2>&1 | grep -q "PONG"
}

check_chromadb() {
    curl -sf "http://localhost:8000/api/v2/heartbeat" > /dev/null 2>&1
}

check_qdrant() {
    curl -sf "http://localhost:6333/healthz" > /dev/null 2>&1
}

# Check if containers are running
echo "[1/3] Checking if containers are running..."
ALL_RUNNING=true
for service in "${SERVICES[@]}"; do
    case $service in
        postgresql)
            CONTAINER="bruno-memory-postgres"
            ;;
        redis)
            CONTAINER="bruno-memory-redis"
            ;;
        chromadb)
            CONTAINER="bruno-memory-chromadb"
            ;;
        qdrant)
            CONTAINER="bruno-memory-qdrant"
            ;;
    esac
    
    if docker ps --filter "name=$CONTAINER" --format "{{.Names}}" | grep -q "$CONTAINER"; then
        echo "  ✓ $service container is running"
    else
        echo "  ✗ $service container is not running"
        ALL_RUNNING=false
    fi
done

if [ "$ALL_RUNNING" = false ]; then
    echo ""
    echo "✗ Some containers are not running. Please start them first."
    echo "  Run: docker-compose up -d"
    exit 1
fi

# Wait for services to be ready
echo ""
echo "[2/3] Waiting for services to be ready..."
declare -A READY_SERVICES

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo ""
        echo "✗ Timeout waiting for services to be ready"
        exit 1
    fi
    
    ALL_READY=true
    for service in "${SERVICES[@]}"; do
        if [ -z "${READY_SERVICES[$service]}" ]; then
            case $service in
                postgresql)
                    PORT=5432
                    ;;
                redis)
                    PORT=6379
                    ;;
                chromadb)
                    PORT=8000
                    ;;
                qdrant)
                    PORT=6333
                    ;;
            esac
            
            if check_$service 2>/dev/null; then
                READY_SERVICES[$service]=1
                echo "  ✓ $service is ready (port $PORT)"
            else
                ALL_READY=false
            fi
        fi
    done
    
    if [ "$ALL_READY" = true ]; then
        break
    fi
    
    sleep $CHECK_INTERVAL
done

# Final verification
echo ""
echo "[3/3] Final verification..."
ALL_HEALTHY=true
for service in "${SERVICES[@]}"; do
    if check_$service 2>/dev/null; then
        echo "  ✓ $service verified"
    else
        echo "  ✗ $service verification failed"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = true ]; then
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    echo ""
    echo "============================================"
    echo "✓ All services are ready!"
    echo "Time elapsed: $ELAPSED seconds"
    echo "============================================"
    exit 0
else
    echo ""
    echo "✗ Some services failed final verification"
    exit 1
fi
