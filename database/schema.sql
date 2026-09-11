-- ============================================================================
-- UGANDA NETWORK & SERVICE INTELLIGENCE PLATFORM — MASTER REPRODUCIBLE SCHEMA
-- Database: network_intelligence
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. BASE INGESTION LAYER (Staging Entities)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sites (
    site_id INTEGER PRIMARY KEY,
    site_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    district VARCHAR(100) NOT NULL,
    site_type VARCHAR(30) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS equipment (
    equipment_id INTEGER PRIMARY KEY,
    site_id INTEGER REFERENCES sites(site_id) ON DELETE CASCADE,
    equipment_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    installation_date DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id BIGINT PRIMARY KEY,
    measured_at TIMESTAMPTZ NOT NULL,
    site_id INTEGER REFERENCES sites(site_id) ON DELETE CASCADE,
    equipment_id INTEGER REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    traffic_mb DECIMAL(12,2) CHECK (traffic_mb >= 0),
    latency_ms DECIMAL(10,2) CHECK (latency_ms >= 0),
    packet_loss_pct DECIMAL(5,2) CHECK (packet_loss_pct BETWEEN 0 AND 100),
    signal_strength_dbm DECIMAL(6,2),
    availability_pct DECIMAL(5,2) CHECK (availability_pct BETWEEN 0 AND 100)
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id BIGINT PRIMARY KEY,
    site_id INTEGER REFERENCES sites(site_id) ON DELETE CASCADE,
    equipment_id INTEGER REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ CHECK (end_time >= start_time),
    incident_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL')),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. SILVER TIER (Enriched Wide Models & Classifications)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS silver_measurements (
    measurement_id BIGINT PRIMARY KEY REFERENCES measurements(measurement_id),
    measured_at TIMESTAMPTZ NOT NULL,
    site_id INTEGER NOT NULL,
    site_name VARCHAR(100),
    region VARCHAR(50),
    district VARCHAR(100),
    site_type VARCHAR(30),
    equipment_id INTEGER NOT NULL,
    equipment_type VARCHAR(50),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    traffic_mb DECIMAL(12,2),
    latency_ms DECIMAL(10,2),
    packet_loss_pct DECIMAL(5,2),
    signal_strength_dbm DECIMAL(6,2),
    availability_pct DECIMAL(5,2),
    ingested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver_network_health (
    measurement_id BIGINT PRIMARY KEY REFERENCES measurements(measurement_id),
    measured_at TIMESTAMPTZ NOT NULL,
    site_id INTEGER NOT NULL,
    site_name VARCHAR(100),
    region VARCHAR(50),
    district VARCHAR(100),
    site_type VARCHAR(30),
    equipment_id INTEGER NOT NULL,
    equipment_type VARCHAR(50),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    traffic_mb DECIMAL(12,2),
    latency_ms DECIMAL(10,2),
    packet_loss_pct DECIMAL(5,2),
    signal_strength_dbm DECIMAL(6,2),
    availability_pct DECIMAL(5,2),
    health_status VARCHAR(20) NOT NULL CHECK (health_status IN ('Healthy', 'Warning', 'Critical')),
    ingested_at TIMESTAMPTZ,
    batch_id INTEGER,
    run_id BIGINT,
    inserted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 3. GOLD TIER (Analytical Aggregate Summary Cubes)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold_site_daily_performance (
    site_id INTEGER NOT NULL,
    site_name VARCHAR(100) NOT NULL,
    measurement_date DATE NOT NULL,
    measurement_count INTEGER DEFAULT 0,
    avg_traffic_mb DECIMAL(12,2),
    avg_latency_ms DECIMAL(10,2),
    avg_packet_loss_pct DECIMAL(5,2),
    avg_signal_strength_dbm DECIMAL(6,2),
    avg_availability_pct DECIMAL(5,2),
    PRIMARY KEY (site_id, measurement_date)
);

CREATE TABLE IF NOT EXISTS gold_equipment_health (
    equipment_id INTEGER PRIMARY KEY,
    equipment_type VARCHAR(50),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    measurement_count INTEGER DEFAULT 0,
    avg_latency_ms DECIMAL(10,2),
    avg_packet_loss_pct DECIMAL(5,2),
    avg_availability_pct DECIMAL(5,2),
    health_status VARCHAR(20)
);

-- ----------------------------------------------------------------------------
-- 4. OPERATIONAL TRACKING & TELEMETRY LEDGERS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id BIGSERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING' CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    current_stage VARCHAR(50) NOT NULL,
    records_processed INTEGER DEFAULT 0 CHECK (records_processed >= 0),
    error_message TEXT,
    duration_seconds NUMERIC(10,3) DEFAULT 0.000 CHECK (duration_seconds >= 0)
);

CREATE TABLE IF NOT EXISTS pipeline_stage_runs (
    stage_run_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    stage_name VARCHAR(50) NOT NULL CHECK (stage_name IN ('SILVER', 'QUALITY', 'GOLD')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING' CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    records_processed INTEGER DEFAULT 0 CHECK (records_processed >= 0),
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS pipeline_lineage (
    lineage_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    stage_run_id BIGINT REFERENCES pipeline_stage_runs(stage_run_id) ON DELETE SET NULL,
    source_table VARCHAR(100) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    records_processed INTEGER DEFAULT 0 CHECK (records_processed >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Optimization Index Trees
CREATE INDEX IF NOT EXISTS idx_pipeline_lineage_run_id ON pipeline_lineage(run_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_lineage_stage_run_id ON pipeline_lineage(stage_run_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_pipeline_lineage_relationship ON pipeline_lineage(run_id, stage_run_id, source_table, target_table);
-- ============================================================
-- ADDITIONAL OPERATIONAL MONITORING ENFORCEMENT & RULES
-- ============================================================

-- Stage Tracking Optimization Indexes
CREATE INDEX IF NOT EXISTS idx_pipeline_stage_runs_run_id ON pipeline_stage_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_stage_runs_stage_name ON pipeline_stage_runs(stage_name);
CREATE UNIQUE INDEX IF NOT EXISTS uq_pipeline_stage_run ON pipeline_stage_runs(run_id, stage_name);

-- ----------------------------------------------------------------------------
-- 4b. DATA QUALITY RESULTS LEDGER
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS data_quality_results (
    quality_result_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    check_name VARCHAR(150) NOT NULL,
    status VARCHAR(20) NOT NULL,
    failed_records INTEGER DEFAULT 0,
    severity VARCHAR(20) DEFAULT 'INFO',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_quality_severity 
        CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL'))
);

-- ----------------------------------------------------------------------------
-- 5. DIAGNOSTIC REUSABLE AUDIT VIEWS
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW pipeline_audit_report AS
SELECT
    pr.run_id,
    pr.pipeline_name,
    pr.started_at AS pipeline_started_at,
    pr.completed_at AS pipeline_completed_at,
    CASE WHEN pr.completed_at IS NOT NULL THEN pr.completed_at - pr.started_at ELSE NULL END AS pipeline_duration,
    pr.status AS pipeline_status,
    psr.stage_run_id,
    psr.stage_name,
    psr.started_at AS stage_started_at,
    psr.completed_at AS stage_completed_at,
    CASE WHEN psr.completed_at IS NOT NULL THEN psr.completed_at - psr.started_at ELSE NULL END AS stage_duration,
    psr.status AS stage_status,
    pl.source_table,
    pl.target_table,
    COALESCE(pl.records_processed, pr.records_processed) AS lineage_records_processed,
    pl.created_at AS lineage_created_at
FROM pipeline_runs pr
LEFT JOIN pipeline_stage_runs psr ON pr.run_id = psr.run_id
LEFT JOIN pipeline_lineage pl ON psr.stage_run_id = pl.stage_run_id;

CREATE OR REPLACE VIEW pipeline_operational_metrics AS
SELECT
    r.run_id,
    r.pipeline_name,
    r.pipeline_started_at,
    r.pipeline_completed_at,
    r.pipeline_status,
    r.pipeline_duration,
    EXTRACT(EPOCH FROM r.pipeline_duration) AS pipeline_duration_seconds,
    CASE
        WHEN r.pipeline_duration IS NULL THEN 'UNKNOWN'
        WHEN EXTRACT(EPOCH FROM r.pipeline_duration) <= 60 THEN 'PASS'
        ELSE 'BREACH'
    END AS pipeline_sla_status,
    m.latest_measurement,
    CURRENT_DATE - m.latest_measurement::DATE AS freshness_days,
    CASE
        WHEN m.latest_measurement IS NULL THEN 'UNKNOWN'
        WHEN CURRENT_DATE - m.latest_measurement::DATE <= 1 THEN 'PASS'
        ELSE 'BREACH'
    END AS freshness_status
FROM (
    SELECT DISTINCT run_id, pipeline_name, pipeline_started_at, pipeline_completed_at, pipeline_status, pipeline_duration 
    FROM pipeline_audit_report
) r
CROSS JOIN (
    SELECT MAX(measured_at) AS latest_measurement FROM measurements
) m;
