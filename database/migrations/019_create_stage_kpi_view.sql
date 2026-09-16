-- Migration: 019
-- Description: Create pipeline_stage_kpis per-run granular metrics view

CREATE OR REPLACE VIEW pipeline_stage_kpis AS
SELECT
    run_id,
    stage_name,

    COUNT(*) AS stage_executions,

    COUNT(*) FILTER (
        WHERE status = 'SUCCESS'
    ) AS successful_executions,

    COUNT(*) FILTER (
        WHERE status = 'FAILED'
    ) AS failed_executions,

    COUNT(*) FILTER (
        WHERE status = 'RUNNING'
    ) AS running_executions,

    ROUND(
        AVG(
            EXTRACT(
                EPOCH FROM (completed_at - started_at)
            )
        )::numeric,
        2
    ) AS avg_duration_seconds,

    MAX(records_read) AS max_records_read,

    MAX(records_inserted) AS max_records_inserted,

    MAX(records_rejected) AS max_records_rejected,

    MAX(records_skipped) AS max_records_skipped

FROM pipeline_stage_runs

GROUP BY
    run_id,
    stage_name;