-- ============================================
-- Migration 003
-- Pipeline run summary
-- ============================================

CREATE OR REPLACE VIEW pipeline_run_summary AS
SELECT
    p.run_id,
    p.pipeline_name,
    p.started_at,
    p.completed_at,
    p.current_stage,
    p.status,
    p.records_processed,
    p.duration_seconds,

    COUNT(q.quality_result_id) AS quality_checks,

    COUNT(q.quality_result_id) FILTER (
        WHERE q.status = 'PASS'
    ) AS quality_passed,

    COUNT(q.quality_result_id) FILTER (
        WHERE q.status = 'FAIL'
    ) AS quality_failed,

    COALESCE(
        SUM(q.records_failed),
        0
    ) AS failed_records,

    CASE
        WHEN p.status = 'SUCCESS'
         AND COUNT(q.quality_result_id) FILTER (WHERE q.status = 'FAIL') = 0
        THEN 'HEALTHY'
        WHEN p.status = 'FAILED'
        THEN 'FAILED'
        ELSE 'WARNING'
    END AS pipeline_health,

    MAX(q.table_name) FILTER (
        WHERE q.status = 'FAIL'
    ) AS failed_table,

    MAX(q.check_name) FILTER (
        WHERE q.status = 'FAIL'
    ) AS failed_check

FROM pipeline_runs p
LEFT JOIN data_quality_results q ON p.run_id = q.run_id
GROUP BY
    p.run_id,
    p.pipeline_name,
    p.started_at,
    p.completed_at,
    p.current_stage,
    p.status,
    p.records_processed,
    p.duration_seconds;
