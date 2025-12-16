"""
SQLite database schema definitions for bruno-memory.

Provides complete schema with proper indexing, constraints, and
optimization for bruno-core model storage and retrieval.
"""

# SQLite schema for bruno-memory
SCHEMA_SQL = """
-- Messages table for conversation history
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    message_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata TEXT,
    parent_id TEXT,
    conversation_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (parent_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- Memory entries table for persistent memory storage
CREATE TABLE IF NOT EXISTS memory_entries (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    user_id TEXT NOT NULL,
    conversation_id TEXT,
    metadata TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_accessed TEXT NOT NULL,
    expires_at TEXT,
    importance REAL DEFAULT 0.0,
    confidence REAL DEFAULT 0.0,
    embedding BLOB
);

-- Session contexts table for session management
CREATE TABLE IF NOT EXISTS session_contexts (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    last_activity TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    state TEXT NOT NULL DEFAULT '{}',
    metadata TEXT NOT NULL DEFAULT '{}'
);

-- User contexts table for user profiles and preferences
CREATE TABLE IF NOT EXISTS user_contexts (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    preferences TEXT NOT NULL DEFAULT '{}',
    profile TEXT NOT NULL DEFAULT '{}',
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    last_active TEXT NOT NULL
);

-- Conversation contexts table for conversation metadata
CREATE TABLE IF NOT EXISTS conversation_contexts (
    conversation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT,
    summary TEXT,
    tags TEXT,
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    message_count INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_contexts(user_id) ON DELETE CASCADE
);

-- Memory categories table for organizing memories
CREATE TABLE IF NOT EXISTS memory_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    parent_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (parent_id) REFERENCES memory_categories(id) ON DELETE CASCADE
);

-- Memory tags table for flexible tagging
CREATE TABLE IF NOT EXISTS memory_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Many-to-many relationship between memories and categories
CREATE TABLE IF NOT EXISTS memory_entry_categories (
    memory_id TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (memory_id, category_id),
    FOREIGN KEY (memory_id) REFERENCES memory_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES memory_categories(id) ON DELETE CASCADE
);

-- Many-to-many relationship between memories and tags
CREATE TABLE IF NOT EXISTS memory_entry_tags (
    memory_id TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (memory_id, tag_id),
    FOREIGN KEY (memory_id) REFERENCES memory_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES memory_tags(id) ON DELETE CASCADE
);

-- Indexes for performance optimization

-- Messages indexes
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_parent_id ON messages(parent_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);

-- Memory entries indexes
CREATE INDEX IF NOT EXISTS idx_memory_entries_user_id ON memory_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_entries_conversation_id ON memory_entries(conversation_id);
CREATE INDEX IF NOT EXISTS idx_memory_entries_memory_type ON memory_entries(memory_type);
CREATE INDEX IF NOT EXISTS idx_memory_entries_created_at ON memory_entries(created_at);
CREATE INDEX IF NOT EXISTS idx_memory_entries_updated_at ON memory_entries(updated_at);
CREATE INDEX IF NOT EXISTS idx_memory_entries_last_accessed ON memory_entries(last_accessed);
CREATE INDEX IF NOT EXISTS idx_memory_entries_expires_at ON memory_entries(expires_at);
CREATE INDEX IF NOT EXISTS idx_memory_entries_importance ON memory_entries(importance);
CREATE INDEX IF NOT EXISTS idx_memory_entries_confidence ON memory_entries(confidence);

-- Session contexts indexes
CREATE INDEX IF NOT EXISTS idx_session_contexts_user_id ON session_contexts(user_id);
CREATE INDEX IF NOT EXISTS idx_session_contexts_conversation_id ON session_contexts(conversation_id);
CREATE INDEX IF NOT EXISTS idx_session_contexts_is_active ON session_contexts(is_active);
CREATE INDEX IF NOT EXISTS idx_session_contexts_last_activity ON session_contexts(last_activity);

-- User contexts indexes
CREATE INDEX IF NOT EXISTS idx_user_contexts_last_active ON user_contexts(last_active);

-- Conversation contexts indexes
CREATE INDEX IF NOT EXISTS idx_conversation_contexts_user_id ON conversation_contexts(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_contexts_created_at ON conversation_contexts(created_at);
CREATE INDEX IF NOT EXISTS idx_conversation_contexts_updated_at ON conversation_contexts(updated_at);

-- Memory categories indexes
CREATE INDEX IF NOT EXISTS idx_memory_categories_parent_id ON memory_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_memory_categories_name ON memory_categories(name);

-- Memory tags indexes
CREATE INDEX IF NOT EXISTS idx_memory_tags_name ON memory_tags(name);

-- Full-text search support for content
CREATE VIRTUAL TABLE IF NOT EXISTS memory_entries_fts USING fts5(
    id UNINDEXED,
    content,
    content='memory_entries',
    content_rowid='rowid'
);

-- Triggers to keep FTS table in sync
CREATE TRIGGER IF NOT EXISTS memory_entries_fts_insert AFTER INSERT ON memory_entries
BEGIN
    INSERT INTO memory_entries_fts(rowid, id, content) VALUES (new.rowid, new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS memory_entries_fts_delete AFTER DELETE ON memory_entries
BEGIN
    INSERT INTO memory_entries_fts(memory_entries_fts, rowid, id, content) VALUES ('delete', old.rowid, old.id, old.content);
END;

CREATE TRIGGER IF NOT EXISTS memory_entries_fts_update AFTER UPDATE ON memory_entries
BEGIN
    INSERT INTO memory_entries_fts(memory_entries_fts, rowid, id, content) VALUES ('delete', old.rowid, old.id, old.content);
    INSERT INTO memory_entries_fts(rowid, id, content) VALUES (new.rowid, new.id, new.content);
END;

-- Views for common queries

-- Active sessions view
CREATE VIEW IF NOT EXISTS active_sessions AS
SELECT 
    sc.*,
    uc.name as user_name
FROM session_contexts sc
JOIN user_contexts uc ON sc.user_id = uc.user_id
WHERE sc.is_active = 1;

-- Recent conversations view
CREATE VIEW IF NOT EXISTS recent_conversations AS
SELECT 
    cc.*,
    uc.name as user_name,
    COUNT(m.id) as actual_message_count,
    MAX(m.timestamp) as last_message_at
FROM conversation_contexts cc
JOIN user_contexts uc ON cc.user_id = uc.user_id
LEFT JOIN messages m ON cc.conversation_id = m.conversation_id
GROUP BY cc.conversation_id, uc.name
ORDER BY cc.updated_at DESC;

-- Memory statistics view
CREATE VIEW IF NOT EXISTS memory_stats AS
SELECT 
    user_id,
    memory_type,
    COUNT(*) as entry_count,
    AVG(importance) as avg_importance,
    AVG(confidence) as avg_confidence,
    MIN(created_at) as oldest_entry,
    MAX(updated_at) as newest_entry
FROM memory_entries
GROUP BY user_id, memory_type;
"""

