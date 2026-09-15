-- Migration: 005
-- Description: Create ingestion_batches tracking ledger and performance indexes

-- ----------------------------------------------------------------------------
-- 1. MATERIALIZE THE INGESTION BATCH REGISTRY TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingestion_batches (
    batch_id BIGSERIAL PRIMARY KEY,

    pipeline_run_id BIGINT,
    source_type VARCHAR(20) NOT NULL,
    source_name VARCHAR(255) NOT NULL,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    records_received INTEGER NOT NULL DEFAULT 0,
    records_loaded INTEGER NOT NULL DEFAULT 0,

    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    error_message TEXT,

    CONSTRAINT fk_ingestion_pipeline_run
        FOREIGN KEY (pipeline_run_id)
        REFERENCES pipeline_runs(run_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_ingestion_source_type
        CHECK (source_type IN ('CSV', 'API')),

    CONSTRAINT chk_ingestion_status
        CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),

    CONSTRAINT chk_records_received
        CHECK (records_received >= 0),

    CONSTRAINT chk_records_loaded
        CHECK (records_loaded >= 0)
);

-- ----------------------------------------------------------------------------
-- 2. DEPLOY DIAGNOSTIC SEARCH INDEX TREES
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_ingestion_batches_pipeline_run
    ON ingestion_batches(pipeline_run_id);

CREATE INDEX IF NOT EXISTS idx_ingestion_batches_source
    ON ingestion_batches(source_type, source_name);

CREATE INDEX IF NOT EXISTS idx_ingestion_batches_started
    ON ingestion_batches(started_at);
