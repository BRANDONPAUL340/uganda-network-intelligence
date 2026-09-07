-- ============================================
-- Migration 002
-- Pipeline observability
-- ============================================

ALTER TABLE pipeline_runs
ADD COLUMN IF NOT EXISTS duration_seconds DECIMAL(12,3);

ALTER TABLE pipeline_runs
ADD COLUMN IF NOT EXISTS current_stage VARCHAR(30);
