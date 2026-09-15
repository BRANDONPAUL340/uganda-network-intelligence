import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def start_ingestion_batch(pipeline_run_id, source_type, source_name):
    """
    Spins up an atomic tracking batch block inside ingestion_batches.
    Enforces perimeter reference integrity back to active pipeline runs.
    Returns the auto-generated bigserial batch_id primary key index.
    """
    logger.info(f"Registering initialization checkpoint for {source_type} batch: [{source_name}]")
    
    query = text("""
        INSERT INTO ingestion_batches (
            pipeline_run_id,
            source_type,
            source_name,
            status
        )
        VALUES (
            :pipeline_run_id,
            :source_type,
            :source_name,
            'RUNNING'
        )
        RETURNING batch_id;
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "pipeline_run_id": pipeline_run_id,
                "source_type": source_type,
                "source_name": source_name,
            },
        )
        batch_id = result.scalar_one()
        logger.info(f"Ingestion batch initialized successfully | batch_id={batch_id}")
        return batch_id


def finish_ingestion_batch(batch_id, status, records_received, records_loaded, error_message=None):
    """
    Finalizes an open tracking batch block. Updates microsecond processing timers,
    row calculation counters, and error states.
    """
    logger.info(f"Closing ingestion batch handle {batch_id} with exit status: [{status}]")
    
    query = text("""
        UPDATE ingestion_batches
        SET
            completed_at = CURRENT_TIMESTAMP,
            status = :status,
            records_received = :records_received,
            records_loaded = :records_loaded,
            error_message = :error_message
        WHERE batch_id = :batch_id;
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "batch_id": batch_id,
                "status": status,
                "records_received": records_received,
                "records_loaded": records_loaded,
                "error_message": error_message,
            },
        )
    logger.info(f"Ingestion batch {batch_id} tracking closeout successfully saved to disk.")
