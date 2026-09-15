-- Migration: 010
-- Description: Create incremental_processing_status dashboard analytics monitor view

CREATE OR REPLACE VIEW incremental_processing_status AS
SELECT
    w.pipeline_name,
    w.source_name,
    w.last_raw_measurement_id,
    COALESCE(MAX(r.raw_measurement_id), 0) AS latest_raw_measurement_id,
    GREATEST(
        COALESCE(MAX(r.raw_measurement_id), 0) - w.last_raw_measurement_id,
        0
    ) AS pending_records,
    w.updated_at
FROM processing_watermarks w
LEFT JOIN raw_measurements r
    ON r.raw_measurement_id > w.last_raw_measurement_id
GROUP BY
    w.pipeline_name,
    w.source_name,
    w.last_raw_measurement_id,
    w.updated_at;
