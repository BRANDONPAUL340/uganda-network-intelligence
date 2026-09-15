import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def load_raw_measurements(ingestion_run_id, source_file="database/source_measurements"):
    """
    Legacy backwards-compatible staging data loader.
    """
    query = text("""
        INSERT INTO raw_measurements (
            measurement_id, site_id, equipment_id, measurement_date,
            traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm,
            availability_pct, source_file, ingestion_run_id
        )
        SELECT
            measurement_id, site_id, equipment_id, measured_at::DATE,
            traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm,
            availability_pct, :source_file, :ingestion_run_id
        FROM measurements
        ON CONFLICT (measurement_id, source_file) DO NOTHING;
    """)
    with engine.begin() as connection:
        result = connection.execute(query, {"source_file": source_file, "ingestion_run_id": ingestion_run_id})
        return result.rowcount


def load_raw_records(records, ingestion_run_id, source_file, ingestion_batch_id=None):
    """
    Executes an optimized, transactional bulk batch insert of normalized record
    dictionaries straight into the immutable raw data lake boundary layer.
    """
    if not records:
        logger.info("Empty record batch array passed to raw loader. Skipping operation.")
        return 0

    logger.info(f"Preparing database write transaction for {len(records)} records with batch_id={ingestion_batch_id}...")
    
    query = text("""
        INSERT INTO raw_measurements (
            measurement_id,
            site_id,
            equipment_id,
            measurement_date,
            traffic_mb,
            latency_ms,
            packet_loss_pct,
            signal_strength_dbm,
            availability_pct,
            source_file,
            ingestion_run_id,
            ingestion_batch_id
        )
        VALUES (
            :measurement_id,
            :site_id,
            :equipment_id,
            :measurement_date,
            :traffic_mb,
            :latency_ms,
            :packet_loss_pct,
            :signal_strength_dbm,
            :availability_pct,
            :source_file,
            :ingestion_run_id,
            :ingestion_batch_id
        )
        ON CONFLICT (measurement_id, source_file)
        DO NOTHING;
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            [
                {
                    **record,
                    "source_file": source_file,
                    "ingestion_run_id": ingestion_run_id,
                    "ingestion_batch_id": ingestion_batch_id,
                }
                for record in records
            ],
        )
        
        rows_written = result.rowcount
        logger.info(f"Batch write transaction complete. Rows safely committed: {rows_written}")
        return rows_written
