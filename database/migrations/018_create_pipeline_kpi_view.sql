-- Migration: 018
-- Description: Create pipeline_kpis operational dashboard and reporting metric view

CREATE OR REPLACE VIEW pipeline_kpis AS
WITH pipeline_stats AS (
    SELECT
        pipeline_name,
        COUNT(*) AS total_runs,
        COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_runs,
        COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_runs,
        COUNT(*) FILTER (WHERE status = 'RUNNING') AS running_runs
    FROM pipeline_runs
    GROUP BY pipeline_name
),
health_stats AS (
    SELECT
        pipeline_name,
        COUNT(*) AS total_health_checks,
        COUNT(*) FILTER (WHERE overall_status = 'HEALTHY') AS healthy_checks,
        COUNT(*) FILTER (WHERE overall_status = 'WARNING') AS warning_checks,
        COUNT(*) FILTER (WHERE overall_status = 'CRITICAL') AS critical_checks,
        COALESCE(SUM(alert_count), 0) AS total_alerts,
        COALESCE(SUM(warning_alert_count), 0) AS total_warning_alerts,
        COALESCE(SUM(critical_alert_count), 0) AS total_critical_alerts
    FROM pipeline_health_history
    GROUP BY pipeline_name
)
SELECT
    p.pipeline_name,
    p.total_runs,
    p.successful_runs,
    p.failed_runs,
    p.running_runs,
    ROUND(
        100.0 * p.successful_runs / NULLIF(p.total_runs, 0),
        2
    ) AS pipeline_success_rate,
    COALESCE(h.total_health_checks, 0) AS total_health_checks,
    COALESCE(h.healthy_checks, 0) AS healthy_checks,
    COALESCE(h.warning_checks, 0) AS warning_checks,
    COALESCE(h.critical_checks, 0) AS critical_checks,
    COALESCE(
        ROUND(
            100.0 * h.healthy_checks / NULLIF(h.total_health_checks, 0),
            2
        ),
        0
    ) AS healthy_percentage,
    COALESCE(h.total_alerts, 0) AS total_alerts,
    COALESCE(h.total_warning_alerts, 0) AS total_warning_alerts,
    COALESCE(h.total_critical_alerts, 0) AS total_critical_alerts
FROM pipeline_stats p
LEFT JOIN health_stats h ON p.pipeline_name = h.pipeline_name;
