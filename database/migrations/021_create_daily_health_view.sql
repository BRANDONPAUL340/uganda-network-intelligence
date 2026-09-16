-- Migration: 021
-- Description: Create daily_pipeline_health rolling timeline trend view

CREATE OR REPLACE VIEW daily_pipeline_health AS
SELECT
    pipeline_name,

    DATE(checked_at) AS health_date,

    COUNT(*) AS health_checks,

    COUNT(*) FILTER (
        WHERE overall_status = 'HEALTHY'
    ) AS healthy_checks,

    COUNT(*) FILTER (
        WHERE overall_status = 'WARNING'
    ) AS warning_checks,

    COUNT(*) FILTER (
        WHERE overall_status = 'CRITICAL'
    ) AS critical_checks,

    SUM(alert_count) AS total_alerts,

    SUM(warning_alert_count)
        AS warning_alerts,

    SUM(critical_alert_count)
        AS critical_alerts,

    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE overall_status = 'HEALTHY'
        )
        / NULLIF(COUNT(*), 0),
        2
    ) AS healthy_percentage

FROM pipeline_health_history

GROUP BY
    pipeline_name,
    DATE(checked_at);
