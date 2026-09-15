-- Migration: 006
-- Description: Add ingestion_batch_id column and foreign key constraint to raw_measurements

-- 1. Inject the tracking key field safely into the table schema
ALTER TABLE raw_measurements
ADD COLUMN IF NOT EXISTS ingestion_batch_id BIGINT;

-- 2. Bind the new column to our master operational audit ledger
ALTER TABLE raw_measurements
ADD CONSTRAINT fk_raw_ingestion_batch
FOREIGN KEY (ingestion_batch_id)
REFERENCES ingestion_batches(batch_id)
ON DELETE SET NULL;

-- 3. Provision an optimization index tree to accelerate batch promotions
CREATE INDEX IF NOT EXISTS idx_raw_ingestion_batch
ON raw_measurements(ingestion_batch_id);
