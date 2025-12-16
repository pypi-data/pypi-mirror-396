-- Development Helper Queries for bruno-memory PostgreSQL
-- This file contains useful queries for development and debugging

-- ================================================
-- Database Information
-- ================================================

-- Show all tables with row counts
SELECT 
    schemaname,
    tablename,
    n_tup_ins AS inserts,
    n_tup_upd AS updates,
    n_tup_del AS deletes,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows
FROM pg_stat_user_tables
ORDER BY tablename;

-- Show database size
SELECT 
    pg_database.datname AS database_name,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = current_database();

-- ================================================
-- Extension Status
-- ================================================

-- Check installed extensions
SELECT 
    extname AS extension_name,
    extversion AS version,
    extrelocatable AS relocatable
FROM pg_extension
ORDER BY extname;

-- ================================================
-- Table Statistics
-- ================================================

-- Messages table statistics
SELECT 
    COUNT(*) AS total_messages,
    COUNT(DISTINCT conversation_id) AS unique_conversations,
    COUNT(DISTINCT role) AS unique_roles,
    MIN(timestamp) AS earliest_message,
    MAX(timestamp) AS latest_message
FROM messages;

-- Memory entries statistics
SELECT 
    COUNT(*) AS total_memories,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(DISTINCT memory_type) AS unique_types,
    AVG(importance) AS avg_importance,
    AVG(confidence) AS avg_confidence,
    COUNT(*) FILTER (WHERE embedding IS NOT NULL) AS with_embeddings
FROM memory_entries;

-- Session statistics
SELECT 
    COUNT(*) AS total_sessions,
    COUNT(*) FILTER (WHERE is_active = TRUE) AS active_sessions,
    COUNT(DISTINCT user_id) AS unique_users,
    AVG(EXTRACT(EPOCH FROM (COALESCE(ended_at, NOW()) - started_at))) AS avg_duration_seconds
FROM session_contexts;

-- ================================================
-- Recent Activity
-- ================================================

-- Recent messages (last 10)
SELECT 
    id,
    role,
    LEFT(content, 50) AS content_preview,
    message_type,
    timestamp,
    conversation_id
FROM messages
ORDER BY timestamp DESC
LIMIT 10;

-- Recent memory entries (last 10)
SELECT 
    id,
    LEFT(content, 50) AS content_preview,
    memory_type,
    user_id,
    importance,
    confidence,
    created_at
FROM memory_entries
ORDER BY created_at DESC
LIMIT 10;

-- ================================================
-- Index Health
-- ================================================

-- Show index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Show unused indexes (potential candidates for removal)
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- ================================================
-- Performance Queries
-- ================================================

-- Show slow queries (requires pg_stat_statements extension)
-- Uncomment to use:
-- SELECT 
--     LEFT(query, 100) AS query_preview,
--     calls,
--     total_exec_time,
--     mean_exec_time,
--     max_exec_time
-- FROM pg_stat_statements
-- ORDER BY mean_exec_time DESC
-- LIMIT 20;

-- Show table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ================================================
-- Data Cleanup Helpers
-- ================================================

-- Clear all test data (use with caution!)
-- TRUNCATE TABLE messages CASCADE;
-- TRUNCATE TABLE memory_entries CASCADE;
-- TRUNCATE TABLE session_contexts CASCADE;
-- TRUNCATE TABLE conversation_contexts CASCADE;
-- TRUNCATE TABLE user_contexts CASCADE;

-- Delete old messages (older than 7 days)
-- DELETE FROM messages WHERE timestamp < NOW() - INTERVAL '7 days';

-- Delete expired memories
-- DELETE FROM memory_entries WHERE expires_at IS NOT NULL AND expires_at < NOW();

-- ================================================
-- Vector Search Examples (requires data with embeddings)
-- ================================================

-- Find similar memories using cosine similarity
-- SELECT 
--     id,
--     content,
--     1 - (embedding <=> '[your_embedding_vector]'::vector) AS similarity
-- FROM memory_entries
-- WHERE embedding IS NOT NULL
-- ORDER BY embedding <=> '[your_embedding_vector]'::vector
-- LIMIT 10;

-- ================================================
-- Schema Information
-- ================================================

-- Show current schema version
SELECT * FROM schema_migrations ORDER BY applied_at DESC;

-- Show all triggers
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- Show all foreign keys
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;
