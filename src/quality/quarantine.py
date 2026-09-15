import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def quarantine_invalid_records():
    """
    Evaluates records inside the RAW landing layer against data platform contracts.
    Identifies anomalies, attaches failure tags, and transactionally routes them
    to the quarantined_measurements vault.
    """
    logger.info("Initializing high-performance anomaly isolation pass: [RAW -> QUARANTINE]...")
    
    query = text("""
        INSERT INTO quarantined_measurements (
            raw_measurement_id,
            measurement_id,
            rejection_reason,
            ingestion_batch_id,
            pipeline_run_id
        )
        SELECT
            r.raw_measurement_id,
            r.measurement_id,
            CASE
                WHEN r.measurement_id IS NULL
                    THEN 'missing_measurement_id'

                WHEN r.site_id IS NULL
                    THEN 'missing_site_id'

                WHEN NOT EXISTS (
                    SELECT 1
                    FROM sites s
                    WHERE s.site_id = r.site_id
                )
                    THEN 'invalid_site_reference'

                WHEN r.equipment_id IS NULL
                    THEN 'missing_equipment_id'

                WHEN NOT EXISTS (
                    SELECT 1
                    FROM equipment e
                    WHERE e.equipment_id = r.equipment_id
                )
                    THEN 'invalid_equipment_reference'

                WHEN r.traffic_mb < 0
                    THEN 'invalid_traffic'

                WHEN r.latency_ms < 0
                    THEN 'invalid_latency'

                WHEN r.packet_loss_pct NOT BETWEEN 0 AND 100
                    THEN 'invalid_packet_loss'

                WHEN r.availability_pct NOT BETWEEN 0 AND 100
                    THEN 'invalid_availability'

                ELSE NULL
            END AS rejection_reason,

            r.ingestion_batch_id,
            r.ingestion_run_id

        FROM raw_measurements r

        WHERE
            r.measurement_id IS NULL

            OR r.site_id IS NULL
            OR NOT EXISTS (
                SELECT 1
                FROM sites s
                WHERE s.site_id = r.site_id
            )

            OR r.equipment_id IS NULL
            OR NOT EXISTS (
                SELECT 1
                FROM equipment e
                WHERE e.equipment_id = r.equipment_id
            )

            OR r.traffic_mb < 0
            OR r.latency_ms < 0
            OR r.packet_loss_pct NOT BETWEEN 0 AND 100
            OR r.availability_pct NOT BETWEEN 0 AND 100

        -- 🔒 Idempotency Protection: Drops duplicate violations safely
        ON CONFLICT (raw_measurement_id, rejection_reason)
        DO NOTHING;
    """)

    with engine.begin() as connection:
        result = connection.execute(query)
        quarantined_count = result.rowcount
        logger.info(f"RAW to QUARANTINE anomaly isolation pass complete. Quarantined rows: {quarantined_count}")
        return quarantined_count
