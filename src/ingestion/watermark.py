import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def get_watermark(pipeline_name, source_name):
    """
    Looks up the last successfully processed raw_measurement_id boundary mark.
    Returns 0 if no record exists yet for this specific pipeline source target.
    """
    query = text("""
        SELECT last_raw_measurement_id
        FROM processing_watermarks
        WHERE pipeline_name = :pipeline_name
          AND source_name = :source_name;
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "pipeline_name": pipeline_name,
                "source_name": source_name,
            },
        ).scalar_one_or_none()

    return result if result is not None else 0


def update_watermark(pipeline_name, source_name, last_raw_measurement_id):
    """
    Upserts the tracking state watermark for a given pipeline source target block.
    """
    logger.info(f"Upserting processing checkpoint state: {pipeline_name}/{source_name} -> last_id={last_raw_measurement_id}")
    
    query = text("""
        INSERT INTO processing_watermarks (
            pipeline_name,
            source_name,
            last_raw_measurement_id
        )
        VALUES (
            :pipeline_name,
            :source_name,
            :last_raw_measurement_id
        )
        ON CONFLICT (pipeline_name, source_name)
        DO UPDATE SET
            last_raw_measurement_id = EXCLUDED.last_raw_measurement_id,
            updated_at = CURRENT_TIMESTAMP;
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "pipeline_name": pipeline_name,
                "source_name": source_name,
                "last_raw_measurement_id": last_raw_measurement_id,
            },
        )


def advance_watermark(pipeline_name, source_name, processed_raw_measurement_id):
    """
    Safer production wrapper: Explicitly updates the tracking state boundary pointer
    only after the orchestration layer confirms the incremental stage has succeeded completely.
    """
    update_watermark(pipeline_name, source_name, processed_raw_measurement_id)
