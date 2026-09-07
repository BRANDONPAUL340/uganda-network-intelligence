from datetime import datetime
from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize tracking layer logger instance
logger = get_logger(__name__)


def start_stage_run(run_id, stage_name):
    """
    Inserts an initial running audit tracking checkpoint row for an individual 
    pipeline layer processing stage.
    """
    sql = """
    INSERT INTO pipeline_stage_runs (
        run_id,
        stage_name,
        started_at,
        status
    )
    VALUES (
        :run_id,
        :stage_name,
        :started_at,
        'RUNNING'
    )
    RETURNING stage_run_id;
    """
    with engine.begin() as connection:
        result = connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "stage_name": stage_name,
                "started_at": datetime.now(),
            }
        )
        stage_run_id = result.scalar()
        logger.info(f"Stage tracker initialized | stage_run_id={stage_run_id} | stage={stage_name}")
        return stage_run_id


def finish_stage_run(
    stage_run_id,
    status,
    records_read=0,
    records_inserted=0,
    records_rejected=0,
    records_skipped=0,
    error_message=None,
):
    """
    Updates the stage audit tracking record with completion timestamp, granular 
    volumetric parameters, and calculates precise execution duration fields natively.
    """
    completed_at = datetime.now()

    sql = """
    UPDATE pipeline_stage_runs
    SET
        completed_at = :completed_at,
        status = :status,
        records_read = :records_read,
        records_inserted = :records_inserted,
        records_rejected = :records_rejected,
        records_skipped = :records_skipped,
        duration_seconds = EXTRACT(EPOCH FROM (:completed_at - started_at)),
        error_message = :error_message
    WHERE stage_run_id = :stage_run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "stage_run_id": stage_run_id,
                "completed_at": completed_at,
                "status": status,
                "records_read": records_read,
                "records_inserted": records_inserted,
                "records_rejected": records_rejected,
                "records_skipped": records_skipped,
                "error_message": error_message,
            }
        )
    logger.info(f"Stage tracker closed out | stage_run_id={stage_run_id} | status={status}")
