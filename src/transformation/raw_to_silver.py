import logging
from sqlalchemy import text
from src.database import engine
from src.config import PIPELINE_NAME
from src.quality.quarantine import quarantine_invalid_records
from src.ingestion.watermark import get_watermark, advance_watermark

logger = logging.getLogger(__name__)


def get_new_raw_measurements(source_name="measurements"):
    """
    Diagnostic Delta Extractor Module: Queries the raw landing tier catalog.
    Extracts *only* rows that arrived after the watermark checkpoint checkpoint [INDEX].
    """
    last_id = get_watermark(PIPELINE_NAME, source_name)
    logger.info(f"Extracting new delta tracks above high-watermark pointer: last_id={last_id}")

    query = text("""
        SELECT
            raw_measurement_id,
            measurement_id,
            site_id,
            equipment_id,
            measurement_date,
            traffic_mb,
            latency_ms,
            packet_loss_pct,
            signal_strength_dbm,
            availability_pct
        FROM raw_measurements
        WHERE raw_measurement_id > :last_id
        ORDER BY raw_measurement_id;
    """)

    with engine.connect() as connection:
        rows = connection.execute(query, {"last_id": last_id}).mappings().all()

    logger.info(f"Delta sweep complete. Unprocessed rows located: {len(rows)}")
    return rows


def promote_incremental_raw_to_silver(source_name="measurements"):
    """
    Idempotent Incremental Loader: Promotes clean raw data above the watermark.
    Employs 'ON CONFLICT DO NOTHING' to protect destination data layers against rerun duplication bloat [INDEX].
    Intentionally does NOT advance the watermark pointer to keep transaction steps safe [INDEX].
    """
    last_id = get_watermark(PIPELINE_NAME, source_name)
    logger.info(f"Initializing safe idempotent incremental promotion pass above watermark={last_id}")

    # Note: Target maps to 'measured_at' to match your production database schema fields perfectly
    query = text("""
        INSERT INTO silver_measurements (
            measurement_id,
            site_id,
            equipment_id,
            measured_at,
            traffic_mb,
            latency_ms,
            packet_loss_pct,
            signal_strength_dbm,
            availability_pct
        )
        SELECT
            r.measurement_id,
            r.site_id,
            r.equipment_id,
            r.measurement_date,
            r.traffic_mb,
            r.latency_ms,
            r.packet_loss_pct,
            r.signal_strength_dbm,
            r.availability_pct
        FROM raw_measurements r
        WHERE r.raw_measurement_id > :last_id
          AND r.measurement_id IS NOT NULL
          AND EXISTS (
              SELECT 1 FROM sites s WHERE s.site_id = r.site_id
          )
          AND EXISTS (
              SELECT 1 FROM equipment e WHERE e.equipment_id = r.equipment_id
          )
          AND NOT EXISTS (
              SELECT 1 FROM quarantined_measurements q WHERE q.raw_measurement_id = r.raw_measurement_id
          )
        ON CONFLICT (measurement_id)
        DO NOTHING;
    """)

    with engine.begin() as connection:
        result = connection.execute(query, {"last_id": last_id})
        promoted_count = result.rowcount

    logger.info(f"Safe incremental promotion complete. Loaded rows: {promoted_count}")
    return promoted_count


def promote_raw_to_silver():
    """Legacy full-load fallback method for backwards-compatibility checks."""
    quarantine_count = quarantine_invalid_records()
    query = text("""
        INSERT INTO silver_measurements (
            measurement_id, site_id, equipment_id, measured_at,
            traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct
        )
        SELECT
            r.measurement_id, r.site_id, r.equipment_id, r.measurement_date,
            r.traffic_mb, r.latency_ms, r.packet_loss_pct, r.signal_strength_dbm, r.availability_pct
        FROM raw_measurements r
        WHERE r.measurement_id IS NOT NULL
          AND EXISTS (SELECT 1 FROM sites s WHERE s.site_id = r.site_id)
          AND EXISTS (SELECT 1 FROM equipment e WHERE e.equipment_id = r.equipment_id)
          AND NOT EXISTS (SELECT 1 FROM silver_measurements s WHERE s.measurement_id = r.measurement_id)
          AND NOT EXISTS (SELECT 1 FROM quarantined_measurements q WHERE q.raw_measurement_id = r.raw_measurement_id);
    """)
    with engine.begin() as connection:
        result = connection.execute(query)
        return {"records_loaded": result.rowcount, "records_quarantined": quarantine_count}


def promote_new_raw_to_silver(source_name="measurements"):
    """Lineage-advancing incremental load module step."""
    last_id = get_watermark(PIPELINE_NAME, source_name)
    query = text("""
        INSERT INTO silver_measurements (
            measurement_id, site_id, equipment_id, measured_at,
            traffic_mb, latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct
        )
        SELECT
            r.measurement_id, r.site_id, r.equipment_id, r.measurement_date,
            r.traffic_mb, r.latency_ms, r.packet_loss_pct, r.signal_strength_dbm, r.availability_pct
        FROM raw_measurements r
        WHERE r.raw_measurement_id > :last_id
          AND r.measurement_id IS NOT NULL
          AND EXISTS (SELECT 1 FROM sites s WHERE s.site_id = r.site_id)
          AND EXISTS (SELECT 1 FROM equipment e WHERE e.equipment_id = r.equipment_id)
          AND NOT EXISTS (SELECT 1 FROM quarantined_measurements q WHERE q.raw_measurement_id = r.raw_measurement_id)
          AND NOT EXISTS (SELECT 1 FROM silver_measurements s WHERE s.measurement_id = r.measurement_id);
    """)
    with engine.begin() as connection:
        result = connection.execute(query, {"last_id": last_id})
        promoted_count = result.rowcount
    new_last_id_query = text("SELECT COALESCE(MAX(raw_measurement_id), :last_id) FROM raw_measurements WHERE raw_measurement_id > :last_id;")
    with engine.connect() as connection:
        new_last_id = connection.execute(new_last_id_query, {"last_id": last_id}).scalar_one()
    if new_last_id > last_id:
        advance_watermark(PIPELINE_NAME, source_name, new_last_id)
    return {"records_loaded": promoted_count, "previous_watermark": last_id, "new_watermark": new_last_id}
