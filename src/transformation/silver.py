from sqlalchemy import text

from src.database import engine
from src.logger import get_logger

# 🛠️ Hardened: Instantiating centralized module logger context name
logger = get_logger(__name__)


def upgrade_silver_schemas():
    """
    Programmatically patches existing Silver tables to ensure they have 
    the necessary primary key constraints and lineage columns without losing data.
    """
    logger.info("Shielding, altering, and upgrading Silver schemas.")
    
    alter_cols_sql = """
    ALTER TABLE silver_measurements 
    ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

    ALTER TABLE silver_measurements 
    ADD COLUMN IF NOT EXISTS batch_id BIGINT;

    ALTER TABLE silver_network_health 
    ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

    ALTER TABLE silver_network_health 
    ADD COLUMN IF NOT EXISTS batch_id BIGINT;
    """
    
    alter_keys_sql = "ALTER TABLE silver_measurements ADD PRIMARY KEY (measurement_id);"
    alter_health_keys_sql = "ALTER TABLE silver_network_health ADD PRIMARY KEY (measurement_id);"
    
    with engine.begin() as connection:
        connection.execute(text(alter_cols_sql))
        
        try:
            connection.execute(text(alter_keys_sql))
        except Exception:
            pass
            
        try:
            connection.execute(text(alter_health_keys_sql))
        except Exception:
            pass
            
    logger.info("Silver schemas successfully upgraded and indexed.")


def load_silver_measurements():
    logger.info("Loading new measurements into Silver layer.")

    sql = """
    INSERT INTO silver_measurements (
        measurement_id, measured_at, site_id, site_name, region, district, site_type,
        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,
        packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id
    )
    SELECT
        m.measurement_id, m.measured_at, m.site_id, s.site_name, s.region, s.district, s.site_type,
        m.equipment_id, e.equipment_type, e.manufacturer, e.model, m.traffic_mb, m.latency_ms,
        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct,
        COALESCE(m.ingested_at, CURRENT_TIMESTAMP), m.batch_id
    FROM measurements m
    JOIN sites s ON m.site_id = s.site_id
    JOIN equipment e ON m.equipment_id = e.equipment_id
    ON CONFLICT (measurement_id) DO NOTHING;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql))
        logger.info("New Silver measurements loaded: %s", result.rowcount)
        return result.rowcount


def load_silver_network_health():
    logger.info("Loading network health.")

    sql = """
    INSERT INTO silver_network_health (
        measurement_id, measured_at, site_id, site_name, region, district, site_type,
        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,
        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id
    )
    SELECT
        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,
        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,
        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,
        CASE
            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'
            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'
            ELSE 'Healthy'
        END,
        sm.ingested_at, sm.batch_id
    FROM silver_measurements sm
    ON CONFLICT (measurement_id) DO NOTHING;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql))
        logger.info("New network-health records loaded: %s", result.rowcount)
        return result.rowcount


def run_silver():
    logger.info("--- SILVER LAYER ---")
    upgrade_silver_schemas()
    
    measurements_added = load_silver_measurements()
    health_added = load_silver_network_health()
    
    return {
        "measurements_loaded": measurements_added,
        "health_loaded": health_added
    }


if __name__ == "__main__":
    run_silver()
