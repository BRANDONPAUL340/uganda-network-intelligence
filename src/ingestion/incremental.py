import logging
from sqlalchemy import text
from src.config import PIPELINE_NAME
from src.database import engine
from src.ingestion.watermark import update_watermark

logger = logging.getLogger(__name__)


def get_latest_raw_id():
    """Queries the RAW landing tier sequence catalog to extract the maximum primary key index [INDEX]."""
    query = text("""
        SELECT COALESCE(MAX(raw_measurement_id), 0)
        FROM raw_measurements;
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar_one()


def advance_processing_watermark(source_name="measurements"):
    """
    Orchestration Hook: Safely advances the watermark state boundary registry to match the latest raw primary key.
    Ensures that high-watermark updates are decoupled from insert processes [INDEX].
    """
    latest_id = get_latest_raw_id()
    logger.info(f"Advancing orchestrator high-watermark state for source=[{source_name}] to last_id={latest_id}...")

    update_watermark(
        PIPELINE_NAME,
        source_name,
        latest_id,
    )

    logger.info("Orchestration watermark state successfully locked onto disk.")
    return latest_id
