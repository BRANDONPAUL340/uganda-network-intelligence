-- Migration: 020
-- Description: Create pipeline_stage_summary macro dashboard view

CREATE OR REPLACE VIEW pipeline_stage_summary AS
SELECT
    stage_name,

    COUNT(*) AS total_executions,

    COUNT(*) FILTER (
        WHERE status = 'SUCCESS'
    ) AS successful_executions,

    COUNT(*) FILTER (
        WHERE status = 'FAILED'
    ) AS failed_executions,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status = 'SUCCESS'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS success_rate,

    ROUND(
        AVG(
            EXTRACT(
                EPOCH FROM (completed_at - started_at)
            )
        )::numeric,
        2
    ) AS average_duration_seconds,

    COALESCE(
        SUM(records_read),
        0
    ) AS total_records_read,

    COALESCE(
        SUM(records_inserted),
        0
    ) AS total_records_inserted,

    COALESCE(
        SUM(records_rejected),
        0
    ) AS total_records_rejected,

    COALESCE(
        SUM(records_skipped),
        0
    ) AS total_records_skipped

FROM pipeline_stage_runs

GROUP BY stage_name;