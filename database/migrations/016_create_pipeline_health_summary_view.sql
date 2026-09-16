-- Migration: 016
-- Description: Create pipeline_health_summary operational monitoring dashboard view

CREATE OR REPLACE VIEW pipeline_health_summary AS
SELECT
    pipeline_name,

    COUNT(*) AS total_checks,

    COUNT(*) FILTER (
        WHERE overall_status = 'HEALTHY'
    ) AS healthy_checks,

    COUNT(*) FILTER (
        WHERE overall_status = 'WARNING'
    ) AS warning_checks,

    COUNT(*) FILTER (
        WHERE overall_status = 'CRITICAL'
    ) AS critical_checks,

    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE overall_status = 'HEALTHY'
        )
        / NULLIF(COUNT(*), 0),
        2
    ) AS healthy_percentage,

    MAX(checked_at) AS last_checked_at

FROM pipeline_health_history
GROUP BY pipeline_name;
