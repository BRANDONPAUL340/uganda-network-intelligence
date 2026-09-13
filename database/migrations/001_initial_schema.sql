-- Migration: 001
-- Description: Baseline existing Uganda Network Intelligence schema

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (version, description)
VALUES ('001', 'baseline existing Uganda Network Intelligence schema')
ON CONFLICT (version) DO NOTHING;
