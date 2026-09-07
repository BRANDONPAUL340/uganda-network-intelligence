-- ============================================
-- Migration 005
-- Uganda Network Intelligence
-- Silver Enriched Tier Data Contracts
-- ============================================

CREATE TABLE IF NOT EXISTS silver_measurements (
    measurement_id BIGINT PRIMARY KEY,
    measured_at TIMESTAMP NOT NULL,
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
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver_network_health (
    measurement_id BIGINT PRIMARY KEY,
    measured_at TIMESTAMP NOT NULL,
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
    health_status VARCHAR(20),
    ingested_at TIMESTAMP,
    batch_id INTEGER,
    run_id INTEGER,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
