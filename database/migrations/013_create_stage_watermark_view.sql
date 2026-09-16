-- Migration: 013
-- Description: Create stage_watermark_status operational monitoring dashboard view

CREATE OR REPLACE VIEW stage_watermark_status AS
SELECT
    pipeline_name,
    stage_name,
    source_name,
    last_raw_measurement_id,
    updated_at
FROM processing_watermarks
ORDER BY
    pipeline_name,
    stage_name;
