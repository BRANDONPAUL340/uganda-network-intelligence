import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def reprocess_quarantined_record(quarantine_id):
    """
    Extracts a quarantined record, updates its retry counters, re-validates
    its fields against master dimension indices, and promotes it to Silver upon success [INDEX].
    """
    logger.info(f"Initializing transactional replay attempt for quarantine_id={quarantine_id}...")

    select_query = text("""
        SELECT
            q.quarantine_id,
            q.raw_measurement_id,
            q.status,
            r.measurement_id,
            r.site_id,
            r.equipment_id,
            r.measurement_date,
            r.traffic_mb,
            r.latency_ms,
            r.packet_loss_pct,
            r.signal_strength_dbm,
            r.availability_pct
        FROM quarantined_measurements q
        JOIN raw_measurements r
            ON r.raw_measurement_id = q.raw_measurement_id
        WHERE q.quarantine_id = :quarantine_id;
    """)

    with engine.begin() as connection:
        record = connection.execute(
            select_query,
            {"quarantine_id": quarantine_id},
        ).mappings().first()

        if record is None:
            raise ValueError(
                f"Quarantine record {quarantine_id} was not found"
            )

        if record["status"] == "REPROCESSED":
            logger.info(f"Skipping: quarantine_id={quarantine_id} has already been resolved.")
            return {
                "status": "ALREADY_REPROCESSED",
                "quarantine_id": quarantine_id,
            }

        # 🚦 Check validation parameters dynamically
        validation_query = text("""
            SELECT
                :measurement_id IS NOT NULL
                AND :site_id IS NOT NULL
                AND :equipment_id IS NOT NULL
                AND EXISTS (
                    SELECT 1
                    FROM sites
                    WHERE site_id = :site_id
                )
                AND EXISTS (
                    SELECT 1
                    FROM equipment
                    WHERE equipment_id = :equipment_id
                )
                AND (:traffic_mb IS NULL OR :traffic_mb >= 0)
                AND (:latency_ms IS NULL OR :latency_ms >= 0)
                AND (
                    :packet_loss_pct IS NULL
                    OR :packet_loss_pct BETWEEN 0 AND 100
                )
                AND (
                    :availability_pct IS NULL
                    OR :availability_pct BETWEEN 0 AND 100
                )
            AS is_valid;
        """)

        valid = connection.execute(
            validation_query,
            dict(record),
        ).scalar_one()

        # 📈 Increment processing counter
        update_attempt = text("""
            UPDATE quarantined_measurements
            SET reprocessing_attempts = reprocessing_attempts + 1
            WHERE quarantine_id = :quarantine_id;
        """)

        connection.execute(
            update_attempt,
            {"quarantine_id": quarantine_id},
        )

        if not valid:
            logger.warning(f"Replay failed: quarantine_id={quarantine_id} breaks data contracts.")
            connection.execute(
                text("""
                    UPDATE quarantined_measurements
                    SET
                        status = 'REPROCESS_FAILED',
                        resolution_notes = 'Record still fails validation'
                    WHERE quarantine_id = :quarantine_id;
                """),
                {"quarantine_id": quarantine_id},
            )

            return {
                "status": "REPROCESS_FAILED",
                "quarantine_id": quarantine_id,
            }

        # 🚀 Success: Promote clean data record straight to Silver
        connection.execute(
            text("""
                INSERT INTO silver_measurements (
                    measurement_id,
                    site_id,
                    equipment_id,
                    measurement_date,
                    traffic_mb,
                    latency_ms,
                    packet_loss_pct,
                    signal_strength_dbm,
                    availability_pct
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
                    :availability_pct
                )
                ON CONFLICT (measurement_id)
                DO NOTHING;
            """),
            dict(record),
        )

        # 📝 Record resolution logs to disk
        connection.execute(
            text("""
                UPDATE quarantined_measurements
                SET
                    status = 'REPROCESSED',
                    reprocessed_at = CURRENT_TIMESTAMP,
                    resolution_notes = 'Record passed validation and was promoted to Silver'
                WHERE quarantine_id = :quarantine_id;
            """),
            {"quarantine_id": quarantine_id},
        )

        logger.info(f"Replay successful: quarantine_id={quarantine_id} promoted to Silver tier.")
        return {
            "status": "REPROCESSED",
            "quarantine_id": quarantine_id,
        }
