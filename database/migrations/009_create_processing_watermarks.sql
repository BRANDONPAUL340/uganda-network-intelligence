-- Migration: 009
-- Description: Create processing_watermarks operational delta checkpoint ledger

-- ----------------------------------------------------------------------------
-- 1. MATERIALIZE THE HIGH-WATERMARK CHECKPOINT LEDGER
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS processing_watermarks (
    watermark_id BIGSERIAL PRIMARY KEY,
    pipeline_name VARCHAR(255) NOT NULL,
    source_name VARCHAR(255) NOT NULL,
    last_raw_measurement_id BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Enforce absolute state uniqueness across single execution targets
    CONSTRAINT uq_processing_watermark
        UNIQUE (pipeline_name, source_name),

    -- Guarantee baseline pointer integrity boundaries
    CONSTRAINT chk_last_raw_measurement_id
        CHECK (last_raw_measurement_id >= 0)
);

-- ----------------------------------------------------------------------------
-- 2. DEPLOY DIAGNOSTIC ARCHITECTURE SEARCH INDEXES
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_processing_watermarks_pipeline
ON processing_watermarks(pipeline_name);
