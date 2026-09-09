-- ============================================
-- Migration 004
-- Uganda Network Intelligence
-- Pipeline Run Summary Performance View
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
    EXTRACT(EPOCH FROM (p.completed_at - p.started_at))::NUMERIC(10,3) AS duration_seconds,
    COALESCE(q.quality_checks, 0) AS quality_checks,
    COALESCE(q.quality_passed, 0) AS quality_passed,
    COALESCE(q.quality_failed, 0) AS quality_failed,
    COALESCE(q.critical_failed, 0) AS critical_failed,
    COALESCE(q.warning_failed, 0) AS warning_failed,
    COALESCE(q.failed_records, 0) AS failed_records,
    CASE
        WHEN COALESCE(q.critical_failed, 0) > 0 THEN 'CRITICAL'
        WHEN COALESCE(q.warning_failed, 0) > 0 THEN 'WARNING'
        WHEN p.status = 'FAILED' THEN 'FAILED'
        ELSE 'HEALTHY'
    END AS pipeline_health
FROM pipeline_runs p
LEFT JOIN (
    SELECT
        run_id,
        COUNT(*) AS quality_checks,
        COUNT(*) FILTER (WHERE status = 'PASS') AS quality_passed,
        COUNT(*) FILTER (WHERE status = 'FAIL') AS quality_failed,
        COUNT(*) FILTER (WHERE severity = 'CRITICAL' AND status = 'FAIL') AS critical_failed,
        COUNT(*) FILTER (WHERE severity = 'WARNING' AND status = 'FAIL') AS warning_failed,
        COALESCE(SUM(records_failed), 0) AS failed_records
    FROM data_quality_results
    GROUP BY run_id
) q ON p.run_id = q.run_id;
