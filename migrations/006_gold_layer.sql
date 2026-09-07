-- ============================================
-- Migration 006
-- Uganda Network Intelligence
-- Gold Analytical Slices Tier Data Contracts
-- ============================================

CREATE TABLE IF NOT EXISTS gold_site_daily_performance (
    site_id INTEGER NOT NULL,
    site_name VARCHAR(100),
    region VARCHAR(50),
    district VARCHAR(100),
    measurement_date DATE NOT NULL,
    measurement_count INTEGER,
    avg_traffic_mb DECIMAL(12,2),
    avg_latency_ms DECIMAL(10,2),
    avg_packet_loss_pct DECIMAL(5,2),
    avg_signal_strength_dbm DECIMAL(6,2),
    avg_availability_pct DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (site_id, measurement_date)
);

CREATE TABLE IF NOT EXISTS gold_equipment_health (
    equipment_id INTEGER PRIMARY KEY,
    equipment_type VARCHAR(50),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    measurement_count INTEGER,
    avg_latency_ms DECIMAL(10,2),
    avg_packet_loss_pct DECIMAL(5,2),
    avg_signal_strength_dbm DECIMAL(6,2),
    avg_availability_pct DECIMAL(5,2),
    health_status VARCHAR(20),
    record_count INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
