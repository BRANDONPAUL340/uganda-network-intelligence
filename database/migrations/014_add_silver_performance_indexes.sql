-- Migration: 014
-- Description: Deploy high-performance composite index on silver_measurements (site_id, measured_at)

CREATE INDEX IF NOT EXISTS idx_silver_site_date
ON silver_measurements (
    site_id,
    measured_at
);
