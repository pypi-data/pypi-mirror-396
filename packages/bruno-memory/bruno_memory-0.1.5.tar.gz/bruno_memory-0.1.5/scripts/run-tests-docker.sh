#!/bin/bash
# Run tests with Docker services
# Manages Docker environment and executes pytest with proper configuration

set -e

# Default configuration
PROFILE="full"
MARKERS=()
TEST_PATH="tests/"
NO_COVERAGE=false
VERBOSE=false
KEEP_ENV=false
SETUP_ONLY=false
PYTEST_ARGS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile)
            PROFILE=$2
            shift 2
            ;;
        --markers)
            IFS=',' read -ra MARKERS <<< "$2"
            shift 2
            ;;
        --test-path)
            TEST_PATH=$2
            shift 2
            ;;
        --no-coverage)
            NO_COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --keep-env)
            KEEP_ENV=true
            shift
            ;;
        --setup-only)
            SETUP_ONLY=true
            shift
            ;;
        *)
            PYTEST_ARGS+=("$1")
            shift
            ;;
    esac
done

echo "============================================"
echo "Bruno-Memory Docker Test Runner"
echo "============================================"
echo "Profile: $PROFILE"
echo "Test path: $TEST_PATH"
if [ ${#MARKERS[@]} -gt 0 ]; then
    echo "Markers: ${MARKERS[*]}"
fi
echo "============================================"
echo ""

# Step 1: Setup test environment
echo "[1/4] Setting up test environment..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/setup-test-env.sh" --profile "$PROFILE"

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Failed to setup test environment"
    exit 1
fi

if [ "$SETUP_ONLY" = true ]; then
    echo ""
    echo "✓ Setup complete (setup-only mode)"
    exit 0
fi

# Step 2: Verify services are ready
echo ""
echo "[2/4] Verifying services..."
case $PROFILE in
    minimal)
        SERVICES_TO_WAIT="postgresql,redis"
        ;;
    *)
        SERVICES_TO_WAIT="postgresql,redis,chromadb,qdrant"
        ;;
esac
bash "$SCRIPT_DIR/wait-for-services.sh" --services "$SERVICES_TO_WAIT" --timeout 60

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Services not ready"
    exit 1
fi

# Step 3: Build pytest command
echo ""
echo "[3/4] Running tests..."

PYTEST_CMD=("pytest" "$TEST_PATH")

# Add markers
if [ ${#MARKERS[@]} -gt 0 ]; then
    MARKER_EXPR=$(IFS=" or "; echo "${MARKERS[*]}")
    PYTEST_CMD+=("-m" "$MARKER_EXPR")
fi

# Add coverage
if [ "$NO_COVERAGE" != true ]; then
    PYTEST_CMD+=(
        "--cov=bruno_memory"
        "--cov-report=html"
        "--cov-report=term-missing"
    )
fi

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD+=("-vv")
else
    PYTEST_CMD+=("-v")
fi

# Add additional pytest args
if [ ${#PYTEST_ARGS[@]} -gt 0 ]; then
    PYTEST_CMD+=("${PYTEST_ARGS[@]}")
fi

echo "  Command: ${PYTEST_CMD[*]}"

# Run pytest
set +e
"${PYTEST_CMD[@]}"
TEST_RESULT=$?
set -e

# Step 4: Cleanup (if not keeping environment)
if [ "$KEEP_ENV" != true ]; then
    echo ""
    echo "[4/4] Cleaning up test environment..."
    bash "$SCRIPT_DIR/teardown-test-env.sh" --profile "$PROFILE"
else
    echo ""
    echo "[4/4] Keeping test environment (use --keep-env to preserve)"
    echo "  To cleanup manually: ./scripts/teardown-test-env.sh"
fi

# Summary
echo ""
echo "============================================"
if [ $TEST_RESULT -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Some tests failed"
fi
echo "============================================"

exit $TEST_RESULT
