-- Migration: 022
-- Description: Create current_pipeline_health real-time snapshot target view

CREATE OR REPLACE VIEW current_pipeline_health AS
SELECT
    health_id,
    pipeline_name,
    checked_at,
    overall_status,
    database_status,
    pipeline_run_status,
    pipeline_stage_status,
    alert_count,
    warning_alert_count,
    critical_alert_count
FROM pipeline_health_history
WHERE health_id = (
    SELECT MAX(health_id)
    FROM pipeline_health_history
);
