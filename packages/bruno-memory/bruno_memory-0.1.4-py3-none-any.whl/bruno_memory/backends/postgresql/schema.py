"""
PostgreSQL database schema for bruno-memory.

Provides production-ready schema with JSON support, indexes for performance,
and preparation for pgvector extension for semantic search.
"""

# Schema version for migrations
SCHEMA_VERSION = "1.0.0"

# PostgreSQL schema with JSON support and optimized indexes
SCHEMA_SQL = """
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "vector";  -- Uncomment when pgvector needed

-- Messages table with JSON metadata
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL DEFAULT 'text',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    parent_id UUID,
    conversation_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (parent_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- Indexes for messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_messages_parent ON messages(parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_messages_metadata ON messages USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_messages_content_search ON messages USING GIN(to_tsvector('english', content));

-- Memory entries table with JSON metadata and vector support preparation
CREATE TABLE IF NOT EXISTS memory_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    memory_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    conversation_id UUID,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_accessed TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    importance REAL DEFAULT 0.0,
    confidence REAL DEFAULT 0.0,
    embedding BYTEA
    -- embedding vector(1536)  -- Uncomment when pgvector enabled
);

-- Indexes for memory entries
CREATE INDEX IF NOT EXISTS idx_memory_user ON memory_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_conversation ON memory_entries(conversation_id) WHERE conversation_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type);
CREATE INDEX IF NOT EXISTS idx_memory_created ON memory_entries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_updated ON memory_entries(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_expires ON memory_entries(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_memory_importance ON memory_entries(importance DESC) WHERE importance > 0;
CREATE INDEX IF NOT EXISTS idx_memory_metadata ON memory_entries USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_memory_content_search ON memory_entries USING GIN(to_tsvector('english', content));
-- CREATE INDEX IF NOT EXISTS idx_memory_embedding ON memory_entries USING ivfflat(embedding vector_cosine_ops);

-- Session contexts table
CREATE TABLE IF NOT EXISTS session_contexts (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    conversation_id UUID NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    last_activity TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    state JSONB NOT NULL DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Indexes for session contexts
CREATE INDEX IF NOT EXISTS idx_session_user ON session_contexts(user_id);
CREATE INDEX IF NOT EXISTS idx_session_conversation ON session_contexts(conversation_id);
CREATE INDEX IF NOT EXISTS idx_session_active ON session_contexts(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_session_last_activity ON session_contexts(last_activity DESC);

-- User contexts table
CREATE TABLE IF NOT EXISTS user_contexts (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    profile JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for user contexts
CREATE INDEX IF NOT EXISTS idx_user_last_active ON user_contexts(last_active DESC);

-- Conversation contexts table
CREATE TABLE IF NOT EXISTS conversation_contexts (
    conversation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    metadata JSONB DEFAULT '{}',
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES user_contexts(user_id) ON DELETE CASCADE
);

-- Indexes for conversation contexts
CREATE INDEX IF NOT EXISTS idx_conversation_user ON conversation_contexts(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_updated ON conversation_contexts(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversation_created ON conversation_contexts(created_at DESC);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT
);

-- Insert initial schema version
INSERT INTO schema_migrations (version, description) 
VALUES ('1.0.0', 'Initial schema with messages, memories, sessions, and contexts')
ON CONFLICT (version) DO NOTHING;

-- Triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_memory_entries_updated_at 
    BEFORE UPDATE ON memory_entries 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_contexts_updated_at 
    BEFORE UPDATE ON conversation_contexts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update last_activity in sessions
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_activity = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_session_contexts_activity 
    BEFORE UPDATE ON session_contexts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_session_activity();
"""


def get_full_schema_sql() -> str:
    """Get the complete PostgreSQL schema SQL.

    Returns:
        str: Complete schema SQL
    """
    return SCHEMA_SQL


def get_drop_schema_sql() -> str:
    """Get SQL to drop all schema objects.

    Returns:
        str: SQL to drop schema
    """
    return """
    DROP TABLE IF EXISTS schema_migrations CASCADE;
    DROP TABLE IF EXISTS conversation_contexts CASCADE;
    DROP TABLE IF EXISTS user_contexts CASCADE;
    DROP TABLE IF EXISTS session_contexts CASCADE;
    DROP TABLE IF EXISTS memory_entries CASCADE;
    DROP TABLE IF EXISTS messages CASCADE;
    DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
    DROP FUNCTION IF EXISTS update_session_activity CASCADE;
    """


# Migration templates for future schema changes
MIGRATION_TEMPLATE = """
-- Migration: {version}
-- Description: {description}
-- Date: {date}

-- Forward migration
BEGIN;

{forward_sql}

-- Record migration
INSERT INTO schema_migrations (version, description) 
VALUES ('{version}', '{description}');

COMMIT;
"""

ROLLBACK_TEMPLATE = """
-- Rollback: {version}
-- Description: {description}

BEGIN;

{rollback_sql}

-- Remove migration record
DELETE FROM schema_migrations WHERE version = '{version}';

COMMIT;
"""
