#!/bin/bash
# PostgreSQL Schema Setup Script
# This script can be used to reset or rebuild the database schema

set -e

# Configuration from environment or defaults
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-bruno_memory_test}"

echo "================================================"
echo "Bruno-Memory PostgreSQL Schema Setup"
echo "================================================"
echo "Host: $POSTGRES_HOST"
echo "Port: $POSTGRES_PORT"
echo "Database: $POSTGRES_DB"
echo "User: $POSTGRES_USER"
echo "================================================"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is ready!"

# Check if database exists, create if not
echo "Checking database existence..."
DB_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB'" 2>/dev/null || echo "0")

if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating database $POSTGRES_DB..."
    PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $POSTGRES_DB;"
    echo "Database created successfully!"
else
    echo "Database $POSTGRES_DB already exists."
fi

# Apply schema
echo "Applying schema..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$(dirname "$0")/init.sql"

echo "================================================"
echo "Schema setup completed successfully!"
echo "================================================"

# Show schema version
echo "Current schema version:"
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version, applied_at, description FROM schema_migrations ORDER BY applied_at DESC LIMIT 5;"

echo ""
echo "Tables created:"
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"

echo ""
echo "Setup complete! You can now run tests."
