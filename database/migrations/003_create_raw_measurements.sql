-- Migration: 003
-- Description: Create raw_measurements landing table and associated optimization index trees

-- ----------------------------------------------------------------------------
-- 1. MATERIALIZE RAW INGESTION BOUNDARY TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_measurements (
    raw_measurement_id BIGSERIAL PRIMARY KEY,
    
    -- Immutable core business metrics
    measurement_id BIGINT NOT NULL,
    site_id BIGINT NOT NULL,
    equipment_id BIGINT NOT NULL,
    measurement_date DATE NOT NULL,
    traffic_mb NUMERIC(14,2),
    latency_ms NUMERIC(10,2),
    packet_loss_pct NUMERIC(6,2),
    signal_strength_dbm NUMERIC(8,2),
    availability_pct NUMERIC(6,2),
    
    -- Extensible ingestion micro-telemetry metrics
    source_file VARCHAR(255),
    ingestion_run_id BIGINT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Security constraints & reference integrity boundaries
    CONSTRAINT uq_raw_measurement_source
        UNIQUE (measurement_id, source_file),

    CONSTRAINT fk_raw_ingestion_run
        FOREIGN KEY (ingestion_run_id)
        REFERENCES pipeline_runs(run_id),

    -- Soft structural check rules (Accept rough values but check boundary format metrics)
    CONSTRAINT chk_raw_traffic
        CHECK (traffic_mb IS NULL OR traffic_mb >= 0),

    CONSTRAINT chk_raw_latency
        CHECK (latency_ms IS NULL OR latency_ms >= 0),

    CONSTRAINT chk_raw_packet_loss
        CHECK (packet_loss_pct IS NULL OR packet_loss_pct BETWEEN 0 AND 100),

    CONSTRAINT chk_raw_availability
        CHECK (availability_pct IS NULL OR availability_pct BETWEEN 0 AND 100)
);

-- ----------------------------------------------------------------------------
-- 2. DEPLOY HIGH-PERFORMANCE OPTIMIZATION INDEX TREES
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_raw_measurements_measurement_id
    ON raw_measurements(measurement_id);

CREATE INDEX IF NOT EXISTS idx_raw_measurements_ingestion_run
    ON raw_measurements(ingestion_run_id);

CREATE INDEX IF NOT EXISTS idx_raw_measurements_ingested_at
    ON raw_measurements(ingested_at);
