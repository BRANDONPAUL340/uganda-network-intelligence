from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize package-level logger instance
logger = get_logger(__name__)


def reject_measurement(record, reason, source_file=None):
    """
    Safely captures and writes an individual anomalous record row into 
    the persistent rejected_measurements ledger table on disk.
    
    Distinguishes new rejections from historically quarantined records via result.rowcount.
    """
    sql = """
    INSERT INTO rejected_measurements (
        source_record_id, equipment_id, site_id, measured_at, traffic_mb,
        latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct,
        rejection_reason, source_file, ingested_at
    )
    VALUES (
        :source_record_id, :equipment_id, :site_id, :measured_at, :traffic_mb,
        :latency_ms, :packet_loss_pct, :signal_strength_dbm, :availability_pct,
        :rejection_reason, :source_file, CURRENT_TIMESTAMP
    )
    ON CONFLICT (source_record_id)
    DO NOTHING;
    """
    with engine.begin() as connection:
        result = connection.execute(
            text(sql),
            {
                "source_record_id": record.get("source_record_id"),
                "equipment_id": record.get("equipment_id"),
                "site_id": record.get("site_id"),
                "measured_at": record.get("measured_at"),
                "traffic_mb": record.get("traffic_mb"),
                "latency_ms": record.get("latency_ms"),
                "packet_loss_pct": record.get("packet_loss_pct"),
                "signal_strength_dbm": record.get("signal_strength_dbm"),
                "availability_pct": record.get("availability_pct"),
                "rejection_reason": reason,
                "source_file": source_file,
            },
        )

        # 📊 Structured Telemetry: Count if a row was actively written vs dropped as duplicate
        if result.rowcount == 1:
            logger.warning(
                "Measurement quarantined | "
                f"source_record_id={record.get('source_record_id')} | "
                f"reason={reason}"
            )
        else:
            logger.info(
                "Rejected record already quarantined | "
                f"source_record_id={record.get('source_record_id')}"
            )


def quarantine_records(rejected_records, source_file=None):
    """
    Orchestrates batch-level routing of multiple corrupt rows into the isolation tier.
    """
    for item in rejected_records:
        reject_measurement(
            record=item["record"],
            reason=item["reason"],
            source_file=source_file,
        )
    logger.info(f"Quarantine completed | records={len(rejected_records)}")
