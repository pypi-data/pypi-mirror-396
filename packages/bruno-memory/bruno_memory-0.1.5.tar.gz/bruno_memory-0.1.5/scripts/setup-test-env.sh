#!/bin/bash
# Setup test environment - starts Docker services and waits for readiness

set -e

# Default configuration
PROFILE="full"
PULL=false
BUILD=false
CLEAN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE=$2
            shift 2
            ;;
        --pull)
            PULL=true
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo "============================================"
echo "Bruno-Memory Test Environment Setup"
echo "============================================"
echo "Profile: $PROFILE"
echo "============================================"
echo ""

# Determine compose file
case $PROFILE in
    minimal)
        COMPOSE_FILE="docker-compose.minimal.yml"
        ;;
    ci)
        COMPOSE_FILE="docker-compose.ci.yml"
        ;;
    *)
        COMPOSE_FILE="docker-compose.yml"
        ;;
esac

echo "[1/5] Using compose file: $COMPOSE_FILE"

# Clean up if requested
if [ "$CLEAN" = true ]; then
    echo ""
    echo "[2/5] Cleaning up existing containers..."
    docker-compose -f $COMPOSE_FILE down -v 2>&1 > /dev/null
    echo "  ✓ Cleaned up"
else
    echo ""
    echo "[2/5] Skipping cleanup (use --clean to remove existing containers)"
fi

# Pull images if requested
if [ "$PULL" = true ]; then
    echo ""
    echo "[3/5] Pulling latest images..."
    docker-compose -f $COMPOSE_FILE pull
    echo "  ✓ Images pulled"
else
    echo ""
    echo "[3/5] Skipping image pull (use --pull to update images)"
fi

# Build custom images if requested
if [ "$BUILD" = true ]; then
    echo ""
    echo "[4/5] Building custom images..."
    docker-compose -f $COMPOSE_FILE build
    echo "  ✓ Images built"
else
    echo ""
    echo "[4/5] Skipping build (use --build to rebuild images)"
fi

# Start services
echo ""
echo "[5/5] Starting Docker services..."
if docker-compose -f $COMPOSE_FILE up -d 2>&1; then
    echo "  ✓ Services started"
else
    echo "  ✗ Failed to start services"
    exit 1
fi

# Determine which services to wait for based on profile
case $PROFILE in
    minimal)
        SERVICES_TO_WAIT="postgresql,redis"
        ;;
    *)
        SERVICES_TO_WAIT="postgresql,redis,chromadb,qdrant"
        ;;
esac

# Wait for services to be ready
echo ""
echo "[6/6] Waiting for services to be ready..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/wait-for-services.sh" --services "$SERVICES_TO_WAIT"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "✓ Test environment is ready!"
    echo "============================================"
    echo ""
    echo "Running containers:"
    docker ps --filter "name=bruno-memory" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "To run tests: pytest tests/"
    echo "To stop: docker-compose -f $COMPOSE_FILE down"
    exit 0
else
    echo ""
    echo "✗ Failed to setup test environment"
    exit 1
fi
