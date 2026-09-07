-- ============================================
-- Migration 004
-- Uganda Network Intelligence
-- Data Quality Results & Observability Ledger
-- ============================================

CREATE TABLE IF NOT EXISTS data_quality_results (
    quality_result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id INTEGER NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    check_name VARCHAR(100) NOT NULL,
    check_type VARCHAR(50) NOT NULL DEFAULT 'VALIDITY',
    status VARCHAR(20) NOT NULL,
    records_checked BIGINT DEFAULT 0,
    records_failed BIGINT DEFAULT 0,
    failure_rate_pct NUMERIC(8,3) DEFAULT 0.0,
    details TEXT,
    checked_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,

    CONSTRAINT fk_quality_run
        FOREIGN KEY (run_id)
        REFERENCES pipeline_runs(run_id)
);

-- Apply high-performance indexes for monitoring queries
CREATE INDEX IF NOT EXISTS idx_quality_run_id ON data_quality_results(run_id);
CREATE INDEX IF NOT EXISTS idx_quality_status ON data_quality_results(status);
