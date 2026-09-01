 
-- ============================================================
-- DATA ARCHITECTURE Sprint: DAY 26 MILESTONE MIGRATION
-- Database Schema Hardening & Relational Constraints Blueprint
-- ============================================================

-- 📍 1. HARDEN SITE COORDINATES & UNIQUENESS CONSTRAINTS
ALTER TABLE sites
ADD CONSTRAINT chk_sites_latitude
CHECK (
    latitude IS NULL
    OR latitude BETWEEN -90 AND 90
);

ALTER TABLE sites
ADD CONSTRAINT chk_sites_longitude
CHECK (
    longitude IS NULL
    OR longitude BETWEEN -180 AND 180
);

ALTER TABLE sites
ADD CONSTRAINT chk_sites_status
CHECK (
    status IN (
        'Active',
        'Inactive',
        'Maintenance',
        'Planned'
    )
);

ALTER TABLE sites
ADD CONSTRAINT chk_sites_site_type
CHECK (
    site_type IN (
        'Data Center',
        'Macro Tower',
        'Micro Cell',
        'Rooftop Hub'
    )
);

ALTER TABLE sites
ADD CONSTRAINT uq_sites_name_district
UNIQUE (site_name, district);


-- 🛠️ 2. HARDEN HARDWARE ASSET COMPLIANCE RESTRAINTS
ALTER TABLE equipment
ADD CONSTRAINT chk_equipment_status
CHECK (
    status IN (
        'Active',
        'Inactive',
        'Maintenance',
        'Retired'
    )
);


-- 📊 3. HARDEN CORE TELEMETRY PERFORMANCE FACT RANGES
ALTER TABLE measurements
ADD CONSTRAINT chk_measurements_traffic
CHECK (
    traffic_mb IS NULL
    OR traffic_mb >= 0
);

ALTER TABLE measurements
ADD CONSTRAINT chk_measurements_latency
CHECK (
    latency_ms IS NULL
    OR latency_ms >= 0
);

ALTER TABLE measurements
ADD CONSTRAINT chk_measurements_packet_loss
CHECK (
    packet_loss_pct IS NULL
    OR packet_loss_pct BETWEEN 0 AND 100
);

ALTER TABLE measurements
ADD CONSTRAINT chk_measurements_availability
CHECK (
    availability_pct IS NULL
    OR availability_pct BETWEEN 0 AND 100
);


-- 🚨 4. HARDEN INCIDENT DISRUPTION METRIC RULES
ALTER TABLE incidents
ADD CONSTRAINT chk_incidents_severity
CHECK (
    severity IN (
        'Low', 'Medium', 'High', 'Critical',
        'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    )
);

ALTER TABLE incidents
ADD CONSTRAINT chk_incidents_status
CHECK (
    status IN (
        'Open', 'In Progress', 'Resolved', 'Closed',
        'OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'
    )
);

ALTER TABLE incidents
ADD CONSTRAINT chk_incidents_time
CHECK (
    end_time IS NULL
    OR end_time >= start_time
);
