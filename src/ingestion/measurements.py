import csv
from pathlib import Path

from sqlalchemy import text

from src.database import engine
from src.logger import get_logger


logger = get_logger(__name__)


# Establish root folder reference levels dynamically
BASE_DIR = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    BASE_DIR
    / "data"
    / "bronze"
    / "network_measurements.csv"
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


def insert_measurement(record):

    sql = """
    INSERT INTO measurements (
        equipment_id,
        site_id,
        measured_at,
        traffic_mb,
        latency_ms,
        packet_loss_pct,
        signal_strength_dbm,
        availability_pct
    )

    VALUES (
        :equipment_id,
        :site_id,
        :measured_at,
        :traffic_mb,
        :latency_ms,
        :packet_loss_pct,
        :signal_strength_dbm,
        :availability_pct
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
            }
        )

        return result.rowcount


def run_ingestion():

    logger.info(
        "Starting measurement ingestion"
    )

    records = read_measurements()

    inserted = 0
    duplicates = 0
    rejected = 0

    for record in records:

        try:

            validate_measurement(record)

            result = insert_measurement(record)

            if result == 1:
                inserted += 1

            else:
                duplicates += 1

        except Exception as error:

            rejected += 1

            logger.error(
                f"Rejected record: {error}"
            )

    logger.info(
        f"Ingestion complete | "
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
    }


if __name__ == "__main__":
    run_ingestion()
