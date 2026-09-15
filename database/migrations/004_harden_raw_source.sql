-- Migration: 004
-- Description: Harden raw_measurements table by setting source_file to NOT NULL

-- 1. Backfill any accidental historical NULL values to preserve data state integrity
UPDATE raw_measurements
SET source_file = 'unknown_source'
WHERE source_file IS NULL;

-- 2. Enforce structural constraint boundary rules onto the database catalog
ALTER TABLE raw_measurements
ALTER COLUMN source_file SET NOT NULL;
