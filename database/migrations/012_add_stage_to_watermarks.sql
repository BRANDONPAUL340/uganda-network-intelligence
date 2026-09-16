-- Migration: 012
-- Description: Evolve processing_watermarks ledger to support decoupled, stage-specific tracking variables

-- 1. Inject the stage tracking attribute column into the catalog
ALTER TABLE processing_watermarks
ADD COLUMN IF NOT EXISTS stage_name VARCHAR(50);

-- 2. Backfill existing row states to retain backward-compatibility metrics
UPDATE processing_watermarks
SET stage_name = 'SILVER'
WHERE stage_name IS NULL;

-- 3. Apply the strict structural NOT NULL contract constraint
ALTER TABLE processing_watermarks
ALTER COLUMN stage_name SET NOT NULL;

-- 4. Reconstruct the unique constraint index to pair pipeline, stage, and source targets
ALTER TABLE processing_watermarks
DROP CONSTRAINT IF EXISTS uq_processing_watermark;

ALTER TABLE processing_watermarks
ADD CONSTRAINT uq_processing_watermark_stage
UNIQUE (
    pipeline_name,
    stage_name,
    source_name
);

-- 5. Deploy an optimized search tree to accelerate stage checkpoint lookups
CREATE INDEX IF NOT EXISTS idx_processing_watermarks_stage
ON processing_watermarks (
    pipeline_name,
    stage_name
);
