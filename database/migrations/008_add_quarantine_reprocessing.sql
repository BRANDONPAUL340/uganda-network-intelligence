-- Migration: 008
-- Description: Add lifecycle status, retry counters, and auditing logs to quarantined_measurements

ALTER TABLE quarantined_measurements
ADD COLUMN IF NOT EXISTS status VARCHAR(30)
    NOT NULL DEFAULT 'QUARANTINED';

ALTER TABLE quarantined_measurements
ADD COLUMN IF NOT EXISTS reprocessed_at TIMESTAMPTZ;

ALTER TABLE quarantined_measurements
ADD COLUMN IF NOT EXISTS reprocessing_attempts INTEGER
    NOT NULL DEFAULT 0;

ALTER TABLE quarantined_measurements
ADD COLUMN IF NOT EXISTS resolution_notes TEXT;

ALTER TABLE quarantined_measurements
DROP CONSTRAINT IF EXISTS chk_quarantine_status;

ALTER TABLE quarantined_measurements
ADD CONSTRAINT chk_quarantine_status
CHECK (
    status IN (
        'QUARANTINED',
        'REPROCESSED',
        'REPROCESS_FAILED'
    )
);

ALTER TABLE quarantined_measurements
DROP CONSTRAINT IF EXISTS chk_reprocessing_attempts;

ALTER TABLE quarantined_measurements
ADD CONSTRAINT chk_reprocessing_attempts
CHECK (reprocessing_attempts >= 0);

CREATE INDEX IF NOT EXISTS idx_quarantine_status
ON quarantined_measurements(status);
