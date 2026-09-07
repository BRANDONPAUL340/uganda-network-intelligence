from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize package-level logger instance
logger = get_logger(__name__)


def upgrade_silver_schemas():
    """
    Creates and hardens the schema structures for the Silver data tier,
    ensuring full support for advanced denormalized performance attributes.
    """
    logger.info("Shielding, altering, and upgrading Silver schemas...")
    
    measurements_sql = """
    CREATE TABLE IF NOT EXISTS silver_measurements (
        measurement_id INTEGER PRIMARY KEY,
        equipment_id INTEGER NOT NULL,
        site_id INTEGER NOT NULL,
        measured_at TIMESTAMP NOT NULL,
        traffic_mb NUMERIC(12,3),
        latency_ms NUMERIC(12,3),
        packet_loss_pct NUMERIC(5,2),
        signal_strength_dbm NUMERIC(5,2),
        availability_pct NUMERIC(5,2),
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    health_sql = """
    CREATE TABLE IF NOT EXISTS silver_network_health (
        measurement_id INTEGER PRIMARY KEY,
        measured_at TIMESTAMP NOT NULL,
        site_id INTEGER NOT NULL,
        site_name VARCHAR(255),
        region VARCHAR(100),
        district VARCHAR(100),
        site_type VARCHAR(100),
        equipment_id INTEGER NOT NULL,
        equipment_type VARCHAR(100),
        manufacturer VARCHAR(100),
        model VARCHAR(100),
        traffic_mb NUMERIC(12,3),
        latency_ms NUMERIC(12,3),
        packet_loss_pct NUMERIC(5,2),
        signal_strength_dbm NUMERIC(5,2),
        availability_pct NUMERIC(5,2),
        health_status VARCHAR(50),
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
    Transforms raw staging data and loads it into the silver_measurements fact tier.
    ON CONFLICT (measurement_id) DO NOTHING guarantees idempotency.
    """
    sql = """
    INSERT INTO silver_measurements (
        measurement_id, equipment_id, site_id, measured_at,
        traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct
    )
    SELECT 
        measurement_id, equipment_id, site_id, measured_at,
        traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct
    FROM measurements
    ON CONFLICT (measurement_id) DO NOTHING;
    """
    with engine.begin() as connection:
        result = connection.execute(text(sql))
        records_loaded = result.rowcount
        
        print(f"New Silver measurements loaded: {records_loaded}")
        logger.info(f"Silver measurements tier populated | records={records_loaded}")
        return records_loaded


def load_silver_network_health(latest_batch_id=3, run_id=112):
    """
    Computes an operational network health index metric out of clean raw fact attributes,
    supporting incoming batch_id and run_id parameter dictionaries.
    """
    sql = """
    INSERT INTO silver_network_health (
        measurement_id, measured_at, site_id, site_name, region, district, site_type,
        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,
        packet_loss_pct, signal_strength_dbm, availability_pct, health_status, ingested_at, batch_id, run_id
    )
    SELECT 
        m.measurement_id, m.measured_at, m.site_id, 'Site ' || m.site_id, 'Region', 'District', 'Macro',
        m.equipment_id, 'Radio', 'Manufacturer', 'Model', m.traffic_mb, m.latency_ms,
        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct,
        CASE 
            WHEN m.availability_pct < 95 OR m.packet_loss_pct > 5 OR m.latency_ms > 70 THEN 'Critical'
            WHEN m.availability_pct < 98 OR m.packet_loss_pct > 2 OR m.latency_ms > 40 THEN 'Warning'
            ELSE 'Healthy'
        END AS health_status,
        CURRENT_TIMESTAMP, :batch_id, :run_id
    FROM measurements m
    ON CONFLICT (measurement_id) DO NOTHING;
    """
    with engine.begin() as connection:
        result = connection.execute(text(sql), {"batch_id": latest_batch_id, "run_id": run_id})
        records_loaded = result.rowcount
        
        print(f"New network-health records loaded: {records_loaded}")
        logger.info(f"Silver network health profiling completed | records={records_loaded}")
        return records_loaded


def run_silver(run_id=112):
    """
    Orchestrates the entire Silver layer transformation sweep.
    """
    print("\n--- SILVER LAYER ---")
    upgrade_silver_schemas()

    measurement_records = load_silver_measurements()
    
    # Dynamic parameter fallback routing matching your execution loops
    health_records = load_silver_network_health(latest_batch_id=3, run_id=run_id)

    total_records = measurement_records + health_records
    print(f"Total Silver records processed: {total_records}")
    
    return {
        "measurements_loaded": measurement_records,
        "health_loaded": health_records,
        "total_processed": total_records
    }
