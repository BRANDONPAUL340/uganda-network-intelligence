-- Migration: 015
-- Description: Deploy pipeline_health_history persistent snapshot table layer [INDEX]

CREATE TABLE IF NOT EXISTS pipeline_health_history (
    health_id BIGSERIAL PRIMARY KEY,

    pipeline_name VARCHAR(255) NOT NULL,

    checked_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    overall_status VARCHAR(20) NOT NULL,

    database_status VARCHAR(20) NOT NULL,

    pipeline_run_status VARCHAR(20) NOT NULL,

    pipeline_stage_status VARCHAR(20) NOT NULL,

    alert_count INTEGER NOT NULL DEFAULT 0,

    critical_alert_count INTEGER NOT NULL DEFAULT 0,

    warning_alert_count INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT chk_health_overall_status
        CHECK (
            overall_status IN (
                'HEALTHY',
                'WARNING',
                'CRITICAL',
                'UNKNOWN'
            )
        ),

    CONSTRAINT chk_health_database_status
        CHECK (
            database_status IN (
                'HEALTHY',
                'WARNING',
                'CRITICAL',
                'UNKNOWN'
            )
        ),

    CONSTRAINT chk_health_pipeline_run_status
        CHECK (
            pipeline_run_status IN (
                'HEALTHY',
                'WARNING',
                'CRITICAL',
                'UNKNOWN'
            )
        ),

    CONSTRAINT chk_health_stage_status
        CHECK (
            pipeline_stage_status IN (
                'HEALTHY',
                'WARNING',
                'CRITICAL',
                'UNKNOWN'
            )
        ),

    CONSTRAINT chk_health_alert_count
        CHECK (alert_count >= 0),

    CONSTRAINT chk_health_critical_alert_count
        CHECK (critical_alert_count >= 0),

    CONSTRAINT chk_health_warning_alert_count
        CHECK (warning_alert_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_pipeline_health_history_pipeline
    ON pipeline_health_history(pipeline_name);

CREATE INDEX IF NOT EXISTS idx_pipeline_health_history_checked_at
    ON pipeline_health_history(checked_at);

CREATE INDEX IF NOT EXISTS idx_pipeline_health_history_status
    ON pipeline_health_history(overall_status);
