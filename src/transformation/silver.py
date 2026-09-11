import logging
from sqlalchemy import text
from src.database import engine
from src.config import (
    CRITICAL_AVAILABILITY_PCT,
    CRITICAL_PACKET_LOSS_PCT,
    CRITICAL_LATENCY_MS,
    WARNING_AVAILABILITY_PCT,
    WARNING_PACKET_LOSS_PCT,
    WARNING_LATENCY_MS,
)

# Instantiate package-level logging context handle wrapper
logger = logging.getLogger(__name__)


def upgrade_silver_schemas():
    """
    Creates and hardens the schema structures for the Silver data tier,
    ensuring full support for advanced denormalized performance attributes.
    """
    logger.info("Shielding, altering, and upgrading Silver schemas...")
    
    measurements_sql = """
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
    """
    
    health_sql = """
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
    """
    
    with engine.begin() as connection:
        connection.execute(text(measurements_sql))
        connection.execute(text(health_sql))


def load_silver_measurements():
    """
    Transforms raw staging data and loads it into the silver_measurements fact tier,
    denormalizing site and equipment attributes into a single wide model.
    """
    print("Loading new measurements into Silver...")
    logger.info("Executing denormalized insert into silver_measurements fact tier...")

    sql = """
    INSERT INTO silver_measurements (
        measurement_id, measured_at, site_id, site_name, region, district, site_type,
        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,
        packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at
    )
    SELECT 
        m.measurement_id, m.measured_at, s.site_id, s.site_name, s.region, s.district, s.site_type,
        e.equipment_id, e.equipment_type, e.manufacturer, e.model, m.traffic_mb, m.latency_ms,
        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct, CURRENT_TIMESTAMP
    FROM measurements m
    JOIN sites s ON m.site_id = s.site_id
    JOIN equipment e ON m.equipment_id = e.equipment_id
    ON CONFLICT (measurement_id) DO NOTHING;
    """
    with engine.begin() as connection:
        result = connection.execute(text(sql))
        records_loaded = result.rowcount
        
        print(f"New Silver measurements loaded: {records_loaded}")
        logger.info(f"Silver measurements tier populated | records_loaded={records_loaded}")
        return records_loaded


def load_silver_network_health(latest_batch_id=3, run_id=112):
    """
    Computes an operational network health index metric out of clean raw fact attributes,
    supporting incoming batch_id, run_id, and dynamic parameter thresholds.
    """
    logger.info("Executing operational health index calculations for silver_network_health...")
    sql = """
    INSERT INTO silver_network_health (
        measurement_id, measured_at, site_id, site_name, region, district, site_type,
        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,
        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id
    )
    SELECT 
        sm.measurement_id, sm.measured_at, sm.site_id, sm.site_name, sm.region, sm.district, sm.site_type,
        sm.equipment_id, sm.equipment_type, sm.manufacturer, sm.model, sm.traffic_mb, sm.latency_ms,
        sm.packet_loss_pct, sm.signal_strength_dbm, sm.availability_pct,
        CASE 
            WHEN sm.availability_pct < :critical_availability 
              OR sm.packet_loss_pct > :critical_packet_loss 
              OR sm.latency_ms > :critical_latency 
            THEN 'Critical'
            
            WHEN sm.availability_pct < :warning_availability 
              OR sm.packet_loss_pct > :warning_packet_loss 
              OR sm.latency_ms > :warning_latency 
            THEN 'Warning'
            
            ELSE 'Healthy'
        END AS health_status,
        CURRENT_TIMESTAMP, :batch_id, :run_id
    FROM silver_measurements sm
    ON CONFLICT (measurement_id) DO NOTHING;
    """
    with engine.begin() as connection:
        result = connection.execute(
            text(sql), 
            {
                "batch_id": latest_batch_id, 
                "run_id": run_id,
                "critical_availability": CRITICAL_AVAILABILITY_PCT,
                "critical_packet_loss": CRITICAL_PACKET_LOSS_PCT,
                "critical_latency": CRITICAL_LATENCY_MS,
                "warning_availability": WARNING_AVAILABILITY_PCT,
                "warning_packet_loss": WARNING_PACKET_LOSS_PCT,
                "warning_latency": WARNING_LATENCY_MS,
            }
        )
        records_loaded = result.rowcount
        
        print(f"New network-health records loaded: {records_loaded}")
        logger.info(f"Silver network health profiling completed | records_loaded={records_loaded}")
        return records_loaded


def run_silver(run_id=112):
    """
    Orchestrates the entire Silver layer transformation sweep.
    Returns the count of newly processed metrics to the main pipeline.
    """
    print("\n--- SILVER LAYER ---")
    upgrade_silver_schemas()

    # Interlock metrics tracking counters from row modifications
    measurement_records = load_silver_measurements()
    
    # Execute downstream operational health evaluations
    load_silver_network_health(latest_batch_id=3, run_id=run_id)
    
    print(f"Total Silver records processed: {measurement_records}")
    logger.info(f"Silver transformation stage complete | tracking_delta={measurement_records}")
    return measurement_records
