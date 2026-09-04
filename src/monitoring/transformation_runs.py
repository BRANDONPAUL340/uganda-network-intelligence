from datetime import datetime
from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize tracking layer utility logger instance
logger = get_logger(__name__)


def start_transformation(run_id, layer, transformation_name):
    """
    Inserts a micro-tier audit record tracking the lifecycle execution 
    checkpoint for an individual warehouse layer transformation process loop.
    """
    sql = """
    INSERT INTO transformation_runs (
        run_id,
        layer,
        transformation_name,
        started_at,
        status
    )
    VALUES (
        :run_id,
        :layer,
        :transformation_name,
        :started_at,
        'RUNNING'
    )
    RETURNING transformation_run_id;
    """
    with engine.begin() as connection:
        result = connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "layer": layer,
                "transformation_name": transformation_name,
                "started_at": datetime.now(),
            }
        )
        tx_run_id = result.scalar()
        logger.info(
            f"Transformation tracker started | "
            f"transformation_run_id={tx_run_id} | "
            f"layer={layer} | name={transformation_name}"
        )
        return tx_run_id


def finish_transformation(transformation_run_id, status, records_processed=0, error_message=None):
    """
    Updates the micro-tier transformation run record with completion timestamp, 
    volumetric metrics parameters, and explicit exception messages if caught.
    """
    sql = """
    UPDATE transformation_runs
    SET
        completed_at = :completed_at,
        status = :status,
        records_processed = :records_processed,
        error_message = :error_message
    WHERE transformation_run_id = :transformation_run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "transformation_run_id": transformation_run_id,
                "completed_at": datetime.now(),
                "status": status,
                "records_processed": records_processed,
                "error_message": error_message,
            }
        )
    logger.info(
        f"Transformation tracker completed | "
        f"transformation_run_id={transformation_run_id} | "
        f"status={status} | processed={records_processed}"
    )
