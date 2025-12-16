#!/bin/bash
# Teardown test environment - stops and optionally removes Docker services

# Default configuration
PROFILE="full"
VOLUMES=false
FORCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE=$2
            shift 2
            ;;
        --volumes)
            VOLUMES=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo "============================================"
echo "Bruno-Memory Test Environment Teardown"
echo "============================================"
echo "Profile: $PROFILE"
echo "Remove volumes: $VOLUMES"
echo "============================================"
echo ""

# Determine compose files to stop
COMPOSE_FILES=()
if [ "$PROFILE" = "all" ]; then
    COMPOSE_FILES=("docker-compose.yml" "docker-compose.minimal.yml" "docker-compose.ci.yml")
    echo "[1/2] Stopping all compose configurations..."
else
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
    COMPOSE_FILES=("$COMPOSE_FILE")
    echo "[1/2] Stopping $COMPOSE_FILE..."
fi

# Build docker-compose command arguments
DOWN_ARGS=()
if [ "$VOLUMES" = true ]; then
    DOWN_ARGS+=("-v")
fi

# Stop each compose configuration
SUCCESS=true
for file in "${COMPOSE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Stopping services from $file..."
        
        if docker-compose -f "$file" down "${DOWN_ARGS[@]}" 2>&1; then
            echo "  ✓ Stopped $file"
        else
            echo "  ⚠ Warning: Some issues stopping $file"
            if [ "$FORCE" != true ]; then
                SUCCESS=false
            fi
        fi
    else
        echo "  ⚠ File not found: $file"
    fi
done

# Show remaining containers
echo ""
echo "[2/2] Checking for remaining bruno-memory containers..."
REMAINING_CONTAINERS=$(docker ps -a --filter "name=bruno-memory" --format "{{.Names}}")

if [ -n "$REMAINING_CONTAINERS" ]; then
    echo "  ⚠ Some containers still exist:"
    echo "$REMAINING_CONTAINERS" | while read container; do
        echo "    - $container"
    done
    
    if [ "$FORCE" = true ]; then
        echo ""
        echo "  Force removing containers..."
        echo "$REMAINING_CONTAINERS" | while read container; do
            docker rm -f "$container" 2>&1 > /dev/null
        done
        echo "  ✓ Containers removed"
    fi
else
    echo "  ✓ No bruno-memory containers remaining"
fi

# Show remaining volumes if not removed
if [ "$VOLUMES" != true ]; then
    echo ""
    echo "[Info] Checking for bruno-memory volumes..."
    VOLUMES_LIST=$(docker volume ls --filter "name=bruno-memory" --format "{{.Name}}")
    
    if [ -n "$VOLUMES_LIST" ]; then
        echo "  Data volumes still exist (use --volumes to remove):"
        echo "$VOLUMES_LIST" | while read volume; do
            echo "    - $volume"
        done
    fi
fi

# Summary
echo ""
echo "============================================"
if [ "$SUCCESS" = true ]; then
    echo "✓ Test environment teardown complete!"
    if [ "$VOLUMES" = true ]; then
        echo "  All data has been removed"
    else
        echo "  Data volumes preserved (use --volumes to remove)"
    fi
else
    echo "⚠ Teardown completed with warnings"
    echo "  Use --force to remove containers forcefully"
fi
echo "============================================"
exit 0
