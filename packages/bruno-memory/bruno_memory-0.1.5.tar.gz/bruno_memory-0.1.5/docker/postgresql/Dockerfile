# PostgreSQL with pgvector extension for bruno-memory
# Using pgvector/pgvector image which has pgvector pre-installed

FROM pgvector/pgvector:pg16

# Metadata
LABEL maintainer="meggy-ai <contact@meggy-ai.com>"
LABEL description="PostgreSQL 16 with pgvector extension for bruno-memory testing"
LABEL version="1.0"

# Install additional tools for healthcheck and utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for PostgreSQL
ENV POSTGRES_INITDB_ARGS="-E UTF8"
ENV PGDATA=/var/lib/postgresql/data

# Expose PostgreSQL port
EXPOSE 5432

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=30s \
    CMD pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-postgres}

# Use the default PostgreSQL entrypoint
# The entrypoint will automatically run scripts in /docker-entrypoint-initdb.d/
