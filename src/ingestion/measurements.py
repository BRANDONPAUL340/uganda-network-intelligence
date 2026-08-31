import csv
import hashlib
from pathlib import Path

from sqlalchemy import text

from src.database import engine
from src.logger import get_logger


logger = get_logger(__name__)


# 🛠️ Fixed permanently: Added index [2] to extract the exact project folder path out of the collection
BASE_DIR = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    BASE_DIR
    / "data"
    / "bronze"
    / "network_measurements.csv"
)


def calculate_file_checksum():
    """
    Reads the data file in binary blocks and generates a completely 
    unique SHA-256 fingerprint signature hash for the contents.
    """
    sha256 = hashlib.sha256()

    with SOURCE_FILE.open("rb") as file:

        for chunk in iter(
            lambda: file.read(8192),
            b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def batch_already_processed(checksum):
    """
    Check if exactly this file content hash has already been loaded successfully.
    """
    sql = """
    SELECT batch_id
    FROM source_batches
    WHERE file_checksum = :checksum
      AND status = 'SUCCESS'
    LIMIT 1;
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(sql),
            {
                "checksum": checksum
            }
        )

        return result.scalar()


def start_batch(checksum):
    """
    Log the initialization of a fresh file ingestion batch run ticket.
    """
    sql = """
    INSERT INTO source_batches (
        source_name,
        file_name,
        file_checksum,
        status
    )

    VALUES (
        :source_name,
        :file_name,
        :checksum,
        'RUNNING'
    )

    RETURNING batch_id;
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(sql),
            {
                "source_name": "network_measurements",
                "file_name": SOURCE_FILE.name,
                "checksum": checksum
            }
        )

        return result.scalar()


def finish_batch(
    batch_id,
    records_read,
    records_inserted,
    records_rejected,
    status="SUCCESS",
    error_message=None
):
    """
    Update the source batch metadata log tracking metrics when the job ends.
    """
    sql = """
    UPDATE source_batches

    SET
        records_read = :records_read,
        records_inserted = :records_inserted,
        records_rejected = :records_rejected,
        status = :status,
        completed_at = CURRENT_TIMESTAMP,
        error_message = :error_message

    WHERE batch_id = :batch_id;
    """

    with engine.begin() as connection:

        connection.execute(
            text(sql),
            {
                "batch_id": batch_id,
                "records_read": records_read,
                "records_inserted": records_inserted,
                "records_rejected": records_rejected,
                "status": status,
                "error_message": error_message
            }
        )


def read_measurements():

    logger.info(
        f"Reading measurements from {SOURCE_FILE}"
    )

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Source file not found: {SOURCE_FILE}"
        )

    with SOURCE_FILE.open(
        mode="r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        records = list(reader)

    logger.info(
        f"Read {len(records)} records from source"
    )

    return records


def validate_measurement(record):

    required_fields = [
        "equipment_id",
        "site_id",
        "measured_at",
        "traffic_mb",
        "latency_ms",
        "packet_loss_pct",
        "signal_strength_dbm",
        "availability_pct",
    ]

    for field in required_fields:

        if not record.get(field):
            raise ValueError(
                f"Missing required field: {field}"
            )

    availability = float(
        record["availability_pct"]
    )

    packet_loss = float(
        record["packet_loss_pct"]
    )

    latency = float(
        record["latency_ms"]
    )

    if not 0 <= availability <= 100:
        raise ValueError(
            f"Invalid availability: {availability}"
        )

    if not 0 <= packet_loss <= 100:
        raise ValueError(
            f"Invalid packet loss: {packet_loss}"
        )

    if latency < 0:
        raise ValueError(
            f"Invalid latency: {latency}"
        )


def insert_measurement(record, batch_id):
    """
    Inserts a validated measurement record while explicitly tagging its source data lineage.
    """
    sql = """
    INSERT INTO measurements (
        equipment_id,
        site_id,
        measured_at,
        traffic_mb,
        latency_ms,
        packet_loss_pct,
        signal_strength_dbm,
        availability_pct,
        batch_id
    )

    VALUES (
        :equipment_id,
        :site_id,
        :measured_at,
        :traffic_mb,
        :latency_ms,
        :packet_loss_pct,
        :signal_strength_dbm,
        :availability_pct,
        :batch_id
    )
    ON CONFLICT (
        equipment_id,
        measured_at
    )
    DO NOTHING;
    """

    with engine.begin() as connection:

        result = connection.execute(
            text(sql),
            {
                "equipment_id": int(
                    record["equipment_id"]
                ),
                "site_id": int(
                    record["site_id"]
                ),
                "measured_at": record["measured_at"],
                "traffic_mb": float(
                    record["traffic_mb"]
                ),
                "latency_ms": float(
                    record["latency_ms"]
                ),
                "packet_loss_pct": float(
                    record["packet_loss_pct"]
                ),
                "signal_strength_dbm": float(
                    record["signal_strength_dbm"]
                ),
                "availability_pct": float(
                    record["availability_pct"]
                ),
                "batch_id": batch_id,
            }
        )

        return result.rowcount


def run_ingestion():

    logger.info(
        "Starting measurement ingestion"
    )

    checksum = calculate_file_checksum()

    logger.info(
        f"Source checksum: {checksum}"
    )

    existing_batch = batch_already_processed(
        checksum
    )

    if existing_batch:

        logger.info(
            f"Batch already processed: "
            f"{existing_batch}"
        )

        return {
            "records_read": 0,
            "records_inserted": 0,
            "records_rejected": 0,
            "duplicates": 0,
            "batch_id": existing_batch,
            "skipped": True
        }

    batch_id = start_batch(checksum)

    records = read_measurements()

    inserted = 0
    duplicates = 0
    rejected = 0

    try:

        for record in records:

            try:

                validate_measurement(record)

                # 🔑 Upgraded: Passing the structural batch ticket index through to enforce data lineage tracking
                result = insert_measurement(
                    record,
                    batch_id
                )

                if result == 1:

                    inserted += 1

                else:

                    duplicates += 1

            except Exception as error:

                rejected += 1

                logger.error(
                    f"Rejected record: {error}"
                )

        finish_batch(
            batch_id=batch_id,
            records_read=len(records),
            records_inserted=inserted,
            records_rejected=rejected
        )

    except Exception as error:

        finish_batch(
            batch_id=batch_id,
            records_read=len(records),
            records_inserted=inserted,
            records_rejected=rejected,
            status="FAILED",
            error_message=str(error)
        )

        raise

    logger.info(
        f"Ingestion complete | "
        f"batch={batch_id} | "
        f"read={len(records)} | "
        f"inserted={inserted} | "
        f"duplicates={duplicates} | "
        f"rejected={rejected}"
    )

    return {
        "records_read": len(records),
        "records_inserted": inserted,
        "records_rejected": rejected,
        "duplicates": duplicates,
        "batch_id": batch_id,
        "skipped": False
    }


if __name__ == "__main__":
    run_ingestion()