# Version tracking for schema migrations
SCHEMA_VERSION = "1.0.0"


def get_schema_version_sql() -> str:
    """Get SQL to create and populate schema version table."""
    return f"""
    CREATE TABLE IF NOT EXISTS schema_version (
        version TEXT PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT (datetime('now')),
        description TEXT
    );
    
    INSERT OR REPLACE INTO schema_version (version, description) 
    VALUES ('{SCHEMA_VERSION}', 'Initial bruno-memory SQLite schema');
    """


def get_full_schema_sql() -> str:
    """Get complete schema SQL including version tracking."""
    return SCHEMA_SQL + "\n\n" + get_schema_version_sql()


# Utility functions for schema operations
def get_table_names() -> list[str]:
    """Get list of all table names in the schema."""
    return [
        "messages",
        "memory_entries",
        "session_contexts",
        "user_contexts",
        "conversation_contexts",
        "memory_categories",
        "memory_tags",
        "memory_entry_categories",
        "memory_entry_tags",
        "schema_version",
    ]


def get_view_names() -> list[str]:
    """Get list of all view names in the schema."""
    return ["active_sessions", "recent_conversations", "memory_stats"]


def get_index_names() -> list[str]:
    """Get list of all index names in the schema."""
    return [
        "idx_messages_conversation_id",
        "idx_messages_timestamp",
        "idx_messages_parent_id",
        "idx_messages_role",
        "idx_memory_entries_user_id",
        "idx_memory_entries_conversation_id",
        "idx_memory_entries_memory_type",
        "idx_memory_entries_created_at",
        "idx_memory_entries_updated_at",
        "idx_memory_entries_last_accessed",
        "idx_memory_entries_expires_at",
        "idx_memory_entries_importance",
        "idx_memory_entries_confidence",
        "idx_session_contexts_user_id",
        "idx_session_contexts_conversation_id",
        "idx_session_contexts_is_active",
        "idx_session_contexts_last_activity",
        "idx_user_contexts_last_active",
        "idx_conversation_contexts_user_id",
        "idx_conversation_contexts_created_at",
        "idx_conversation_contexts_updated_at",
        "idx_memory_categories_parent_id",
        "idx_memory_categories_name",
        "idx_memory_tags_name",
    ]
