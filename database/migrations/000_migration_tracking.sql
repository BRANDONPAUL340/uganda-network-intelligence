-- ============================================================================
-- UGANDA NETWORK PLATFORM — SCHEMA EVOLUTION VERSION MONITORING LEDGER
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
