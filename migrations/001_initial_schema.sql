-- ============================================
-- Migration 001
-- Uganda Network Intelligence
-- Initial database schema
-- ============================================

CREATE TABLE IF NOT EXISTS sites (
    site_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    district VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    site_type VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS equipment (
    equipment_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_id INTEGER NOT NULL,
    equipment_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    installation_date DATE,
    status VARCHAR(20) NOT NULL,

    CONSTRAINT fk_equipment_site
        FOREIGN KEY (site_id)
        REFERENCES sites(site_id)
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    equipment_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    measured_at TIMESTAMP NOT NULL,
    traffic_mb DECIMAL(12,2),
    latency_ms DECIMAL(10,2),
    packet_loss_pct DECIMAL(5,2),
    signal_strength_dbm DECIMAL(6,2),
    availability_pct DECIMAL(5,2),

    CONSTRAINT fk_measurement_equipment
        FOREIGN KEY (equipment_id)
        REFERENCES equipment(equipment_id),

    CONSTRAINT fk_measurement_site
        FOREIGN KEY (site_id)
        REFERENCES sites(site_id)
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_id INTEGER NOT NULL,
    equipment_id INTEGER,
    incident_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    description TEXT,

    CONSTRAINT fk_incident_site
        FOREIGN KEY (site_id)
        REFERENCES sites(site_id),

    CONSTRAINT fk_incident_equipment
        FOREIGN KEY (equipment_id)
        REFERENCES equipment(equipment_id)
);
-- =========================================================
-- METADATA LOGGING SUB-TIER SCHEMA FOR PIPELINE ACCOUNTING
-- =========================================================
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    error_message TEXT
);
