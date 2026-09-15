-- Migration: 007
-- Description: Create quarantined_measurements operational error tracking ledger

-- ----------------------------------------------------------------------------
-- 1. MATERIALIZE THE QUARANTINE LEDGER TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quarantined_measurements (
    quarantine_id BIGSERIAL PRIMARY KEY,

    raw_measurement_id BIGINT NOT NULL,
    measurement_id BIGINT,

    rejection_reason VARCHAR(255) NOT NULL,
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    ingestion_batch_id BIGINT,
    pipeline_run_id BIGINT,

    -- Enforce foreign key constraints back to data platform tracking hubs
    CONSTRAINT fk_quarantine_raw
        FOREIGN KEY (raw_measurement_id)
        REFERENCES raw_measurements(raw_measurement_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_quarantine_batch
        FOREIGN KEY (ingestion_batch_id)
        REFERENCES ingestion_batches(batch_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_quarantine_pipeline
        FOREIGN KEY (pipeline_run_id)
        REFERENCES pipeline_runs(run_id)
        ON DELETE SET NULL,

    -- Block operational log duplication vectors completely
    CONSTRAINT uq_quarantine_raw_reason
        UNIQUE (raw_measurement_id, rejection_reason)
);

-- ----------------------------------------------------------------------------
-- 2. DEPLOY DIAGNOSTIC SEARCH INDEX TREES
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_quarantine_measurement
    ON quarantined_measurements(measurement_id);

CREATE INDEX IF NOT EXISTS idx_quarantine_batch
    ON quarantined_measurements(ingestion_batch_id);

CREATE INDEX IF NOT EXISTS idx_quarantine_rejected_at
    ON quarantined_measurements(rejected_at);
