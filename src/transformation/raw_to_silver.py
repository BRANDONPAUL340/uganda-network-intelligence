import logging
from sqlalchemy import text
from src.database import engine
from src.quality.quarantine import quarantine_invalid_records

logger = logging.getLogger(__name__)


def promote_raw_to_silver():
    """
    Promotes valid RAW measurements into the current Silver model.

    The workflow:
    1. Quarantines invalid RAW records.
    2. Promotes only valid, non-quarantined records.
    3. Skips measurements already present in Silver.
    4. Returns standardized accounting metrics.
    """
    logger.info("Initializing unified raw promotion workflow step pass...")

    # Step 1: isolate invalid RAW records
    quarantine_count = quarantine_invalid_records()

    logger.info(
        "Anomaly isolation pass complete | records_quarantined=%s",
        quarantine_count,
    )

    # Step 2: promote clean RAW records into the current Silver model
    query = text("""
        INSERT INTO silver_measurements (
            measurement_id,
            measured_at,
            site_id,
            site_name,
            region,
            district,
            site_type,
            equipment_id,
            equipment_type,
            manufacturer,
            model,
            traffic_mb,
            latency_ms,
            packet_loss_pct,
            signal_strength_dbm,
            availability_pct,
            ingested_at,
            batch_id,
            source_record_id,
            run_id
        )
        SELECT
            r.measurement_id,
            r.measurement_date::timestamp,
            s.site_id,
            s.site_name,
            s.region,
            s.district,
            s.site_type,
            e.equipment_id,
            e.equipment_type,
            e.manufacturer,
            e.model,
            r.traffic_mb,
            r.latency_ms,
            r.packet_loss_pct,
            r.signal_strength_dbm,
            r.availability_pct,
            r.ingested_at::timestamp,
            r.ingestion_batch_id,
            CONCAT(r.measurement_id, ':', r.source_file),
            r.ingestion_run_id
        FROM raw_measurements r
        JOIN sites s
            ON s.site_id = r.site_id
        JOIN equipment e
            ON e.equipment_id = r.equipment_id
        WHERE r.measurement_id IS NOT NULL

          AND NOT EXISTS (
              SELECT 1
              FROM silver_measurements sm
              WHERE sm.measurement_id = r.measurement_id
          )

          AND NOT EXISTS (
              SELECT 1
              FROM quarantined_measurements q
              WHERE q.raw_measurement_id = r.raw_measurement_id
          );
    """)

    with engine.begin() as connection:
        result = connection.execute(query)
        promoted_count = result.rowcount

    logger.info(
        "Promotion pass complete | records_promoted=%s",
        promoted_count,
    )

    return {
        "records_loaded": promoted_count,
        "records_quarantined": quarantine_count,
    }