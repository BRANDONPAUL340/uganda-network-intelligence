import logging
from sqlalchemy import text
from src.config import PIPELINE_NAME
from src.database import engine
from src.ingestion.watermark import get_watermark, update_watermark

logger = logging.getLogger(__name__)

GOLD_STAGE = "GOLD"
GOLD_SOURCE = "silver_measurements"


def get_gold_watermark():
    """Looks up the last successfully processed measurement_id milestone for the GOLD stage [INDEX]."""
    return get_watermark(
        PIPELINE_NAME,
        GOLD_STAGE,
        GOLD_SOURCE,
    )


def get_latest_silver_measurement_id():
    """Queries the Silver staging layer to extract the maximum measurement_id currently present [INDEX]."""
    query = text("""
        SELECT COALESCE(MAX(measurement_id), 0)
        FROM silver_measurements;
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar_one()


def update_gold_watermark():
    """
    Orchestration Hook: Advances the durable GOLD checkpoint state ledger to match 
    the maximum processed primary identifier present in the Silver staging tables [INDEX].
    """
    latest_id = get_latest_silver_measurement_id()
    logger.info(f"Advancing GOLD stage high-watermark state to last_id={latest_id}...")

    update_watermark(
        PIPELINE_NAME,
        GOLD_STAGE,
        GOLD_SOURCE,
        latest_id,
    )

    logger.info("GOLD stage orchestration watermark state successfully locked onto disk.")
    return latest_id
