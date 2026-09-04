from sqlalchemy import text

from src.database import engine
from src.logger import get_logger
from src.monitoring.transformation_runs import (
    start_transformation,
    finish_transformation,
)

# Initialize module-level logger instance
logger = get_logger(__name__)


def upgrade_silver_schemas():
    """
    Programmatically patches existing Silver tables to ensure they have 
    the necessary primary key constraints and lineage columns without losing data.
    """
    logger.info("Checking Silver schema")
    
    alter_cols_sql = """
    ALTER TABLE silver_measurements 
    ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS source_record_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS run_id INTEGER;

    ALTER TABLE silver_network_health 
    ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS run_id INTEGER;
    """
    
    with engine.begin() as connection:
        connection.execute(text(alter_cols_sql))
        
        try:
            connection.execute(text("ALTER TABLE silver_measurements ADD PRIMARY KEY (measurement_id);"))
        except Exception:
            logger.warning("Primary key already active on silver_measurements")
            
        try:
            connection.execute(text("ALTER TABLE silver_network_health ADD PRIMARY KEY (measurement_id);"))
        except Exception:
            logger.warning("Primary key already active on silver_network_health")
            
    logger.info("Silver schema upgrade completed")


def get_latest_successful_batch_id():
    """
    Finds the highest successful batch ID registered in our metadata registry.
    """
    sql = """
    SELECT MAX(batch_id)
    FROM source_batches
    WHERE status = 'SUCCESS';
    """
    with engine.begin() as connection:
        return connection.execute(text(sql)).scalar()


def load_silver_measurements(batch_id, run_id):
    """
    Transforms and enriches raw records belonging ONLY to the latest processed data batch.
    Maps the active pipeline run_id to trace record-level provenance.
    """
    if batch_id is None:
        logger.info("No successful source batches found. Skipping Silver measurements load.")
        return 0

    logger.info("Loading new measurements into Silver")

    sql = """
    INSERT INTO silver_measurements (
        measurement_id, source_record_id, measured_at, site_id, site_name, region, district, site_type,
        equipment_id, equipment_type, manufacturer, model, traffic_mb, latency_ms,
        packet_loss_pct, signal_strength_dbm, availability_pct, ingested_at, batch_id, run_id
    )
    SELECT
        m.measurement_id, m.source_record_id, m.measured_at, m.site_id, s.site_name, s.region, s.district, s.site_type,
        m.equipment_id, e.equipment_type, e.manufacturer, e.model, m.traffic_mb, m.latency_ms,
        m.packet_loss_pct, m.signal_strength_dbm, m.availability_pct,
        COALESCE(m.ingested_at, CURRENT_TIMESTAMP), m.batch_id, :run_id
    FROM measurements m
    JOIN sites s ON m.site_id = s.site_id
    JOIN equipment e ON m.equipment_id = e.equipment_id
    WHERE m.batch_id = :batch_id
    ON CONFLICT (measurement_id) DO NOTHING;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql), {"batch_id": batch_id, "run_id": run_id})
        records_loaded = result.rowcount
        logger.info(f"New Silver measurements loaded | records={records_loaded}")
        return records_loaded


def load_silver_network_health(batch_id, run_id):
    """
    Computes features and enriches health status records ONLY for the latest batch.
    Maps the active pipeline run_id to trace record-level provenance.
    """
    if batch_id is None:
        logger.info("No successful source batches found. Skipping Silver health calculation.")
        return 0

    logger.info("Loading network health")

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
            WHEN sm.availability_pct < 95 OR sm.packet_loss_pct > 5 OR sm.latency_ms > 70 THEN 'Critical'
            WHEN sm.availability_pct < 98 OR sm.packet_loss_pct > 2 OR sm.latency_ms > 40 THEN 'Warning'
            ELSE 'Healthy'
        END,
        sm.ingested_at, sm.batch_id, :run_id
    FROM silver_measurements sm
    WHERE sm.batch_id = :batch_id
    ON CONFLICT (measurement_id) DO NOTHING;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql), {"batch_id": batch_id, "run_id": run_id})
        records_loaded = result.rowcount
        logger.info(f"New network-health records loaded | records={records_loaded}")
        return records_loaded


def run_silver(run_id):
    """
    Unified entry point for the Silver layer.
    Accepts run_id and registers a micro-tier audit record inside transformation_runs.
    """
    logger.info("--- SILVER LAYER ---")
    
    # 🚨 1. Register micro-task initiation state
    transformation_run_id = start_transformation(
        run_id=run_id,
        layer="SILVER",
        transformation_name="silver_measurements"
    )

    try:
        upgrade_silver_schemas()
        latest_batch_id = get_latest_successful_batch_id()
        logger.info("Targeting latest successful ingestion batch. batch_id=%s", latest_batch_id)
        
        measurements_loaded = load_silver_measurements(latest_batch_id, run_id)
        health_loaded = load_silver_network_health(latest_batch_id, run_id)
        
        total_processed = measurements_loaded + health_loaded
        
        # 🚨 2. Success Pathway Closeout
        finish_transformation(
            transformation_run_id=transformation_run_id,
            status="SUCCESS",
            records_processed=total_processed
        )
        
        logger.info(
            "Silver layer completed. measurements=%s health=%s",
            measurements_loaded,
            health_loaded
        )

        return {
            "measurements_loaded": measurements_loaded,
            "health_loaded": health_loaded
        }

    except Exception as error:
        # 🚨 3. Failure Pathway Override
        finish_transformation(
            transformation_run_id=transformation_run_id,
            status="FAILED",
            records_processed=0,
            error_message=str(error)
        )
        logger.error(f"Silver transformation module encountered a critical exception: {error}")
        raise


if __name__ == "__main__":
    run_silver(run_id=1)
