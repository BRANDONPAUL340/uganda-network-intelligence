-- Migration: 017
-- Description: Create recent_pipeline_health rolling 24-hour monitoring dashboard view

CREATE OR REPLACE VIEW recent_pipeline_health AS
SELECT
    health_id,
    pipeline_name,
    checked_at,
    overall_status,
    database_status,
    pipeline_run_status,
    pipeline_stage_status,
    alert_count,
    critical_alert_count,
    warning_alert_count
FROM pipeline_health_history
WHERE checked_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY checked_at DESC;
