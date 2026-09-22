-- Migration: 023
-- Description: Add nullable deployment_version metadata column to pipeline_runs table for release traceability

ALTER TABLE pipeline_runs 
ADD COLUMN IF NOT EXISTS deployment_version VARCHAR(20) DEFAULT NULL;
